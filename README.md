# PharmAlert

Module SIH (Systeme d'Information Hospitalier) de gestion des interactions medicamenteuses, validation d'ordonnances et suivi d'administration.

## Architecture

- **Backend**: FastAPI (Python) avec PostgreSQL et Redis
- **Frontend**: React + Vite + Tailwind CSS
- **Monorepo**: pnpm + Turborepo
- **API FHIR**: MedicationRequest, MedicationAdministration, AllergyIntolerance

## Fonctionnalites

- Verification automatique des interactions medicamenteuses lors de la prescription
- Workflow de validation pharmaceutique
- Suivi d'administration infirmier
- Gestion des allergies patients
- Declaration et suivi des evenements indesirables
- Piste d'audit complete
- Systeme de webhooks pour alertes critiques
- Classification ATC des medicaments

## Roles RBAC

| Role | Permissions |
|------|-------------|
| admin | Administration complete du systeme |
| medecin | Prescription de medicaments |
| pharmacien | Validation des ordonnances |
| infirmier | Administration des doses |
| preparateur | Preparation des medicaments |

## Demarrage rapide

### Prerequis

- Node.js >= 18
- pnpm >= 9
- Python >= 3.11
- Docker et Docker Compose

### Installation

```bash
# Demarrer les services (PostgreSQL, Redis)
docker-compose up -d postgres redis

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 96000 --reload

# Frontend
pnpm install
pnpm dev
```

### Avec Docker

```bash
docker-compose up -d
```

- Frontend: http://localhost:3900
- Backend API: http://localhost:96000
- Documentation API: http://localhost:96000/docs

## Ports

| Service | Port |
|---------|------|
| Frontend (web) | 3900 |
| Backend (API) | 96000 |
| PostgreSQL | 5432 |
| Redis | 6379 |

## Tests

```bash
# Backend
cd backend
pytest

# Frontend
pnpm test
```
