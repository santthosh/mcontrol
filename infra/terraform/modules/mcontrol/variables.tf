# Required variables
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod"
  }
}

# Optional variables with sensible defaults
variable "api_image" {
  description = "Docker image for the API service (without tag)"
  type        = string
  default     = null # Will be constructed from artifact registry
}

variable "api_cpu" {
  description = "CPU allocation for API service"
  type        = string
  default     = "1"
}

variable "api_memory" {
  description = "Memory allocation for API service"
  type        = string
  default     = "512Mi"
}

variable "api_min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 0
}

variable "api_max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "api_concurrency" {
  description = "Maximum concurrent requests per instance"
  type        = number
  default     = 80
}

variable "firebase_project_id" {
  description = "Firebase project ID (defaults to GCP project ID)"
  type        = string
  default     = null
}

variable "allow_unauthenticated" {
  description = "Allow unauthenticated access to Cloud Run service"
  type        = bool
  default     = true
}

variable "github_repo" {
  description = "GitHub repository in format owner/repo for Workload Identity"
  type        = string
}
