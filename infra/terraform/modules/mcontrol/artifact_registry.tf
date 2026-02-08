# Artifact Registry repository for container images
# Shared across environments (one repo, different tags)
resource "google_artifact_registry_repository" "containers" {
  project       = var.project_id
  location      = var.region
  repository_id = "mcontrol"
  description   = "Mission Control container images"
  format        = "DOCKER"

  labels = local.labels

  # Cleanup policy - keep last 10 versions per tag
  cleanup_policies {
    id     = "keep-recent"
    action = "KEEP"

    most_recent_versions {
      keep_count = 10
    }
  }

  depends_on = [google_project_service.apis]
}

# Output the repository URL for use in CI/CD
locals {
  artifact_registry_url = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.containers.repository_id}"
  api_image_url         = "${local.artifact_registry_url}/api"
}
