# Google OAuth secrets in Secret Manager
#
# The secret *values* must be populated manually (or via CI) after terraform apply:
#   echo -n "CLIENT_ID" | gcloud secrets versions add google-client-id-ENV --data-file=-
#   echo -n "CLIENT_SECRET" | gcloud secrets versions add google-client-secret-ENV --data-file=-

resource "google_secret_manager_secret" "google_client_id" {
  project   = var.project_id
  secret_id = "google-client-id-${var.environment}"

  labels = local.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
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
