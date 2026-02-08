# API Service outputs
output "api_url" {
  description = "URL of the Cloud Run API service"
  value       = google_cloud_run_v2_service.api.uri
}

output "api_service_name" {
  description = "Name of the Cloud Run API service"
  value       = google_cloud_run_v2_service.api.name
}

# Artifact Registry outputs
output "artifact_registry_url" {
  description = "Artifact Registry repository URL"
  value       = local.artifact_registry_url
}

output "api_image_url" {
  description = "Full image URL for the API (without tag)"
  value       = local.api_image_url
}

# Service Account outputs
output "api_service_account_email" {
  description = "Email of the API service account"
  value       = google_service_account.api.email
}

output "github_actions_service_account_email" {
  description = "Email of the GitHub Actions service account"
  value       = google_service_account.github_actions.email
}

# Workload Identity outputs
output "workload_identity_provider" {
  description = "Workload Identity Provider resource name for GitHub Actions"
  value       = "projects/${data.google_project.current.number}/locations/global/workloadIdentityPools/github/providers/github-actions"
}
