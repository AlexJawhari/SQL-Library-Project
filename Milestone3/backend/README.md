# Demo backend stub (Flask)

Uses MySQL (PyMySQL). Fill connection settings in `app.py` (MYSQL_CONFIG).

## Quick start
```bash
cd Milestone3/demo/backend
python -m venv .venv
.venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
python app.py
```

Server runs at `http://127.0.0.1:5000`. Frontend pages can be opened via file:// or any simple static server (e.g., `python -m http.server 8000` from `Milestone3/demo/frontend`).

## CSV data
- Source CSVs copied from `Milestone1/milestone1_output/` into `Milestone3/demo/data/`.
- Teammates can use MySQL `LOAD DATA INFILE` (or a short Python importer) to load these into the MySQL schema they create.
