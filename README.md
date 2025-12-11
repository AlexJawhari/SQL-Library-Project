# SQL-Library-Project

Project that organizes csv files for authors and their respective books into clean formatted data.

The data is used to create a library system and backend.

Which allows for a user-friendly GUI to operate the library.

## Milestone 3

- Path: `Milestone3/`
- Frontend: static HTML in `frontend/` (Bootstrap, no build tools). Open directly or run `python -m http.server 8000` from that folder. Backend must be running for live data.
- Data: CSVs from Milestone1 in `Milestone3/data/`.
- Specs: `Milestone3/specs/api.md` and `Milestone3/specs/business_rules.md`.
- Backend: `Milestone3/backend/` (Flask + SQLite). To run:
  1. `cd Milestone3/backend`
  2. `python -m venv .venv` and activate
  3. `pip install -r requirements.txt`
  4. First time: create schema and import data (see `backend/README.md`)
  5. `python app.py` (runs on http://127.0.0.1:5000)