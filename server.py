from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import requests
import uuid

# Load environment variables from .env file
load_dotenv()

# Dictionary to store chat sessions in memory
sessions = {}

# Initialize FastAPI app
app = FastAPI()

# Get the absolute path to the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount the static folder to serve front-end files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def serve_index():
    """Serves the main frontend page."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_path):
        return JSONResponse({"error": f"index.html not found in static folder: {STATIC_DIR}"}, status_code=500)
    return FileResponse(index_path)


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Memory Agent running 🚀"}


@app.post("/chat")
async def chat_endpoint(request: Request):
    """Handles chat messages and interacts with the Gemini API."""
    try:
        data = await request.json()
        message = data.get("message")
        session_id = data.get("session_id")

        if not message:
            return JSONResponse({"response": "Please provide a message."}, status_code=400)

        # Get the Gemini API key from environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("GEMINI_API_KEY is not set in the environment variables.")
            return JSONResponse({"response": "Backend error: API key missing."}, status_code=500)

        # Create a new session if one doesn't exist
        if not session_id or session_id not in sessions:
            session_id = str(uuid.uuid4())
            sessions[session_id] = []

        # Get the chat history for the current session
        chat_history = sessions[session_id]

        # Append the user's new message to the history
        chat_history.append({"role": "user", "parts": [{"text": message}]})

        # Construct the API payload
        payload = {
            "contents": chat_history,
            "tools": [{"google_search": {}}],
            "systemInstruction": {
                "parts": [{"text": "You are a helpful and friendly assistant. Use your memory to remember previous conversations. Provide clear and concise answers."}]
            }
        }

        # URL for the Gemini API
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"

        # Make the API call
        response = requests.post(api_url, json=payload, timeout=30)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

        # Extract the bot's response
        api_response = response.json()
        bot_response_text = api_response.get("candidates", [{}])[0].get("content", {}).get(
            "parts", [{}])[0].get("text", "I'm sorry, I couldn't generate a response.")

        # Append the bot's response to the chat history
        chat_history.append(
            {"role": "model", "parts": [{"text": bot_response_text}]})

        return JSONResponse({"response": bot_response_text, "session_id": session_id})

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return JSONResponse({"response": f"API error: {http_err}. Check your API key and permissions."}, status_code=http_err.response.status_code)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return JSONResponse({"response": "An unexpected error occurred."}, status_code=500)
