# Backend (Flask + SQLite)

Uses SQLite database (file-based, no server setup needed).

## Quick start
```bash
cd Milestone3/backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# First time setup: create database and import data
python init_db.py
python data_import.py

# Run server
python app.py
```

Server runs at `http://127.0.0.1:5000`. Frontend pages can be opened via file:// or any simple static server (e.g., `python -m http.server 8000` from `Milestone3/frontend`).

## Database setup
- SQLite database file: `library.db` (created automatically)
- Schema: `schema.sql` (run once to create tables)
- Data import: `data_import.py` (loads CSVs from `Milestone3/data/`)

## Structure (per teammate task)
- `app.py` registers blueprints; keep as entry point.
- `db.py` holds SQLite connection helper.
- `schema.sql` — database schema (SQLite syntax)
- `data_import.py` — CSV import script
- `routes/search.py` — Task A
- `routes/loans.py` — Task B
- `routes/borrowers.py` — Task C
- `routes/fines.py` — Task D
