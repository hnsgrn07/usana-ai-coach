# models.py

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum

class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"
    very_active = "very_active"


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class HealthGoal(str, Enum):
    """
    Goal-based vocabulary (not condition/diagnostic-based).
    This controls what the recommendation engine is allowed to match against.
    """
    energy_support = "energy_support"
    immune_support = "immune_support"
    joint_support = "joint_support"
    digestive_health = "digestive_health"
    heart_health = "heart_health"
    weight_management = "weight_management"
    stress_management = "stress_management"
    sleep_quality = "sleep_quality"
    skin_health = "skin_health"
    cognitive_support = "cognitive_support"
    general_wellness = "general_wellness"
    eye_health = "eye_health"         
    bone_health = "bone_health"        
    detox_support = "detox_support"    
    mens_health = "mens_health"


class DietaryRestriction(str, Enum):
    vegetarian = "vegetarian"
    vegan = "vegan"
    gluten_free = "gluten_free"
    dairy_free = "dairy_free"
    nut_allergy = "nut_allergy"
    none = "none"


class HealthProfile(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the member (placeholder until Phase 8 auth)")

    full_name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=13, le=120, description="Age in years")
    gender: Gender
    weight_kg: float = Field(..., gt=0, le=400)
    height_cm: float = Field(..., gt=0, le=272)

    activity_level: ActivityLevel
    health_goals: List[HealthGoal] = Field(
        default_factory=list,
        description="Areas of focus, not medical diagnoses"
    )
    dietary_restrictions: List[DietaryRestriction] = Field(default_factory=list)

    notes: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Free-text field for anything not captured above"
    )

    @field_validator("health_goals")
    @classmethod
    def at_least_one_goal(cls, v):
        if not v:
            raise ValueError("At least one health goal must be selected")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "usr_001",
                "full_name": "Jane Doe",
                "age": 34,
                "gender": "female",
                "weight_kg": 65.0,
                "height_cm": 168.0,
                "activity_level": "moderate",
                "health_goals": ["energy_support", "immune_support"],
                "dietary_restrictions": ["dairy_free"],
                "notes": "Prefers capsules over powders"
            }
        }

class Product(BaseModel):
    id: str
    name: str
    category: str
    target_goals: List[HealthGoal]
    dosage: str
    contains: List[DietaryRestriction] = Field(
        default_factory=list,
        description="Dietary restrictions this product conflicts with (e.g. fish oil conflicts with vegan)"
    )