terraform {
  required_version = ">= 1.6.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.35"
    }
  }
}

provider "kubernetes" {
  config_path = var.kubeconfig_path
}

resource "kubernetes_namespace" "namespaces" {
  for_each = toset(["app", "database", "vector", "auth", "observability"])

  metadata {
    name = each.value
  }
}
