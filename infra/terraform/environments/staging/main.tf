terraform {
  required_version = ">= 1.5"

  backend "gcs" {
    bucket = "mcontrol-terraform-state"
    prefix = "environments/staging"
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
  environment = "staging"
  github_repo = var.github_repo

  # Staging-specific settings
  api_min_instances        = 0
  api_max_instances        = 5
  allow_unauthenticated    = true
  create_artifact_registry = false  # Created by dev environment
}

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
