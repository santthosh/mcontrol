"""Tests for credential (API key) encryption and CRUD endpoints."""

import base64
import os
import secrets
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Generate a test encryption key before importing the app
_TEST_KEY = base64.b64encode(secrets.token_bytes(32)).decode()
os.environ["CREDENTIAL_ENCRYPTION_KEY"] = _TEST_KEY


@pytest.fixture(autouse=True)
def _reset_crypto_cache() -> Generator[None]:
    """Reset the cached encryption key between tests."""
    import app.lib.crypto as crypto_mod

    crypto_mod._cached_key = None
    yield
    crypto_mod._cached_key = None


# ---------------------------------------------------------------------------
# Unit tests — encryption module
# ---------------------------------------------------------------------------


class TestEncryptDecrypt:
    """Unit tests for the crypto module (no Firestore required)."""

    def test_encrypt_decrypt_roundtrip(self) -> None:
        from app.lib.crypto import decrypt, encrypt

        keys = [
            "sk-abc123def456ghij",
            "AIzaSyA1234567890abcdefg",
            "a" * 100,
            "special-chars!@#$%^&*()",
        ]
        for key in keys:
            assert decrypt(encrypt(key)) == key

    def test_encrypt_produces_unique_ciphertext(self) -> None:
        from app.lib.crypto import encrypt

        plaintext = "sk-test-key-12345678"
        ct1 = encrypt(plaintext)
        ct2 = encrypt(plaintext)
        assert ct1 != ct2, "Two encryptions of the same plaintext should produce different blobs"

    def test_mask_key_with_dash_prefix(self) -> None:
        from app.lib.crypto import mask_key

        result = mask_key("sk-abc123def456")
        assert result == "sk-...f456"

    def test_mask_key_without_dash(self) -> None:
        from app.lib.crypto import mask_key

        result = mask_key("AIzaSyA1234567890")
        assert result == "AI...7890"

    def test_mask_key_multi_dash(self) -> None:
        from app.lib.crypto import mask_key

        result = mask_key("sk-proj-abc123def456")
        assert result == "sk-...f456"

    def test_decrypt_wrong_key_fails(self) -> None:
        from app.lib.config import get_settings
        from app.lib.crypto import encrypt

        ciphertext = encrypt("sk-test-key-12345678")

        # Switch to a different key
        import app.lib.crypto as crypto_mod

        other_key = base64.b64encode(secrets.token_bytes(32)).decode()
        os.environ["CREDENTIAL_ENCRYPTION_KEY"] = other_key
        crypto_mod._cached_key = None
        get_settings.cache_clear()

        from app.lib.crypto import decrypt

        with pytest.raises(Exception):
            decrypt(ciphertext)

        # Restore original key
        os.environ["CREDENTIAL_ENCRYPTION_KEY"] = _TEST_KEY
        crypto_mod._cached_key = None
        get_settings.cache_clear()

    def test_decrypt_corrupted_blob_fails(self) -> None:
        from app.lib.crypto import decrypt, encrypt

        ct = encrypt("sk-test-key-12345678")
        raw = bytearray(base64.b64decode(ct))
        raw[-1] ^= 0xFF  # flip a byte
        corrupted = base64.b64encode(bytes(raw)).decode()

        with pytest.raises(Exception):
            decrypt(corrupted)


# ---------------------------------------------------------------------------
# Integration tests — CRUD endpoints
# ---------------------------------------------------------------------------


class TestKeysEndpoints:
    """Integration tests for the /api/keys endpoints."""

    def test_create_key(self, client: TestClient) -> None:
        resp = client.post(
            "/api/keys",
            json={"provider": "anthropic", "name": "My Claude Key", "key": "sk-ant-12345678"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["provider"] == "anthropic"
        assert data["name"] == "My Claude Key"
        assert data["key_hint"] == "sk-...5678"
        assert "id" in data
        assert "created_at" in data
        # Ensure the plaintext key is NOT in the response
        assert "sk-ant-12345678" not in resp.text

    def test_list_keys_masked(self, client: TestClient) -> None:
        # Create two keys
        client.post(
            "/api/keys",
            json={"provider": "anthropic", "name": "Key A", "key": "sk-ant-aaaabbbb"},
        )
        client.post(
            "/api/keys",
            json={"provider": "openai", "name": "Key B", "key": "sk-openai-ccccdddd"},
        )

        resp = client.get("/api/keys")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        for item in data:
            assert "key_hint" in item
            # No plaintext key field
            assert "key" not in item
            assert "encrypted_key" not in item

    def test_get_key_masked(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/keys",
            json={"provider": "google", "name": "GCP Key", "key": "AIzaSyA1234567890abcdefg"},
        )
        key_id = create_resp.json()["id"]

        resp = client.get(f"/api/keys/{key_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == key_id
        assert data["provider"] == "google"
        assert data["key_hint"] == "AI...defg"

    def test_update_key_name(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/keys",
            json={"provider": "openai", "name": "Old Name", "key": "sk-openai-12345678"},
        )
        key_id = create_resp.json()["id"]

        resp = client.put(f"/api/keys/{key_id}", json={"name": "New Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"

    def test_update_key_reencrypt(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/keys",
            json={"provider": "anthropic", "name": "Reencrypt", "key": "sk-ant-oldkey99"},
        )
        key_id = create_resp.json()["id"]
        old_hint = create_resp.json()["key_hint"]

        resp = client.put(
            f"/api/keys/{key_id}",
            json={"key": "sk-ant-newkey11"},
        )
        assert resp.status_code == 200
        new_hint = resp.json()["key_hint"]
        assert new_hint != old_hint
        assert new_hint == "sk-...ey11"

    def test_delete_key(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/keys",
            json={"provider": "anthropic", "name": "Delete Me", "key": "sk-ant-deleteme"},
        )
        key_id = create_resp.json()["id"]

        resp = client.delete(f"/api/keys/{key_id}")
        assert resp.status_code == 204

        resp = client.get(f"/api/keys/{key_id}")
        assert resp.status_code == 404

    def test_create_key_empty_rejected(self, client: TestClient) -> None:
        resp = client.post(
            "/api/keys",
            json={"provider": "anthropic", "name": "Bad Key", "key": ""},
        )
        assert resp.status_code == 422

    def test_create_key_too_short_rejected(self, client: TestClient) -> None:
        resp = client.post(
            "/api/keys",
            json={"provider": "anthropic", "name": "Short", "key": "abc"},
        )
        assert resp.status_code == 422

    def test_get_nonexistent_key_404(self, client: TestClient) -> None:
        resp = client.get("/api/keys/nonexistent-id")
        assert resp.status_code == 404

    def test_delete_nonexistent_key_404(self, client: TestClient) -> None:
        resp = client.delete("/api/keys/nonexistent-id")
        assert resp.status_code == 404
