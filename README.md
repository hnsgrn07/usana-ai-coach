# USANA Personal Nutritional Coach — Backend API

A multi-tenant, SaaS-ready backend that recommends USANA supplements,
diet, and routine suggestions based on a member's health profile.

## Tech Stack
- Python + FastAPI + Pydantic
- SQLAlchemy + Neon Postgres (production database)
- Gemini API (AI coaching layer)
- Uvicorn (ASGI server)
- React + Vite (frontend, separate repo: usana-dashboard)
- Deployed: Render (backend) + Vercel (frontend)

## Setup
```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```
Visit `http://127.0.0.1:8000/docs` for interactive API testing.

## Live URLs
- Backend: https://usana-ai-coach.onrender.com
- Frontend: https://usana-dashboard.vercel.app

## Project Phases
| Phase | Description | Status |
|---|---|---|
| 1 | Environment & Foundation | ✅ |
| 2 | Health Profile Model | ✅ |
| 3 | Product Catalog Structure | ✅ |
| 4 | Core Recommendation Engine | ✅ |
| 5 | Dietary Restriction Filtering | ✅ |
| 6 | Catalog Expansion (official USANA data) | ✅ |
| 7 | Persistence Layer | ✅ |
| 8a | Auth: user accounts + hashed passwords | ✅ |
| 8b | Auth: JWT login + ownership checks | ✅ |
| 8c | Auth: QR-based enrollment tokens | ✅ |
| 9a | React scaffold + CORS | ✅ |
| 9b | Login & Registration pages | ✅ |
| 9c | Dashboard (profile + recommendations) | ✅ |
| 9d | Enrollment QR page | ✅ |
| 10a | Neon Postgres persistence | ✅ |
| 10b | Backend deployed (Render) | ✅ |
| 10c | Frontend deployed (Vercel), connected end-to-end | ✅ |
| 11a–11d | Visual/branding polish (USANA-accurate colors, typography) | ✅ |
| 12a | AI Coaching Layer (Gemini, goal-based, cached on profile save) | ✅ |
| 12b | AI coaching note displayed on dashboard | ✅ |
| 13 | Daily habit/adherence tracking + streaks | ⏳ in progress |
| 14 | Progress-over-time tracking (weight/goals trend) | ⏳ planned |
| 15 | Interactive AI chat coach | ⏳ planned |
| 16 | Associate/sponsor tools (separate initiative) | ⏳ planned |

## Deferred / Backlog
- **Usanimals (pediatric product):** excluded from catalog. HealthProfile requires age ≥ 13, and Usanimals targets children below that. Revisit if child/family profiles are added — would need `min_age`/`max_age` on Product and an age-range check in /recommend.
- **Associate/sponsor roles:** enrollment token generation is currently open to anyone. Once member vs. associate roles exist (Phase 16), restrict /enrollment/generate to associate accounts only.
- **Schema migrations:** currently running manual `ALTER TABLE` statements in Neon's SQL Editor when models change. Adopt Alembic (or similar) before this matters more, so schema changes don't require manual intervention.
- **products.json is tracked in git.** Originally excluded as "business data," but contains only public USANA product info (names, categories, public benefit descriptions) — no pricing or proprietary formulas. Committed so it deploys correctly on Render. Revisit only if a product-management admin feature is built later, at which point migrating to a Postgres table would make more sense.
- **Mobile responsiveness:** CSS hasn't been explicitly tested/tuned for small screens yet — relevant since the real member entry point (QR scan) is phone-first.