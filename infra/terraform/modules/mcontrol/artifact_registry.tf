# Artifact Registry repository for container images
# Shared across environments (one repo, different tags)
# Only create in first environment (dev), others reference it
resource "google_artifact_registry_repository" "containers" {
  count = var.create_artifact_registry ? 1 : 0

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
  artifact_registry_url = "${var.region}-docker.pkg.dev/${var.project_id}/mcontrol"
  api_image_url         = "${local.artifact_registry_url}/api"
}
