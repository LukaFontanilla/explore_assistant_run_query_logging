variable "cloud_run_service_name" {
  type = string
}

variable "deployment_region" {
  type = string
}

variable "project_id" {
  type = string
}

variable "model_name" {
  type = string
}

resource "google_service_account" "explore-assistant-sa" {
  account_id   = "explore-assistant-cr-sa"
  display_name = "Looker Explore Assistant Cloud Run SA"
}

resource "google_project_iam_member" "iam_permission_looker_aiplatform" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = format("serviceAccount:%s", google_service_account.explore-assistant-sa.email)
}

resource "google_artifact_registry_repository" "default" {
  repository_id = "explore-assistant-repo"
  location      = var.deployment_region
  project       = var.project_id
  format        = "DOCKER"
}

resource "google_cloud_run_v2_service" "default" {
  name     = var.cloud_run_service_name
  location = var.deployment_region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    service_account = google_service_account.explore-assistant-sa.email
    containers {
      image = "${var.deployment_region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.default.repository_id}/${var.cloud_run_service_name}:latest"
      ports {
        container_port = 8080
      }
      env {
        name  = "PROJECT"
        value = var.project_id
      }
      env {
        name  = "REGION"
        value = var.deployment_region
      }
      env {
        name = "MODEL_NAME"
        value = var.model_name
      }
    }
  }
}

output "service_uri" {
  value = google_cloud_run_v2_service.default.uri
}
