from fastapi import Depends, FastAPI, HTTPException
from pydantic import ValidationError
import json

from requests import Session

from model import HealthProfile, Product
from database import engine, SessionLocal, Base
from db_models import ProfileDB


app = FastAPI(title="USANA Nutritional Coach API")

# Creates the profiles table in the database if it doesn't exist yet
Base.metadata.create_all(bind=engine)


# Opens a database session for a request, then closes it when done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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


# Saves a health profile to the database, or updates it if that user_id already exists
@app.post("/profile", tags=["Health Profile"])
async def create_profile(profile: HealthProfile, db: Session = Depends(get_db)):
    data = profile.model_dump(mode="json")  # Convert Pydantic model to dict for SQLAlchemy

    existing_profile = db.query(ProfileDB).filter(ProfileDB.user_id == profile.user_id).first()
    if existing_profile:
        # Update existing profile
        for key, value in data.items():
            setattr(existing_profile, key, value)
        db.commit()
        db.refresh(existing_profile)
        message = f"Profile updated for {profile.full_name}"
    else:
        # Create new profile
        new_profile = ProfileDB(**data)
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        message = f"Profile created for {profile.full_name}"
    return {
        "status": "success",
        "message": message,
        "data": data
    }

# Retrieves a health profile from the database by user_id
@app.get("/profile/{user_id}", tags=["Health Profile"])
def get_profile(user_id: str, db:  Session = Depends(get_db)):
    profile = db.query(ProfileDB).filter(ProfileDB.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "status": "success",
        "data": {
            "user_id": profile.user_id,
            "full_name": profile.full_name,
            "age": profile.age,
            "gender": profile.gender,
            "weight_kg": profile.weight_kg,
            "height_cm": profile.height_cm,
            "activity_level": profile.activity_level,
            "health_goals": profile.health_goals,
            "dietary_restrictions": profile.dietary_restrictions,
            "notes": profile.notes
        }
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