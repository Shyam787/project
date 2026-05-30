from pathlib import Path

import yaml


def _load_all_yaml(path: Path) -> list[dict]:
    return [doc for doc in yaml.safe_load_all(path.read_text()) if doc]


def test_kubernetes_manifests_define_required_namespaces_and_services():
    root = Path(__file__).resolve().parents[2]
    namespaces = _load_all_yaml(root / "infra/kubernetes/namespaces.yaml")
    namespace_names = {doc["metadata"]["name"] for doc in namespaces}

    assert namespace_names == {"app", "database", "vector", "auth", "observability"}

    manifest_paths = list((root / "infra/kubernetes").rglob("*.yaml"))
    docs = [doc for path in manifest_paths for doc in _load_all_yaml(path)]
    services = {
        doc["metadata"]["name"]: doc
        for doc in docs
        if doc.get("kind") == "Service"
    }

    assert services["enterprise-rag-postgres"]["spec"]["type"] == "ClusterIP"
    assert services["enterprise-rag-qdrant"]["spec"]["type"] == "ClusterIP"
    assert services["enterprise-rag-redis"]["spec"]["type"] == "ClusterIP"


def test_network_policies_protect_database_and_vector_namespaces():
    root = Path(__file__).resolve().parents[2]
    policies = _load_all_yaml(root / "infra/kubernetes/network-policies.yaml")
    names = {policy["metadata"]["name"] for policy in policies}

    assert "default-deny" in names
    assert "allow-backend-to-postgres-redis" in names
    assert "allow-backend-to-qdrant" in names


def test_terraform_scaffold_is_present():
    root = Path(__file__).resolve().parents[2]

    assert (root / "infra/terraform/main.tf").exists()
    assert (root / "infra/terraform/variables.tf").exists()
    assert (root / "infra/terraform/outputs.tf").exists()
