# Memory Agent 🤖💡

## A smart chatbot that remembers what you tell it!

It can:

Chat with users in a friendly way

Remember important information about you

Use those memories to have better conversations

## How to Use

Clone the repository:

```
git clone <your-repo-url>
cd MemoryAgent
```

Set up a Python environment:
```
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

Install the required packages:
```
pip install -r requirements.txt
```

Create a .env file in the project folder with the following:
```
USER_ID=default
MODEL=anthropic/claude-3-5-sonnet-20240620
SYSTEM_PROMPT=You are a helpful and friendly chatbot. Get to know the user! Ask questions! Be spontaneous! {user_info} System Time: {time}
```

Run the chatbot:
```
python main.py
```

## Project Structure
```
MemoryAgent/
├── memory_agent/     # Core code
├── main.py           # Run the chatbot
├── .env              # Environment variables
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Notes

This is a work-in-progress AI chatbot

Currently uses in-memory storage; future versions may store memories in a database

Friendly and curious—just like a real conversation!
