# SQL-Library-Project

Project that organizes csv files for authors and their respective books into clean formatted data.

The data is used to create a library system and backend.

Which allows for a user-friendly GUI to operate the library.

## Milestone 3 Demo (local)

- Path: `Milestone3/demo/`
- Frontend: static HTML in `frontend/` (Bootstrap, no build tools). Open directly or run `python -m http.server 8000` from that folder. Backend must be running for live data.
- Data: CSVs copied from Milestone1 into `Milestone3/demo/data/` (read-only demo copy).
- Specs: `Milestone3/demo/specs/api.md` and `Milestone3/demo/specs/business_rules.md`.
- Backend stub: `Milestone3/demo/backend/app.py` (Flask, MySQL placeholder). To run:
  1. `cd Milestone3/demo/backend`
  2. `python -m venv .venv` and activate
  3. `pip install -r requirements.txt`
  4. Fill MySQL settings in `app.py`, then `python app.py` (runs on http://127.0.0.1:5000)

Group will wire real endpoints against MySQL per the specs.