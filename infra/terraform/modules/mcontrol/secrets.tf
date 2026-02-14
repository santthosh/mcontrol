# Google OAuth secrets in Secret Manager
#
# Terraform creates the secrets with a placeholder value so Cloud Run
# can reference them immediately. Replace with real values:
#   echo -n "REAL_CLIENT_ID" | gcloud secrets versions add google-client-id-ENV --data-file=-
#   echo -n "REAL_SECRET" | gcloud secrets versions add google-client-secret-ENV --data-file=-

resource "google_secret_manager_secret" "google_client_id" {
  project   = var.project_id
  secret_id = "google-client-id-${var.environment}"

  labels = local.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "google_client_id_initial" {
  secret      = google_secret_manager_secret.google_client_id.id
  secret_data = "PLACEHOLDER"

  lifecycle {
    # Don't revert to placeholder when real value is set via gcloud CLI
    ignore_changes = [secret_data]
  }
}

resource "google_secret_manager_secret" "google_client_secret" {
  project   = var.project_id
  secret_id = "google-client-secret-${var.environment}"

  labels = local.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "google_client_secret_initial" {
  secret      = google_secret_manager_secret.google_client_secret.id
  secret_data = "PLACEHOLDER"

  lifecycle {
    # Don't revert to placeholder when real value is set via gcloud CLI
    ignore_changes = [secret_data]
  }
}

# Grant the Cloud Run API service account access to read these secrets
resource "google_secret_manager_secret_iam_member" "api_google_client_id" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.google_client_id.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.api.email}"
}

resource "google_secret_manager_secret_iam_member" "api_google_client_secret" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.google_client_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.api.email}"
}

# Credential encryption key for AES-256-GCM encrypted API key storage
resource "google_secret_manager_secret" "credential_encryption_key" {
  project   = var.project_id
  secret_id = "credential-encryption-key-${var.environment}"

  labels = local.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "credential_encryption_key_initial" {
  secret      = google_secret_manager_secret.credential_encryption_key.id
  secret_data = "PLACEHOLDER"

  lifecycle {
    # Don't revert to placeholder when real value is set via gcloud CLI
    ignore_changes = [secret_data]
  }
}

resource "google_secret_manager_secret_iam_member" "api_credential_encryption_key" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.credential_encryption_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.api.email}"
}
