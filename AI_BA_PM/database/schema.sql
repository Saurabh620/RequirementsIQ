-- ============================================================
-- RequirementIQ — MySQL Database Schema
-- Version: 1.0 | Engine: InnoDB | Charset: utf8mb4
-- Run: mysql -u root -p < database/schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS requirementiq
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- USE requirementiq;  -- Commented out: database is specified in connection string

-- ============================================================
-- TABLE: users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              CHAR(36)        NOT NULL,
    email           VARCHAR(255)    NOT NULL,
    password_hash   VARCHAR(255)    DEFAULT NULL,
    full_name       VARCHAR(255)    DEFAULT NULL,
    plan            ENUM('free','pro','enterprise') NOT NULL DEFAULT 'free',
    docs_used_this_month INT        NOT NULL DEFAULT 0,
    docs_limit      INT             NOT NULL DEFAULT 3,
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    is_admin        TINYINT(1)      NOT NULL DEFAULT 0,
    last_login_at   DATETIME        DEFAULT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_email (email),
    INDEX idx_users_plan (plan)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: projects
-- ============================================================
CREATE TABLE IF NOT EXISTS projects (
    id          CHAR(36)        NOT NULL,
    user_id     CHAR(36)        NOT NULL,
    name        VARCHAR(255)    NOT NULL,
    description TEXT            DEFAULT NULL,
    domain      VARCHAR(50)     NOT NULL DEFAULT 'generic',
    is_archived TINYINT(1)      NOT NULL DEFAULT 0,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_projects_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_projects_user_id (user_id),
    INDEX idx_projects_domain (domain)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: documents
-- ============================================================
CREATE TABLE IF NOT EXISTS documents (
    id                  CHAR(36)    NOT NULL,
    user_id             CHAR(36)    NOT NULL,
    project_id          CHAR(36)    DEFAULT NULL,
    title               VARCHAR(500) DEFAULT NULL,
    input_type          ENUM('upload_txt','upload_docx','paste') NOT NULL,
    raw_input_text      MEDIUMTEXT  DEFAULT NULL,
    domain              VARCHAR(50) NOT NULL DEFAULT 'generic',
    status              ENUM('pending','processing','completed','failed','partial') NOT NULL DEFAULT 'pending',
    output_types        VARCHAR(100) NOT NULL DEFAULT 'brd,frd,agile',
    completeness_score  TINYINT     DEFAULT NULL,
    generation_time_ms  INT         DEFAULT NULL,
    error_message       TEXT        DEFAULT NULL,
    created_at          DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_documents_user    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    CONSTRAINT fk_documents_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    INDEX idx_documents_user_id   (user_id),
    INDEX idx_documents_status    (status),
    INDEX idx_documents_created   (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: generated_artifacts
-- ============================================================
CREATE TABLE IF NOT EXISTS generated_artifacts (
    id              CHAR(36)    NOT NULL,
    document_id     CHAR(36)    NOT NULL,
    artifact_type   ENUM('brd','frd','agile','use_cases','nfr') NOT NULL,
    content_json    LONGTEXT    NOT NULL,   -- Stored as JSON string
    content_markdown LONGTEXT   DEFAULT NULL,
    confidence_score TINYINT    DEFAULT NULL,
    prompt_version  VARCHAR(20) DEFAULT NULL,
    model_used      VARCHAR(50) DEFAULT NULL,
    tokens_used     INT         DEFAULT NULL,
    is_edited       TINYINT(1)  NOT NULL DEFAULT 0,
    edited_content  LONGTEXT    DEFAULT NULL,
    version         SMALLINT    NOT NULL DEFAULT 1,
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_artifacts_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    INDEX idx_artifacts_document_id (document_id),
    INDEX idx_artifacts_type        (artifact_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: gap_reports
-- ============================================================
CREATE TABLE IF NOT EXISTS gap_reports (
    id              CHAR(36)    NOT NULL,
    document_id     CHAR(36)    NOT NULL,
    gaps_json       LONGTEXT    NOT NULL DEFAULT ('[]'),
    total_gaps      SMALLINT    NOT NULL DEFAULT 0,
    high_count      SMALLINT    NOT NULL DEFAULT 0,
    medium_count    SMALLINT    NOT NULL DEFAULT 0,
    low_count       SMALLINT    NOT NULL DEFAULT 0,
    prompt_version  VARCHAR(20) DEFAULT NULL,
    tokens_used     INT         DEFAULT NULL,
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_gap_reports_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE KEY uq_gap_reports_document (document_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: risk_reports
-- ============================================================
CREATE TABLE IF NOT EXISTS risk_reports (
    id              CHAR(36)    NOT NULL,
    document_id     CHAR(36)    NOT NULL,
    risks_json      LONGTEXT    NOT NULL DEFAULT ('[]'),
    total_risks     SMALLINT    NOT NULL DEFAULT 0,
    critical_count  SMALLINT    NOT NULL DEFAULT 0,
    prompt_version  VARCHAR(20) DEFAULT NULL,
    tokens_used     INT         DEFAULT NULL,
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_risk_reports_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE KEY uq_risk_reports_document (document_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: ai_usage_logs
-- ============================================================
CREATE TABLE IF NOT EXISTS ai_usage_logs (
    id                  CHAR(36)    NOT NULL,
    user_id             CHAR(36)    NOT NULL,
    document_id         CHAR(36)    DEFAULT NULL,
    chain_name          VARCHAR(50) NOT NULL,
    model               VARCHAR(50) NOT NULL,
    prompt_version      VARCHAR(20) DEFAULT NULL,
    input_tokens        INT         NOT NULL DEFAULT 0,
    output_tokens       INT         NOT NULL DEFAULT 0,
    total_tokens        INT         NOT NULL DEFAULT 0,
    estimated_cost_usd  DECIMAL(10,6) DEFAULT NULL,
    latency_ms          INT         DEFAULT NULL,
    status              ENUM('success','error','retry') NOT NULL DEFAULT 'success',
    error_code          VARCHAR(50) DEFAULT NULL,
    created_at          DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_ai_logs_user     FOREIGN KEY (user_id)     REFERENCES users(id)     ON DELETE CASCADE,
    CONSTRAINT fk_ai_logs_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL,
    INDEX idx_ai_logs_user_id    (user_id),
    INDEX idx_ai_logs_document_id (document_id),
    INDEX idx_ai_logs_created    (created_at DESC),
    INDEX idx_ai_logs_chain      (chain_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: industry_templates
-- ============================================================
CREATE TABLE IF NOT EXISTS industry_templates (
    id              CHAR(36)    NOT NULL,
    domain          VARCHAR(50) NOT NULL,
    template_type   VARCHAR(30) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    description     TEXT        DEFAULT NULL,
    system_context  LONGTEXT    NOT NULL,
    is_active       TINYINT(1)  NOT NULL DEFAULT 1,
    is_pro_only     TINYINT(1)  NOT NULL DEFAULT 0,
    created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_templates_domain (domain),
    INDEX idx_templates_type   (template_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SEED DATA: Industry Templates
-- ============================================================
INSERT IGNORE INTO industry_templates (id, domain, template_type, name, description, system_context)
VALUES
(UUID(), 'saas', 'brd', 'SaaS BRD Template',
 'For SaaS products including multi-tenancy, subscriptions, and API considerations',
 'Domain: SaaS. Watch for: multi-tenancy, subscription lifecycle, API rate limiting, SSO/SAML, GDPR data residency, webhook infrastructure.'),
(UUID(), 'bfsi', 'brd', 'BFSI BRD Template',
 'For Banking, Financial Services, Insurance projects',
 'Domain: BFSI. Watch for: RBI/SEBI regulatory compliance, audit trails, PII/KYC/AML, core banking integration, data sovereignty requirements.'),
(UUID(), 'healthcare', 'brd', 'Healthcare BRD Template',
 'For Healthcare IT, EHR, patient data systems',
 'Domain: Healthcare. Watch for: HIPAA compliance, PHI handling, HL7/FHIR integration, patient de-identification, mandatory audit logging, RTO/RPO for disaster recovery.');

COMMIT;
