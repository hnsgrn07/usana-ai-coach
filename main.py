from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
import json

from model import HealthProfile, Product


app = FastAPI(title="USANA Nutritional Coach API")

# Opens products.json and checks that every product matches our rules
def load_products():

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

# Just says "hello, the API is working" when you visit the homepage
@app.get("/", tags=["Health Check"])
def home():
    """Basic liveness check — confirms the API is running."""
    return {"message": "Welcome to the USANA Nutritional Coach API!"}


# Takes a health profile someone submits and checks it's filled out correctly
@app.post("/profile", tags=["Health Profile"])
async def create_profile(profile: HealthProfile):
    return {
        "status": "success",
        "message": f"Profile validated for {profile.full_name}",
        "data": profile
    }


# Sends back the full list of products
@app.get("/products", tags=["Product Catalog"])
def get_products():
    return {"catalog": load_products()}


# Recommends products based on a submitted health profile
@app.post("/recommend", tags=["Recommendations"])
async def recommend_products(profile: HealthProfile):
    catalog = load_products()
    member_goals = set(goal.value for goal in profile.health_goals)
    member_restrictions = set(r.value for r in profile.dietary_restrictions)

    # Go through each product and see if it shares any goals with the person
    results = []
    for product in catalog:
        # Skip this product completely if it conflicts with the member's diet
        product_conflicts = set(c.value for c in product.contains)
        if member_restrictions & product_conflicts:
            continue
        
        product_goals = set(goal.value for goal in product.target_goals)
        overlap = member_goals & product_goals

        if overlap:
            results.append({
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "dosage": product.dosage,
                "matched_goals": sorted(overlap),
                "match_count": len(overlap)
            })

# Sort the results by how many goals matched, descending
    results.sort(key=lambda r: r["match_count"], reverse=True)

    if not results:
        return {
            "status": "no_matches",
            "message": "No products matched the selected health goals.",
            "recommendations": []
        }

    return {
        "status": "success",
        "recommendations": results
    }