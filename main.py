from fastapi import FastAPI
from model import HealthProfile

app = FastAPI(title="USANA Nutritional Coach API")


@app.get("/", tags=["Health Check"])
def home():
    """Basic liveness check — confirms the API is running."""
    return {"message": "Welcome to the USANA Nutritional Coach API!"}

@app.post("/profile", tags=["Health Profile"])
async def create_profile(profile: HealthProfile):
    """
    Validates a submitted health profile against the HealthProfile schema.
    No persistence yet (that's Phase 7) — this confirms the schema works.
    """
    return {
        "status": "success",
        "message": f"Profile validated for {profile.full_name}",
        "data": profile
    }