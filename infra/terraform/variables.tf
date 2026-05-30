variable "kubeconfig_path" {
  description = "Path to the kubeconfig used for environment provisioning."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "staging"
}
