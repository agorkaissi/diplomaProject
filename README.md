# Project Name
diplomaProject

# Description
TBD

# Technologies Used
- Python 3.14
- FastAPI
- HTML / CSS (optional)
- uv python env

# Requirements
- python: 3.14.1
- uv: 0.9.28
- node.js: v24.13.0
- Ollama client 

# Project Structure
```
diplomaProject/
│
├── api/
│   ├── main.py
│   ├── db.py
│   ├── models.py
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
