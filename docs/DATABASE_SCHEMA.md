# ДарАгент MVP — Backend Specification v0.2

## Часть A — Database Schema (PostgreSQL)

### 1. users
```sql
CREATE TYPE auth_provider_enum AS ENUM ('email', 'phone', 'google', 'yandex', 'apple');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NULL,
    phone VARCHAR(20) NULL,
    name VARCHAR(255) NULL,
    avatar_url TEXT NULL,
    auth_provider auth_provider_enum NOT NULL,
    auth_provider_id VARCHAR(255) NOT NULL,
    balance INTEGER NOT NULL DEFAULT 0,
    bonus_balance INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT users_auth_unique UNIQUE (auth_provider, auth_provider_id),
    CONSTRAINT users_email_check CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_phone_check CHECK (phone IS NULL OR phone ~ '^\+?[0-9]{10,15}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_auth ON users(auth_provider, auth_provider_id);
```

### 2. recipients
```sql
CREATE TABLE recipients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(20) NULL CHECK (gender IN ('male', 'female', 'other')),
    age INTEGER NULL CHECK (age >= 0 AND age <= 120),
    relationship VARCHAR(100) NULL,
    interests JSONB NOT NULL DEFAULT '[]',
    personality JSONB NOT NULL DEFAULT '[]',
    additional_info TEXT NULL,
    photo_asset_id UUID NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_recipients_user ON recipients(user_id);
CREATE INDEX idx_recipients_relationship ON recipients(relationship);
CREATE INDEX idx_recipients_interests ON recipients USING GIN (interests);
```

### 3. projects
```sql
CREATE TYPE project_status_enum AS ENUM (
    'draft',
    'brief_ready',
    'recommendations_ready',
    'template_selected',
    'script_generating',
    'script_ready',
    'assets_generating',
    'rendering',
    'preview_ready',
    'payment_pending',
    'paid',
    'finalizing',
    'completed',
    'failed',
    'cancelled'
);

CREATE TYPE occasion_enum AS ENUM (
    'birthday',
    'wedding',
    'anniversary',
    'new_year',
    'march_8',
    'february_23',
    'graduation',
    'promotion',
    'retirement',
    'baby_shower',
    'christening',
    'housewarming',
    'professional_holiday',
    'other'
);

CREATE TYPE format_enum AS ENUM (
    'short_15s',
    'medium_30s',
    'long_60s',
    'extended_90s'
);

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_id UUID NOT NULL REFERENCES recipients(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    status project_status_enum NOT NULL DEFAULT 'draft',
    occasion occasion_enum NOT NULL,
    format format_enum NOT NULL,
    creative_brief JSONB NOT NULL DEFAULT '{}',
    selected_template_id UUID NULL,
    selected_template_version_id UUID NULL,
    price INTEGER NOT NULL DEFAULT 0,
    currency VARCHAR(3) NOT NULL DEFAULT 'RUB',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE INDEX idx_projects_user ON projects(user_id);
CREATE INDEX idx_projects_recipient ON projects(recipient_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_occasion ON projects(occasion);
CREATE INDEX idx_projects_created ON projects(created_at DESC);
```

### 4. templates
```sql
CREATE TYPE template_category_enum AS ENUM (
    'cinematic',
    'humor',
    'romantic',
    'family',
    'corporate',
    'special'
);

CREATE TYPE price_tier_enum AS ENUM (
    'basic',
    'standard',
    'premium',
    'exclusive'
);

CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    category template_category_enum NOT NULL,
    price_tier price_tier_enum NOT NULL DEFAULT 'standard',
    base_price INTEGER NOT NULL,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    popularity_score INTEGER NOT NULL DEFAULT 0,
    conversion_rate DECIMAL(5,4) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_templates_category ON templates(category);
CREATE INDEX idx_templates_published ON templates(is_published) WHERE is_published = TRUE;
CREATE INDEX idx_templates_popularity ON templates(popularity_score DESC);
```

### 5. template_versions
```sql
CREATE TABLE template_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    requirements JSONB NOT NULL DEFAULT '{}',
    variables JSONB NOT NULL DEFAULT '[]',
    scenes JSONB NOT NULL DEFAULT '[]',
    conditions JSONB NOT NULL DEFAULT '[]',
    prompts JSONB NOT NULL DEFAULT '{}',
    audio_settings JSONB NOT NULL DEFAULT '{}',
    render_settings JSONB NOT NULL DEFAULT '{}',
    fallback_scene_id VARCHAR(100) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_template_version UNIQUE (template_id, version)
);

CREATE INDEX idx_template_versions_template ON template_versions(template_id);
CREATE INDEX idx_template_versions_active ON template_versions(template_id, is_active) WHERE is_active = TRUE;
```

### 6. scenes
```sql
CREATE TYPE scene_type_enum AS ENUM (
    'intro',
    'hero',
    'story',
    'climax',
    'resolution',
    'outro',
    'transition'
);

CREATE TABLE scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_version_id UUID NOT NULL REFERENCES template_versions(id) ON DELETE CASCADE,
    scene_id VARCHAR(100) NOT NULL,
    scene_order INTEGER NOT NULL,
    scene_type scene_type_enum NOT NULL,
    duration INTEGER NOT NULL,
    prompt_template TEXT NOT NULL,
    voice_text_template TEXT NULL,
    voice_settings JSONB DEFAULT '{}',
    visual_style JSONB DEFAULT '{}',
    music_cue JSONB DEFAULT '{}',
    condition_json JSONB NULL,
    variables_required JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scenes_template_version ON scenes(template_version_id);
CREATE INDEX idx_scenes_order ON scenes(template_version_id, scene_order);
```

### 7. generations
```sql
CREATE TYPE generation_status_enum AS ENUM (
    'created',
    'queued',
    'preparing',
    'generating_script',
    'generating_assets',
    'generating_video',
    'rendering',
    'uploading',
    'ready',
    'failed'
);

CREATE TABLE generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    status generation_status_enum NOT NULL DEFAULT 'created',
    retry_count INTEGER NOT NULL DEFAULT 0,
    error_code VARCHAR(50) NULL,
    error_message TEXT NULL,
    script_content TEXT NULL,
    assets_json JSONB DEFAULT '[]',
    video_url TEXT NULL,
    preview_url TEXT NULL,
    started_at TIMESTAMP WITH TIME ZONE NULL,
    completed_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_generations_project ON generations(project_id);
CREATE INDEX idx_generations_status ON generations(status);
CREATE INDEX idx_generations_created ON generations(created_at DESC);
```

### 8. generation_steps
```sql
CREATE TABLE generation_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generation_id UUID NOT NULL REFERENCES generations(id) ON DELETE CASCADE,
    step_type VARCHAR(50) NOT NULL,
    step_order INTEGER NOT NULL,
    status generation_status_enum NOT NULL DEFAULT 'created',
    input_data JSONB NOT NULL DEFAULT '{}',
    output_data JSONB NULL,
    error_message TEXT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE NULL,
    completed_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_generation_steps_generation ON generation_steps(generation_id);
CREATE INDEX idx_generation_steps_status ON generation_steps(status);
```

### 9. assets
```sql
CREATE TYPE asset_type_enum AS ENUM (
    'image',
    'video',
    'audio',
    'document'
);

CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL REFERENCES users(id) ON DELETE SET NULL,
    project_id UUID NULL REFERENCES projects(id) ON DELETE SET NULL,
    asset_type asset_type_enum NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    public_url TEXT NULL,
    file_size INTEGER NULL,
    mime_type VARCHAR(100) NULL,
    width INTEGER NULL,
    height INTEGER NULL,
    duration_seconds INTEGER NULL,
    is_temp BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assets_user ON assets(user_id);
CREATE INDEX idx_assets_project ON assets(project_id);
CREATE INDEX idx_assets_type ON assets(asset_type);
CREATE INDEX idx_assets_temp ON assets(is_temp, expires_at) WHERE is_temp = TRUE;
```

### 10. payments
```sql
CREATE TYPE payment_status_enum AS ENUM (
    'pending',
    'succeeded',
    'failed',
    'refunded',
    'cancelled'
);

CREATE TYPE payment_method_enum AS ENUM (
    'yookassa',
    'wallet',
    'bonus'
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID NULL REFERENCES projects(id) ON DELETE SET NULL,
    amount INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'RUB',
    status payment_status_enum NOT NULL DEFAULT 'pending',
    payment_method payment_method_enum NOT NULL,
    provider_payment_id VARCHAR(255) NULL,
    provider_response JSONB NULL,
    description VARCHAR(500) NULL,
    metadata JSONB DEFAULT '{}',
    paid_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_payments_project ON payments(project_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_provider ON payments(provider_payment_id);
CREATE INDEX idx_payments_created ON payments(created_at DESC);
```

### 11. wallet_transactions
```sql
CREATE TYPE transaction_type_enum AS ENUM (
    'deposit',
    'withdrawal',
    'generation',
    'refund',
    'bonus_grant',
    'bonus_usage',
    'adjustment'
);

CREATE TABLE wallet_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_type transaction_type_enum NOT NULL,
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    bonus_amount INTEGER DEFAULT 0,
    bonus_balance_after INTEGER DEFAULT 0,
    related_entity_type VARCHAR(50) NULL,
    related_entity_id UUID NULL,
    payment_id UUID NULL REFERENCES payments(id) ON DELETE SET NULL,
    description VARCHAR(500) NULL,
    metadata JSONB DEFAULT '{}',
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_wallet_transactions_user ON wallet_transactions(user_id);
CREATE INDEX idx_wallet_transactions_type ON wallet_transactions(transaction_type);
CREATE INDEX idx_wallet_transactions_entity ON wallet_transactions(related_entity_type, related_entity_id);
CREATE INDEX idx_wallet_transactions_payment ON wallet_transactions(payment_id);
CREATE INDEX idx_wallet_transactions_created ON wallet_transactions(created_at DESC);
```

### 12. bonuses
```sql
CREATE TYPE bonus_type_enum AS ENUM (
    'registration',
    'referral',
    'first_payment',
    'promotional',
    'compensation'
);

CREATE TABLE bonuses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bonus_type bonus_type_enum NOT NULL,
    amount INTEGER NOT NULL,
    remaining_amount INTEGER NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    granted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    used_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE INDEX idx_bonuses_user ON bonuses(user_id);
CREATE INDEX idx_bonuses_active ON bonuses(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_bonuses_expires ON bonuses(expires_at) WHERE expires_at IS NOT NULL;
```

### 13. analytics_events
```sql
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_name VARCHAR(100) NOT NULL,
    user_id UUID NULL REFERENCES users(id) ON DELETE SET NULL,
    project_id UUID NULL REFERENCES projects(id) ON DELETE SET NULL,
    properties JSONB NOT NULL DEFAULT '{}',
    session_id VARCHAR(255) NULL,
    device_info JSONB NULL,
    ip_address INET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_analytics_events_name ON analytics_events(event_name);
CREATE INDEX idx_analytics_events_user ON analytics_events(user_id);
CREATE INDEX idx_analytics_events_project ON analytics_events(project_id);
CREATE INDEX idx_analytics_events_created ON analytics_events(created_at DESC);
CREATE INDEX idx_analytics_events_session ON analytics_events(session_id);
```

### 14. refresh_tokens
```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    device_info JSONB NULL,
    ip_address INET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_revoked ON refresh_tokens(revoked) WHERE revoked = FALSE;
```

### 15. admin_users
```sql
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    permissions JSONB NOT NULL DEFAULT '[]',
    last_login_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_admin_users_role ON admin_users(role);
```

### 16. audit_logs
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NULL,
    old_values JSONB NULL,
    new_values JSONB NULL,
    ip_address INET NULL,
    user_agent TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
```

### 17. webhooks
```sql
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    signature VARCHAR(500) NULL,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE NULL,
    response_status INTEGER NULL,
    response_body TEXT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webhooks_provider ON webhooks(provider);
CREATE INDEX idx_webhooks_processed ON webhooks(processed) WHERE processed = FALSE;
CREATE INDEX idx_webhooks_created ON webhooks(created_at DESC);
```

## Индексы производительности

```sql
-- Composite indexes for common queries
CREATE INDEX idx_projects_user_status ON projects(user_id, status);
CREATE INDEX idx_projects_user_created ON projects(user_id, created_at DESC);
CREATE INDEX idx_generations_project_status ON generations(project_id, status);
CREATE INDEX idx_payments_user_status_created ON payments(user_id, status, created_at DESC);
CREATE INDEX idx_wallet_transactions_user_created ON wallet_transactions(user_id, created_at DESC);

-- Partial indexes for active records
CREATE INDEX idx_users_active ON users(id) WHERE is_active = TRUE;
CREATE INDEX idx_templates_published_active ON templates(id) WHERE is_published = TRUE;

-- GIN indexes for JSONB
CREATE INDEX idx_creative_brief_gin ON projects USING GIN (creative_brief);
CREATE INDEX idx_requirements_gin ON template_versions USING GIN (requirements);
```

## Триггеры

```sql
-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recipients_updated_at BEFORE UPDATE ON recipients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```
