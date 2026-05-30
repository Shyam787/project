from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData()
ID_TYPE = String(120)

tenants = Table(
    "tenants",
    metadata,
    Column("id", ID_TYPE, primary_key=True),
    Column("name", String(255), nullable=False),
    Column("slug", String(120), nullable=False, unique=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

users = Table(
    "users",
    metadata,
    Column("id", ID_TYPE, primary_key=True),
    Column("tenant_id", ID_TYPE, ForeignKey("tenants.id"), nullable=False),
    Column("external_subject", String(255), nullable=False),
    Column("email", String(320), nullable=False),
    Column("display_name", String(255), nullable=False),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("tenant_id", "external_subject", name="uq_users_tenant_subject"),
    UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    Index("ix_users_tenant_id", "tenant_id"),
)

roles = Table(
    "roles",
    metadata,
    Column("id", ID_TYPE, primary_key=True),
    Column("tenant_id", ID_TYPE, ForeignKey("tenants.id"), nullable=False),
    Column("name", String(80), nullable=False),
    Column("description", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("tenant_id", "name", name="uq_roles_tenant_name"),
    Index("ix_roles_tenant_id", "tenant_id"),
)

documents = Table(
    "documents",
    metadata,
    Column("id", ID_TYPE, primary_key=True),
    Column("tenant_id", ID_TYPE, ForeignKey("tenants.id"), nullable=False),
    Column("owner_id", ID_TYPE, ForeignKey("users.id"), nullable=False),
    Column("title", String(500), nullable=False),
    Column("document_type", String(80), nullable=False),
    Column("storage_uri", Text, nullable=False),
    Column("ingestion_status", String(40), nullable=False, server_default="pending"),
    Column("pii_sensitive", Boolean, nullable=False, server_default="false"),
    Column("metadata", JSONB, nullable=False, server_default="{}"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint(
        "ingestion_status IN ('pending','processing','completed','failed','archived','soft_deleted')",
        name="ck_documents_ingestion_status",
    ),
    Index("ix_documents_tenant_id", "tenant_id"),
    Index("ix_documents_tenant_status", "tenant_id", "ingestion_status"),
)

document_permissions = Table(
    "document_permissions",
    metadata,
    Column("id", ID_TYPE, primary_key=True),
    Column("tenant_id", ID_TYPE, ForeignKey("tenants.id"), nullable=False),
    Column("document_id", ID_TYPE, ForeignKey("documents.id"), nullable=False),
    Column("role_id", ID_TYPE, ForeignKey("roles.id"), nullable=True),
    Column("user_id", ID_TYPE, ForeignKey("users.id"), nullable=True),
    Column("permission", String(80), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint(
        "(role_id IS NOT NULL) OR (user_id IS NOT NULL)",
        name="ck_document_permissions_principal",
    ),
    UniqueConstraint(
        "tenant_id",
        "document_id",
        "role_id",
        "user_id",
        "permission",
        name="uq_document_permissions_scope",
    ),
    Index("ix_document_permissions_tenant_document", "tenant_id", "document_id"),
)

chunks = Table(
    "chunks",
    metadata,
    Column("id", ID_TYPE, primary_key=True),
    Column("tenant_id", ID_TYPE, ForeignKey("tenants.id"), nullable=False),
    Column("document_id", ID_TYPE, ForeignKey("documents.id"), nullable=False),
    Column("chunk_index", Integer, nullable=False),
    Column("content", Text, nullable=False),
    Column("token_count", Integer, nullable=False),
    Column("metadata", JSONB, nullable=False, server_default="{}"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("tenant_id", "document_id", "chunk_index", name="uq_chunks_order"),
    Index("ix_chunks_tenant_document", "tenant_id", "document_id"),
)

conversations = Table(
    "conversations",
    metadata,
    Column("id", ID_TYPE, primary_key=True),
    Column("tenant_id", ID_TYPE, ForeignKey("tenants.id"), nullable=False),
    Column("user_id", ID_TYPE, ForeignKey("users.id"), nullable=False),
    Column("title", String(255), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Index("ix_conversations_tenant_user", "tenant_id", "user_id"),
)

messages = Table(
    "messages",
    metadata,
    Column("id", ID_TYPE, primary_key=True),
    Column("tenant_id", ID_TYPE, ForeignKey("tenants.id"), nullable=False),
    Column("conversation_id", ID_TYPE, ForeignKey("conversations.id"), nullable=False),
    Column("role", String(40), nullable=False),
    Column("content", Text, nullable=False),
    Column("citation_payload", JSONB, nullable=False, server_default="{}"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("role IN ('user','assistant','system')", name="ck_messages_role"),
    Index("ix_messages_tenant_conversation", "tenant_id", "conversation_id"),
)

feedback = Table(
    "feedback",
    metadata,
    Column("id", ID_TYPE, primary_key=True),
    Column("tenant_id", ID_TYPE, ForeignKey("tenants.id"), nullable=False),
    Column("message_id", ID_TYPE, ForeignKey("messages.id"), nullable=False),
    Column("user_id", ID_TYPE, ForeignKey("users.id"), nullable=False),
    Column("rating", String(20), nullable=False),
    Column("comment", Text, nullable=True),
    Column("retrieval_trace", JSONB, nullable=False, server_default="{}"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("rating IN ('thumbs_up','thumbs_down')", name="ck_feedback_rating"),
    Index("ix_feedback_tenant_message", "tenant_id", "message_id"),
)

audit_logs = Table(
    "audit_logs",
    metadata,
    Column("id", ID_TYPE, primary_key=True),
    Column("tenant_id", ID_TYPE, ForeignKey("tenants.id"), nullable=False),
    Column("user_id", ID_TYPE, ForeignKey("users.id"), nullable=True),
    Column("request_id", String(80), nullable=False),
    Column("event_type", String(120), nullable=False),
    Column("resource_type", String(120), nullable=True),
    Column("resource_id", String(120), nullable=True),
    Column("metadata", JSONB, nullable=False, server_default="{}"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Index("ix_audit_logs_tenant_created", "tenant_id", "created_at"),
    Index("ix_audit_logs_tenant_event", "tenant_id", "event_type"),
)

hallucination_results = Table(
    "hallucination_results",
    metadata,
    Column("id", ID_TYPE, primary_key=True),
    Column("tenant_id", ID_TYPE, ForeignKey("tenants.id"), nullable=False),
    Column("message_id", ID_TYPE, ForeignKey("messages.id"), nullable=False),
    Column("score", Integer, nullable=False),
    Column("confidence", String(40), nullable=False),
    Column("unsupported_claims", JSONB, nullable=False, server_default="[]"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("score >= 0 AND score <= 100", name="ck_hallucination_score"),
    Index("ix_hallucination_results_tenant_message", "tenant_id", "message_id"),
)

CORE_TABLE_NAMES = tuple(table.name for table in metadata.sorted_tables)
