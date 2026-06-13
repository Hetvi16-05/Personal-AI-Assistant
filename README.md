# Personal AI Assistant

An AI-powered assistant with:

- Personal memory
- Study planning
- User profile learning
- Future support for healthcare and customer support modes

## Getting Started

### 1. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

## Project Structure

```
personal-ai-assistant/
│
├── app.py              # Streamlit entry point
├── requirements.txt    # Python dependencies
│
├── modules/
│   ├── memory.py       # Conversation & long-term memory
│   ├── profile.py      # User profile management
│   └── assistant.py    # Core AI assistant logic
│
├── data/
│   ├── memory.json     # Persisted memory store
│   └── profile.json    # Persisted user profile
│
├── assets/             # Images, icons, static files
│
└── README.md
```

## Status

In Development 🚀

| Day | Feature |
|-----|---------|
| 1   | Project setup & basic chat UI ✅ |
| 2   | Memory system |
| 3   | User profile learning |
| 4+  | LLM integration |
