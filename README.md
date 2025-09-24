# Memory Agent Chatbot

This project is a full-stack chatbot application that demonstrates the power of integrating a Large Language Model (LLM) with a persistent memory system. The chatbot can hold conversations and remember key details from previous interactions, even after the application has been closed.

## Key Features

- **Full-Stack Architecture:** A clean separation between the frontend (HTML, CSS, JavaScript) and the backend (FastAPI in Python).
- **Persistent Memory:** Utilizes a database (such as Firebase Firestore) to store conversation history, allowing the bot to remember past conversations.
- **Advanced AI Integration:** Connects to a powerful LLM (like Google's Gemini) via a secure API, ensuring high-quality, contextual responses.
- **Easy Setup:** Simple environment configuration using a `.env` file to manage API keys and credentials.

## Getting Started

Follow these steps to get a local version of the project up and running.

### Prerequisites

- Python 3.9+
- A virtual environment (recommended)
- A Gemini API key from Google AI Studio
- A Firebase project with a service account key

### 1. Set Up Your Environment

Create a project folder and add the necessary files and sub-folders.
```
/your-project/
├── .env
├── requirements.txt
├── server.py
└── static/
├── index.html
├── script.js
└── style.css
```

### 2. Install Dependencies

In your terminal, navigate to the project's root folder and install the required Python libraries.

```
pip install -r requirements.txt

```
### 3. Configure API Keys
Open the .env file and add your API keys.
```
GEMINI_API_KEY="your-gemini-api-key"
FIREBASE_SERVICE_ACCOUNT_KEY="path/to/your-firebase-key.json"
```
### 4. Run the Server
Start the FastAPI server from the project's root folder.
```
uvicorn server:app --reload
```
### 6. Open the Application
Navigate to http://127.0.0.1:8000 in your web browser to start chatting with your Memory Agent!
