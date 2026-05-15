-- Migration: Add SIH sync fields and Patient model (Step 1 of 2)
-- This script must be run BEFORE starting the new backend code.

BEGIN;

-- ─── 1. Add entity_id to entities table ───────────────────────────────────────
ALTER TABLE entities ADD COLUMN IF NOT EXISTS sih_config JSONB;
ALTER TABLE entities ADD COLUMN IF NOT EXISTS last_sih_sync TIMESTAMP;

-- ─── 2. Create patients table ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    ipp VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE,
    gender VARCHAR(1) NOT NULL DEFAULT 'M',
    phone VARCHAR(50),
    email VARCHAR(255),
    address TEXT,
    is_hospitalized BOOLEAN DEFAULT FALSE,
    has_insurance BOOLEAN DEFAULT FALSE,
    insurance_number VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    sih_reference VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_patients_entity_id ON patients(entity_id);
CREATE INDEX IF NOT EXISTS ix_patients_ipp ON patients(ipp);
CREATE INDEX IF NOT EXISTS ix_patients_sih_reference ON patients(sih_reference);

-- ─── 3. Add entity_id to medications (nullable first) ───────────────────────
ALTER TABLE medications ADD COLUMN IF NOT EXISTS entity_id INTEGER;
ALTER TABLE medications ADD COLUMN IF NOT EXISTS stock_quantity INTEGER NOT NULL DEFAULT 0;
ALTER TABLE medications ADD COLUMN IF NOT EXISTS is_controlled BOOLEAN DEFAULT FALSE;
ALTER TABLE medications ADD COLUMN IF NOT EXISTS sih_reference VARCHAR(100);
ALTER TABLE medications ADD COLUMN IF NOT EXISTS atc_code_original VARCHAR(50);
ALTER TABLE medications ADD COLUMN IF NOT EXISTS active_principle VARCHAR(255);

-- Set entity_id for existing medications (use first entity)
UPDATE medications SET entity_id = (SELECT id FROM entities ORDER BY id LIMIT 1) WHERE entity_id IS NULL;
ALTER TABLE medications ALTER COLUMN entity_id SET NOT NULL;

-- ─── 4. Add entity_id + sih_reference to prescriptions ─────────────────────────
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS entity_id INTEGER;
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS sih_reference VARCHAR(100);
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS prescribed_by VARCHAR(255);
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS patient_id INTEGER;

UPDATE prescriptions SET entity_id = (SELECT id FROM entities ORDER BY id LIMIT 1) WHERE entity_id IS NULL;
ALTER TABLE prescriptions ALTER COLUMN entity_id SET NOT NULL;

-- ─── 5. Add entity_id to patient_allergies ───────────────────────────────────
ALTER TABLE patient_allergies ADD COLUMN IF NOT EXISTS entity_id INTEGER;
ALTER TABLE patient_allergies ADD COLUMN IF NOT EXISTS sih_reference VARCHAR(100);

UPDATE patient_allergies SET entity_id = (SELECT id FROM entities ORDER BY id LIMIT 1) WHERE entity_id IS NULL;
ALTER TABLE patient_allergies ALTER COLUMN entity_id SET NOT NULL;

COMMIT;
