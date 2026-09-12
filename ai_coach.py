# ai_coach.py
# Turns a health profile + deterministic recommendations into personalized
# coaching content using Gemini. The AI never picks products — it only
# explains and encourages based on what the matching engine already decided.

import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

SYSTEM_PROMPT = """You are a friendly wellness coach writing a short, personal
note for a USANA member's dashboard. Never diagnose, name a medical condition,
or claim any product treats, cures, or prevents disease — use goal-based
language only. Do not recommend products outside the given list. Keep it
warm and concise, 3 short paragraphs max, with one general non-prescriptive
lifestyle suggestion tied to their goals."""

CHAT_SYSTEM_PROMPT = """You are a friendly wellness coach chatting with a
USANA member through their dashboard. You know their health goals and
recommended products (provided below). Answer their questions naturally
and conversationally.

Rules you must follow, always:
- Never diagnose, name a medical condition, or claim any product treats,
  cures, or prevents disease. Use goal-based language only.
- Do not recommend or discuss any product outside the ones listed below.
- If asked about medications, drug interactions, dosing beyond what's on
  the product label, or anything requiring medical judgment, say you can't
  advise on that and suggest they talk to a doctor or pharmacist.
- If asked something unrelated to wellness/nutrition/their profile, gently
  redirect back to what you can help with.
- Keep replies short and conversational — a few sentences, not an essay.
"""

_client = None


def get_client():
    """Creates the Gemini client only when first needed, not at import time.
    This way, a missing/bad API key only breaks coaching generation itself,
    never crashes the whole app on startup."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        _client = genai.Client(api_key=api_key)
    return _client


def generate_coaching(profile_data: dict, recommendations: list) -> str:
    """One-shot coaching note, generated when a profile is saved/updated."""
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

    client = get_client()

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


def generate_chat_reply(profile_data: dict, recommendations: list, message: str, history: list) -> str:
    """Ongoing back-and-forth chat reply, using the member's profile and
    recommendations as context plus recent conversation history."""
    goals = ", ".join(g.replace("_", " ") for g in profile_data["health_goals"])
    product_lines = "\n".join(
        f"- {rec['name']} (supports: {', '.join(g.replace('_', ' ') for g in rec['matched_goals'])})"
        for rec in recommendations
    ) or "None matched yet."

    # Keep only the last 10 messages so the prompt doesn't grow unbounded
    trimmed_history = history[-10:]
    transcript = "\n".join(
        f"{'Member' if h['role'] == 'user' else 'Coach'}: {h['content']}"
        for h in trimmed_history
    )

    prompt = f"""{CHAT_SYSTEM_PROMPT}

Member: {profile_data['full_name']}
Health goals: {goals}
Recommended products:
{product_lines}

Conversation so far:
{transcript}

Member: {message}

Reply as the coach."""

    client = get_client()

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