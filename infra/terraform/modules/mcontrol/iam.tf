# Service account for the Cloud Run API service
resource "google_service_account" "api" {
  project      = var.project_id
  account_id   = "mcontrol-api-${var.environment}"
  display_name = "Mission Control API (${var.environment})"
  description  = "Service account for mcontrol API Cloud Run service"
}

# Grant the API service account access to Firestore
resource "google_project_iam_member" "api_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.api.email}"
}

# Service account for GitHub Actions deployments
resource "google_service_account" "github_actions" {
  project      = var.project_id
  account_id   = "github-actions-${var.environment}"
  display_name = "GitHub Actions (${var.environment})"
  description  = "Service account for GitHub Actions CI/CD"
}

# GitHub Actions needs these roles for deployment
locals {
  github_actions_roles = [
    "roles/run.admin",              # Deploy to Cloud Run
    "roles/artifactregistry.writer", # Push images
    "roles/iam.serviceAccountUser",  # Act as service accounts
  ]
}

resource "google_project_iam_member" "github_actions" {
  for_each = toset(local.github_actions_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

# Workload Identity Federation - Allow GitHub Actions to impersonate the service account
# Note: The Workload Identity Pool is created in bootstrap (shared across environments)
data "google_project" "current" {
  project_id = var.project_id
}

resource "google_service_account_iam_member" "github_actions_workload_identity" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/projects/${data.google_project.current.number}/locations/global/workloadIdentityPools/github/attribute.repository/${var.github_repo}"
}
