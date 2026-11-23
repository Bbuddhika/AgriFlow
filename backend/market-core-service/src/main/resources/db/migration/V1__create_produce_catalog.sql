CREATE TABLE produce_types (
    id UUID PRIMARY KEY,
    code VARCHAR(32) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    unit VARCHAR(8) NOT NULL DEFAULT 'kg' CHECK (unit = 'kg'),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT produce_code_format CHECK (code ~ '^[A-Z][A-Z0-9_]*$')
);

-- Initial catalog taxonomy only. No fabricated trade, inventory or price records.
INSERT INTO produce_types (id, code, name) VALUES
('00000000-0000-4000-8000-000000000001', 'POTATO', 'Potato'),
('00000000-0000-4000-8000-000000000002', 'TOMATO', 'Tomato'),
('00000000-0000-4000-8000-000000000003', 'CARROT', 'Carrot'),
('00000000-0000-4000-8000-000000000004', 'CABBAGE', 'Cabbage'),
('00000000-0000-4000-8000-000000000005', 'BEANS', 'Green beans'),
('00000000-0000-4000-8000-000000000006', 'PUMPKIN', 'Pumpkin');
