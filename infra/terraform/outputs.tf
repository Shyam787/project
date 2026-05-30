output "namespaces" {
  description = "Provisioned Kubernetes namespaces."
  value       = keys(kubernetes_namespace.namespaces)
}
