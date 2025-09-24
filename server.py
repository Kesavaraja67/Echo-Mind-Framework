import os
import time
from typing import Dict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Import Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables from .env file
load_dotenv()

# ====================================
# Firebase Initialization
# ====================================
# Check if the Firebase credentials are set in the environment
firebase_config_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
if not firebase_config_path or not os.path.exists(firebase_config_path):
    print("Firebase service account key not found. Chat history will not be saved.")
    db = None
else:
    try:
        cred = credentials.Certificate(firebase_config_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
        db = None

# ====================================
# FastAPI Application
# ====================================
app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str
    session_id: str


@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Handles a chat request, sends it to the Gemini API, and saves the
    conversation to Firestore.
    """
    session_id = request.session_id
    user_message = request.message

    # Check for Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return JSONResponse(content={"response": "Backend error: API key missing"})

    try:
        # === Get existing chat history from Firestore ===
        if db:
            doc_ref = db.collection("chat_sessions").document(session_id)
            doc = doc_ref.get()
            if doc.exists:
                history = doc.to_dict().get("messages", [])
            else:
                history = []
        else:
            history = []

        # === Send to Gemini API ===
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": history + [{"role": "user", "parts": [{"text": user_message}]}]
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

        gemini_response = response.json()
        bot_response = gemini_response.get("candidates", [{}])[0].get("content", {}).get(
            "parts", [{}])[0].get("text", "I'm sorry, I couldn't generate a response.")

        # === Save new messages to Firestore ===
        if db:
            new_history = history + [
                {"role": "user", "parts": [{"text": user_message}]},
                {"role": "model", "parts": [{"text": bot_response}]}
            ]
            doc_ref.set({"messages": new_history})

        return JSONResponse(content={"response": bot_response, "session_id": session_id})

    except httpx.HTTPError as e:
        return JSONResponse(
            content={
                "response": f"API call failed with status: {e.response.status_code}"},
            status_code=500
        )
    except Exception as e:
        return JSONResponse(
            content={"response": f"An unexpected error occurred: {str(e)}"},
            status_code=500
        )
