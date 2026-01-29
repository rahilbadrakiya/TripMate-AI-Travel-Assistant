# ORBIS Backend
## Quickstart
python -m venv .venv
.\.venv\Scripts\activate
python -m uvicorn main:app --reload


uvicorn main:app --host 0.0.0.0 --port 8000
python -m uvicorn main:app --reload
Open http://127.0.0.1:8000/docs


Run backend:
  cd backend
  python -m venv .venv
  .\.venv\Scripts\activate
  pip install -r requirements.txt
  copy .env.example .env   # then edit .env and paste keys
  python -m uvicorn main:app --reload
  Open http://127.0.0.1:8000/docs
