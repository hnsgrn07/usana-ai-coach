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
| 5 | Dietary Restriction Filtering | ⏳ |
| 6 | Catalog Expansion | ⏳ |
| 7 | Persistence Layer | ⏳ |
| 8 | Auth & Multi-Tenancy (QR enrollment) | ⏳ |
| 9 | Dashboard (Frontend) | ⏳ |
| 10 | Deployment / SaaS Hardening | ⏳ |