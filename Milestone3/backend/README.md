# Backend (Flask + SQLite)

Flask backend with SQLite database for the Library Management System.

## Quick Start

### First Time Setup

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Initialize database:**
   ```powershell
   python init_db.py
   python data_import.py
   ```

### Running the Server

**Option 1: Use the startup script (from project root)**
```powershell
.\START_SERVER.bat
```

**Option 2: Manual start**
```powershell
python app.py
```

Server runs at `http://127.0.0.1:5000`

## Project Structure

- `app.py` - Main Flask application (entry point)
- `db.py` - SQLite database connection helper
- `schema.sql` - Database schema definition
- `data_import.py` - CSV data import script
- `routes/` - API route handlers
  - `search.py` - Book search endpoints
  - `loans.py` - Checkout/checkin endpoints
  - `borrowers.py` - Borrower management endpoints
  - `fines.py` - Fine calculation and payment endpoints
  - `admin.py` - Admin dashboard endpoints

## Database

- **File:** `library.db` (created automatically)
- **Schema:** Defined in `schema.sql`
- **Data:** Imported from CSV files in `Milestone3/data/`

## API Endpoints

All endpoints are prefixed with `/api`:
- `/api/search` - Search books
- `/api/checkout` - Checkout a book
- `/api/checkin` - Check in a book
- `/api/borrowers` - Create borrower
- `/api/fines` - Manage fines
- `/api/admin/*` - Admin dashboard endpoints

See `Milestone3/specs/api.md` for detailed API documentation.
