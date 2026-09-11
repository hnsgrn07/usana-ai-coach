# main.py

from datetime import datetime
from ai_coach import generate_coaching
import qrcode
import io
from fastapi.responses import StreamingResponse
import uuid
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import ValidationError
from sqlalchemy.orm import Session
import json

from model import HealthProfile, Product, UserRegister, UserOut, UserLogin, Token, EnrollmentTokenOut
from database import engine, SessionLocal, Base
from db_models import ProfileDB, UserDB, EnrollmentToken
from auth import hash_password, verify_password, create_access_token, decode_access_token
from fastapi.middleware.cors import CORSMiddleware
import os

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app = FastAPI(title="USANA Nutritional Coach API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://usana-dashboard.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Lets Swagger's "Authorize" button accept a plain pasted token
security = HTTPBearer()


# Opens a database session for a request, then closes it when done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Reads the token from the request, checks it's valid, and finds the matching user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserDB:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(UserDB).filter(UserDB.user_id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


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


@app.get("/", tags=["Health Check"])
def home():
    return {"message": "Welcome to the USANA Nutritional Coach API!"}


# Creates a new user account, but only if their enrollment token is valid and unused
@app.post("/register", response_model=UserOut, tags=["Auth"])
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    token_row = db.query(EnrollmentToken).filter(EnrollmentToken.token == user.enrollment_token).first()

    if not token_row:
        raise HTTPException(status_code=400, detail="Invalid enrollment token")
    if token_row.is_used:
        raise HTTPException(status_code=400, detail="This enrollment token has already been used")

    existing = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = UserDB(
        user_id=str(uuid.uuid4()),
        email=user.email,
        hashed_password=hash_password(user.password),
        sponsor_id=token_row.sponsor_id
    )
    db.add(new_user)

    token_row.is_used = True  # burn the token so it can't be reused

    db.commit()
    db.refresh(new_user)

    return UserOut(user_id=new_user.user_id, email=new_user.email)


# Checks email + password, hands back a token if they match
@app.post("/login", response_model=Token, tags=["Auth"])
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token({"sub": user.user_id})
    return Token(access_token=token)


# Saves a health profile for the logged-in user (can't save one for someone else)
# Saves a health profile for the logged-in user, and generates a
# personalized AI coaching note based on their matched recommendations
@app.post("/profile", tags=["Health Profile"])
async def create_profile(
    profile: HealthProfile,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    profile.user_id = current_user.user_id
    data = profile.model_dump(mode="json")

    # Run the deterministic matching first, then let the AI narrate it
    rec_result = build_recommendations(profile)
    recommendations = rec_result.get("recommendations", [])

    try:
        coaching_text = generate_coaching(data, recommendations)
    except Exception as e:
        coaching_text = None  # don't block saving the profile if the AI call fails

    existing = db.query(ProfileDB).filter(ProfileDB.user_id == profile.user_id).first()

    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        existing.coaching_text = coaching_text
        existing.coaching_generated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        message = f"Profile updated for {profile.full_name}"
    else:
        new_profile = ProfileDB(**data, coaching_text=coaching_text, coaching_generated_at=datetime.utcnow())
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        message = f"Profile saved for {profile.full_name}"

    return {"status": "success", "message": message, "data": data}

# Returns the logged-in user's saved AI coaching note
@app.get("/coach/{user_id}", tags=["AI Coach"])
def get_coaching(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    profile = db.query(ProfileDB).filter(ProfileDB.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "coaching_text": profile.coaching_text,
        "generated_at": profile.coaching_generated_at,
    }


# Looks up a saved profile — only the profile's owner can view it
@app.get("/profile/{user_id}", tags=["Health Profile"])
def get_profile(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")

    profile = db.query(ProfileDB).filter(ProfileDB.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
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


@app.get("/products", tags=["Product Catalog"])
def get_products():
    return {"catalog": load_products()}


# Looks up a saved profile, then finds matching products — only the owner can run this
@app.get("/recommend/{user_id}", tags=["Recommendations"])
def recommend_for_saved_profile(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile's recommendations")

    profile_row = db.query(ProfileDB).filter(ProfileDB.user_id == user_id).first()
    if not profile_row:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = HealthProfile(
        user_id=profile_row.user_id,
        full_name=profile_row.full_name,
        age=profile_row.age,
        gender=profile_row.gender,
        weight_kg=profile_row.weight_kg,
        height_cm=profile_row.height_cm,
        activity_level=profile_row.activity_level,
        health_goals=profile_row.health_goals,
        dietary_restrictions=profile_row.dietary_restrictions,
        notes=profile_row.notes
    )

    return build_recommendations(profile)


# Left open (no login needed) — useful for testing matching logic without an account
@app.post("/recommend", tags=["Recommendations"])
async def recommend_from_payload(profile: HealthProfile):
    return build_recommendations(profile)

# Creates a new enrollment token — this is what a QR code will encode.
# Open for now (no login required) since "associate" roles don't exist yet.
@app.post("/enrollment/generate", response_model=EnrollmentTokenOut, tags=["Enrollment"])
def generate_enrollment_token(sponsor_id: str = None, db: Session = Depends(get_db)):
    new_token = EnrollmentToken(
        token=str(uuid.uuid4()),
        sponsor_id=sponsor_id
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    enrollment_url = f"{FRONTEND_URL}/register?token={new_token.token}"

    return EnrollmentTokenOut(token=new_token.token, enrollment_url=enrollment_url)


# Turns a token into an actual scannable QR code image
@app.get("/enrollment/qr/{token}", tags=["Enrollment"])
def get_enrollment_qr(token: str):
    enrollment_url = f"{FRONTEND_URL}/register?token={token}"

    qr_img = qrcode.make(enrollment_url)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")

# Tells the frontend who's currently logged in, based on their token
@app.get("/me", tags=["Auth"])
def get_me(current_user: UserDB = Depends(get_current_user)):
    return {"user_id": current_user.user_id, "email": current_user.email}


# Shared matching logic used by both /recommend routes above
def build_recommendations(profile: HealthProfile):
    catalog = load_products()
    member_goals = set(goal.value for goal in profile.health_goals)
    member_restrictions = set(r.value for r in profile.dietary_restrictions)

    results = []
    for product in catalog:
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