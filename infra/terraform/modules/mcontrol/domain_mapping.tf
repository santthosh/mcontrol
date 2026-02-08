# Custom domain mapping for Cloud Run API

resource "google_cloud_run_domain_mapping" "api" {
  count = var.api_domain != null ? 1 : 0

  project  = var.project_id
  location = var.region
  name     = var.api_domain

  metadata {
    namespace = var.project_id
    labels    = local.labels
  }

  spec {
    route_name = google_cloud_run_v2_service.api.name
  }

  depends_on = [
    google_cloud_run_v2_service.api,
  ]
}
