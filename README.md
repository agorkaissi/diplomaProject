# Project Name
diplomaProject

# Description
TBD

# Technologies Used
- Python 3.12
- FastAPI
- HTML / CSS
- uv python env
- Ollama 

# Requirements
- python: 3.12
- uv: 0.9.28
- node.js: v24.13.0
- Ollama client 
- llama3.2:1b model

# Project Structure
```
diplomaProject/
│
├── api/
│   ├── data/
│   │   ├── hogwart/
│   │   ├── hr/
│   │   ├── lotr/
│   │   └── supervisor/
│   │
│   ├── .gitingore
│   ├── agents.db
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   ├── ollama_client.py
│   ├── runtime.py
│   ├── schemas.py
│   └── test_main.http
│ 
├── ui/   
│   ├── public
│   │   ├── index.html
│   │   ├── manifest.json
│   │   └── robots.txt
│   │ 
│   └── src
│       └── pages/
│       │   ├── dashboard/
│       │   │   ├── agentsOverview.js
│       │   │   └── agents.js
│       │   │ 
│       │   ├── AiAssistant.js
│       │   ├── Dashboard.js
│       │   ├── Home.js
│       │   └── Scenarios.js
│       │
│       ├── App.css
│       ├── App.js
│       ├── App.test.js
│       ├── Home.js
│       ├── index.css
│       ├── index.js
│       ├── Layout.js
│       ├── reportWebVitals.js
│       ├── router.js
│       └── setupTests.js
│
├── .dockerignore
├── .gitignore   
├── pyproject.toml
├── README.md
└── uv.lock
```
## Files ignored by Git
The project uses `.gitignore` to exclude virtual environments, environment
variables, cache files, etc.

## Installation
1. Clone the repository:
```
https://github.com/agorkaissi/diplomaProject.git
```
2. Create and Activate a virtual environment & install all dependencies:
- Backend (Python / FastAPI)
```
cd diplomaProject
uv sync
```
- Frontend (UI / Node)
```
cd diplomaProject/ui
npm install
```
3. Prepare Ollama client 
- download and install ollama client from: https://ollama.com/download
```
ollama list
ollama pull llama3.2:1b
ollama run llama3.2:1b
```

## Running the Application
- Backend (separate console)
```
cd diplomaProject/api
uv run uvicorn main:app --reload
```
- Frontend (separate console)
```
cd diplomaProject/ui
npm start
```
then open your browser (Tested on Brave) and open:

The application will be available at:
http://localhost:3000

Interactive Swagger documentation:
http://127.0.0.1:8000/docs

Redoc documentation:
http://127.0.0.1:8000/redoc
