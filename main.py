from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
import json

from model import HealthProfile, Product


app = FastAPI(title="USANA Nutritional Coach API")

def load_products():
    """
    Loads and validates the product catalog against the Product schema.
    Fails loudly (500) if the file is missing, malformed, or contains
    a product with an invalid target_goal — better to catch this at
    request time than have it silently break matching later.
    """
    try:
        with open("products.json", "r") as file:
            raw_catalog = json.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Product catalog not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Product catalog is malformed JSON")

    try:
        validated_catalog = [Product(**item) for item in raw_catalog]
    except ValidationError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Product catalog contains invalid entries: {e}"
        )

    return validated_catalog


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

@app.get("/products", tags=["Product Catalog"])
def get_products():
    """Returns the full validated product catalog."""
    return {"catalog": load_products()}