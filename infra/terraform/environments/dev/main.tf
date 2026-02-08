terraform {
  required_version = ">= 1.5"

  # Remote state in GCS - configured after bootstrap
  backend "gcs" {
    bucket = "mcontrol-terraform-state"
    prefix = "environments/dev"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "mcontrol" {
  source = "../../modules/mcontrol"

  project_id  = var.project_id
  region      = var.region
  environment = "dev"
  github_repo = var.github_repo

  # Dev-specific settings
  api_min_instances     = 0  # Scale to zero when idle
  api_max_instances     = 2
  allow_unauthenticated = true
}

# Outputs
output "api_url" {
  value = module.mcontrol.api_url
}

output "artifact_registry_url" {
  value = module.mcontrol.artifact_registry_url
}

output "github_actions_service_account" {
  value = module.mcontrol.github_actions_service_account_email
}

output "workload_identity_provider" {
  value = module.mcontrol.workload_identity_provider
}
