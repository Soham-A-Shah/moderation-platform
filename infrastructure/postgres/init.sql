CREATE TABLE IF NOT EXISTS content_items (
    id UUID PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL,
    original_text TEXT NOT NULL,
    normalized_text TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'SUBMITTED',
    final_decision VARCHAR(32),
    scores JSONB,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS moderation_audit (
    id SERIAL PRIMARY KEY,
    content_id UUID NOT NULL,
    event_type VARCHAR(128) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS moderation_analytics (
    id SERIAL PRIMARY KEY,
    content_id UUID NOT NULL,
    decision VARCHAR(32) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
