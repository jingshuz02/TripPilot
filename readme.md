# TripPilot - Intelligent Travel Planning Assistant

An LLM-based agent system for comprehensive travel planning using LangGraph, Flask, and Streamlit.

## Team Members
- Backend Development: Jingshu Zeng, Junjie Xu, Yanwen Liu
- Frontend Development: Han Gao, Ni Chen, Zixin Ye

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd TripPilot
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env file with your API keys
```

### 5. Run the application

Backend:
```bash
python backend/app.py
```

Frontend (in a new terminal):
```bash
streamlit run frontend/streamlit_app.py
```

## Project Structure
- `/backend`: Flask API and LangGraph agents
- `/frontend`: Streamlit user interface
- `/tools`: API integrations (booking, maps, search)
- `/database`: SQLite database schema and utilities
- `/config`: Configuration management

## Features
- 🏨 Hotel and flight booking assistance
- 🗺️ Smart itinerary planning with maps
- 💰 Budget tracking and management
- 🔍 Context-aware travel information search