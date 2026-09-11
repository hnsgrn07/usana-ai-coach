# ai_coach.py

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a friendly wellness coach writing a short, personal
note for a USANA member's dashboard. Never diagnose, name a medical condition,
or claim any product treats, cures, or prevents disease — use goal-based
language only. Do not recommend products outside the given list. Keep it
warm and concise, 3 short paragraphs max, with one general non-prescriptive
lifestyle suggestion tied to their goals."""


def generate_coaching(profile_data: dict, recommendations: list) -> str:
    goals = ", ".join(g.replace("_", " ") for g in profile_data["health_goals"])
    product_lines = "\n".join(
        f"- {rec['name']} (supports: {', '.join(g.replace('_', ' ') for g in rec['matched_goals'])})"
        for rec in recommendations
    ) or "None matched yet."

    prompt = f"""{SYSTEM_PROMPT}

Member: {profile_data['full_name']}
Health goals: {goals}
Recommended products:
{product_lines}

Write their personal coaching note."""

    last_error = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            last_error = e
            time.sleep(2)

    raise last_error