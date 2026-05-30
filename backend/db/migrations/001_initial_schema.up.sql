CREATE TABLE tenants (
    id VARCHAR(120) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(120) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id VARCHAR(120) PRIMARY KEY,
    tenant_id VARCHAR(120) NOT NULL REFERENCES tenants(id),
    external_subject VARCHAR(255) NOT NULL,
    email VARCHAR(320) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_users_tenant_subject UNIQUE (tenant_id, external_subject),
    CONSTRAINT uq_users_tenant_email UNIQUE (tenant_id, email)
);
CREATE INDEX ix_users_tenant_id ON users (tenant_id);

CREATE TABLE roles (
    id VARCHAR(120) PRIMARY KEY,
    tenant_id VARCHAR(120) NOT NULL REFERENCES tenants(id),
    name VARCHAR(80) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_roles_tenant_name UNIQUE (tenant_id, name)
);
CREATE INDEX ix_roles_tenant_id ON roles (tenant_id);

CREATE TABLE documents (
    id VARCHAR(120) PRIMARY KEY,
    tenant_id VARCHAR(120) NOT NULL REFERENCES tenants(id),
    owner_id VARCHAR(120) NOT NULL REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    document_type VARCHAR(80) NOT NULL,
    storage_uri TEXT NOT NULL,
    ingestion_status VARCHAR(40) NOT NULL DEFAULT 'pending',
    pii_sensitive BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_documents_ingestion_status CHECK (
        ingestion_status IN ('pending','processing','completed','failed','archived','soft_deleted')
    )
);
CREATE INDEX ix_documents_tenant_id ON documents (tenant_id);
CREATE INDEX ix_documents_tenant_status ON documents (tenant_id, ingestion_status);

CREATE TABLE document_permissions (
    id VARCHAR(120) PRIMARY KEY,
    tenant_id VARCHAR(120) NOT NULL REFERENCES tenants(id),
    document_id VARCHAR(120) NOT NULL REFERENCES documents(id),
    role_id VARCHAR(120) REFERENCES roles(id),
    user_id VARCHAR(120) REFERENCES users(id),
    permission VARCHAR(80) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_document_permissions_principal CHECK (
        (role_id IS NOT NULL) OR (user_id IS NOT NULL)
    ),
    CONSTRAINT uq_document_permissions_scope UNIQUE (
        tenant_id, document_id, role_id, user_id, permission
    )
);
CREATE INDEX ix_document_permissions_tenant_document ON document_permissions (tenant_id, document_id);

CREATE TABLE chunks (
    id VARCHAR(120) PRIMARY KEY,
    tenant_id VARCHAR(120) NOT NULL REFERENCES tenants(id),
    document_id VARCHAR(120) NOT NULL REFERENCES documents(id),
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_chunks_order UNIQUE (tenant_id, document_id, chunk_index)
);
CREATE INDEX ix_chunks_tenant_document ON chunks (tenant_id, document_id);

CREATE TABLE conversations (
    id VARCHAR(120) PRIMARY KEY,
    tenant_id VARCHAR(120) NOT NULL REFERENCES tenants(id),
    user_id VARCHAR(120) NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_conversations_tenant_user ON conversations (tenant_id, user_id);

CREATE TABLE messages (
    id VARCHAR(120) PRIMARY KEY,
    tenant_id VARCHAR(120) NOT NULL REFERENCES tenants(id),
    conversation_id VARCHAR(120) NOT NULL REFERENCES conversations(id),
    role VARCHAR(40) NOT NULL,
    content TEXT NOT NULL,
    citation_payload JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_messages_role CHECK (role IN ('user','assistant','system'))
);
CREATE INDEX ix_messages_tenant_conversation ON messages (tenant_id, conversation_id);

CREATE TABLE feedback (
    id VARCHAR(120) PRIMARY KEY,
    tenant_id VARCHAR(120) NOT NULL REFERENCES tenants(id),
    message_id VARCHAR(120) NOT NULL REFERENCES messages(id),
    user_id VARCHAR(120) NOT NULL REFERENCES users(id),
    rating VARCHAR(20) NOT NULL,
    comment TEXT,
    retrieval_trace JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_feedback_rating CHECK (rating IN ('thumbs_up','thumbs_down'))
);
CREATE INDEX ix_feedback_tenant_message ON feedback (tenant_id, message_id);

CREATE TABLE audit_logs (
    id VARCHAR(120) PRIMARY KEY,
    tenant_id VARCHAR(120) NOT NULL REFERENCES tenants(id),
    user_id VARCHAR(120) REFERENCES users(id),
    request_id VARCHAR(80) NOT NULL,
    event_type VARCHAR(120) NOT NULL,
    resource_type VARCHAR(120),
    resource_id VARCHAR(120),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_audit_logs_tenant_created ON audit_logs (tenant_id, created_at);
CREATE INDEX ix_audit_logs_tenant_event ON audit_logs (tenant_id, event_type);

CREATE TABLE hallucination_results (
    id VARCHAR(120) PRIMARY KEY,
    tenant_id VARCHAR(120) NOT NULL REFERENCES tenants(id),
    message_id VARCHAR(120) NOT NULL REFERENCES messages(id),
    score INTEGER NOT NULL,
    confidence VARCHAR(40) NOT NULL,
    unsupported_claims JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_hallucination_score CHECK (score >= 0 AND score <= 100)
);
CREATE INDEX ix_hallucination_results_tenant_message ON hallucination_results (tenant_id, message_id);
