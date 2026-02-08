# Cloud Run service for the API
resource "google_cloud_run_v2_service" "api" {
  project  = var.project_id
  name     = local.service_name
  location = var.region

  labels = local.labels

  template {
    service_account = google_service_account.api.email

    scaling {
      min_instance_count = var.api_min_instances
      max_instance_count = var.api_max_instances
    }

    containers {
      # Use provided image, or placeholder for initial deployment
      # CI/CD will update this with the real image after first push
      image = coalesce(var.api_image, "us-docker.pkg.dev/cloudrun/container/hello")

      resources {
        limits = {
          cpu    = var.api_cpu
          memory = var.api_memory
        }
      }

      # Environment variables
      env {
        name  = "FIREBASE_PROJECT_ID"
        value = local.firebase_project_id
      }

      env {
        name  = "AUTH_DISABLED"
        value = var.environment == "dev" ? "true" : "false"
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      # Health check endpoint
      startup_probe {
        http_get {
          path = "/api/health"
        }
        initial_delay_seconds = 5
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/api/health"
        }
        period_seconds = 30
      }
    }

    max_instance_request_concurrency = var.api_concurrency
  }

  # Traffic configuration - route all traffic to latest revision
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.apis,
  ]

  lifecycle {
    # Ignore changes to image tag - this is managed by CI/CD
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
}

# Allow unauthenticated access (public API)
resource "google_cloud_run_v2_service_iam_member" "public" {
  count = var.allow_unauthenticated ? 1 : 0

  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
