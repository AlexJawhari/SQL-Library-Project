# SQL-Library-Project

A Library Management System with a web-based interface for managing books, borrowers, loans, and fines.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup (First Time Only)

1. **Install dependencies:**
   ```powershell
   cd Milestone3\backend
   pip install -r requirements.txt
   ```

2. **Initialize database:**
   ```powershell
   python init_db.py
   python data_import.py
   ```

### Running the Application

**Option 1: Use the batch file (Windows)**
```powershell
.\START_SERVER.bat
```

**Option 2: Manual start**
```powershell
cd Milestone3\backend
python app.py
```

The server will start at `http://127.0.0.1:5000`

Open your browser and navigate to `http://127.0.0.1:5000` to access the Library Management System.

## Project Structure

- **`Milestone3/backend/`** - Flask backend with SQLite database
  - `app.py` - Main Flask application
  - `routes/` - API route handlers
  - `schema.sql` - Database schema
  - `data_import.py` - Import CSV data into database
  
- **`Milestone3/frontend/`** - Static HTML/CSS/JavaScript frontend
  - `landingpage.html` - Main entry point
  - `admin.html` - Admin dashboard for librarians
  - `js/` - JavaScript modules
  - `css/` - Stylesheets

- **`Milestone3/data/`** - CSV data files (books, authors, borrowers)

- **`Milestone3/specs/`** - API and business rules documentation

## Features

- **Book Search** - Search books by ISBN, title, or author
- **Checkout/Checkin** - Manage book loans
- **Borrower Management** - Create and manage borrower accounts
- **Fines System** - Automatic fine calculation and payment
- **Admin Dashboard** - Comprehensive view of all system data for librarians

## Documentation

- **Setup Instructions:** See `STARTUP_INSTRUCTIONS.md`
- **Testing Guide:** See `TESTING_GUIDE.md`
- **API Documentation:** See `Milestone3/specs/api.md`
- **Business Rules:** See `Milestone3/specs/business_rules.md`