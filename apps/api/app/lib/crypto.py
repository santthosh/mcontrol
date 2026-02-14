"""AES-256-GCM encryption for credential storage."""

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.lib.config import get_settings

_cached_key: bytes | None = None


def _get_key() -> bytes:
    """Read and cache the base64-decoded 32-byte encryption key from settings."""
    global _cached_key
    if _cached_key is not None:
        return _cached_key

    raw = get_settings().credential_encryption_key
    if not raw:
        raise RuntimeError(
            "CREDENTIAL_ENCRYPTION_KEY is not set. "
            'Generate one with: python -c "import secrets,base64; '
            'print(base64.b64encode(secrets.token_bytes(32)).decode())"'
        )

    key = base64.b64decode(raw)
    if len(key) != 32:
        raise RuntimeError("CREDENTIAL_ENCRYPTION_KEY must be exactly 32 bytes (256 bits)")

    _cached_key = key
    return _cached_key


def encrypt(plaintext: str) -> str:
    """Encrypt a string with AES-256-GCM. Returns base64(nonce + ciphertext + tag)."""
    key = _get_key()
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    # ct already includes the 16-byte GCM tag appended by cryptography
    return base64.b64encode(nonce + ct).decode("ascii")


def decrypt(ciphertext_b64: str) -> str:
    """Decrypt a base64-encoded AES-256-GCM blob. Returns plaintext string."""
    key = _get_key()
    raw = base64.b64decode(ciphertext_b64)
    if len(raw) < 28:  # 12 nonce + 16 tag minimum
        raise ValueError("Ciphertext too short")
    nonce = raw[:12]
    ct = raw[12:]
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ct, None)
    return plaintext.decode("utf-8")


def mask_key(key: str) -> str:
    """Return a masked display hint, e.g. 'sk-...7f3a'.

    Uses prefix up to first '-' (or first 2 chars) + '...' + last 4 chars.
    """
    suffix = key[-4:]
    dash_idx = key.find("-")
    if dash_idx > 0 and dash_idx < len(key) - 4:
        prefix = key[: dash_idx + 1]
    else:
        prefix = key[:2]
    return f"{prefix}...{suffix}"
