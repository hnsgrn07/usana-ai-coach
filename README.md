# USANA Personal Nutritional Coach — Backend API

A multi-tenant, SaaS-ready backend that recommends USANA supplements,
diet, and routine suggestions based on a member's health profile.

## Tech Stack
- Python + FastAPI + Pydantic
- JSON-based product catalog (interim, pre-database)
- Uvicorn (ASGI server)

## Setup
```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```
Visit `http://127.0.0.1:8000/docs` for interactive API testing.

## Project Phases
| Phase | Description | Status |
|---|---|---|
| 1 | Environment & Foundation | ✅ |
| 2 | Health Profile Model | ✅ |
| 3 | Product Catalog Structure | ✅ |
| 4 | Core Recommendation Engine | ✅ |
| 5 | Dietary Restriction Filtering | ✅ |
| 6 | Catalog Expansion | ✅ |
| 7 | Persistence Layer | ✅ |
| 8 | Auth & Multi-Tenancy (QR enrollment) | ⏳ |
    8a: user accounts✅
    8b: JWT login ✅
    8c: QR enrollment✅
| 9 | Dashboard (Frontend) | ⏳ |
    9a ✅ 
    9b: login/register pages ✅
    9c: dashboard page ✅ 
    9d: QR page ⏳
| 10 | Deployment / SaaS Hardening | ⏳ |
    10a: deploy backend⏳

## Deferred / Backlog
- **Usanimals (pediatric product):** excluded from catalog. HealthProfile requires age ≥ 13, and Usanimals targets children below that. Revisit if child/family profiles are added — would need `min_age`/`max_age` on Product and an age-range check in /recommend.
- **Associate/sponsor roles:** enrollment token generation is currently open to anyone. Once member vs. associate roles exist, restrict /enrollment/generate to associate accounts only.
- **Schema migrations:** currently resetting usana_coach.db manually when models change. Adopt Alembic (or similar) before real user data exists, so schema changes don't require wiping the database.