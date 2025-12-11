SQL Library Management System - Milestone 3
CS-4347 Database Systems

================================================================================
COMPILE, BUILD, AND INSTALLATION INSTRUCTIONS
================================================================================

TECHNICAL DEPENDENCIES:
- Python 3.8 or higher
- Flask 3.0.2
- SQLite3 (included with Python)
- Web browser (Chrome, Firefox, Edge, or Safari)

PLATFORM/OS:
- Windows 10/11
- macOS
- Linux

SOFTWARE LIBRARIES:
- Flask==3.0.2 (Python web framework)
- sqlite3 (built-in Python module, no installation needed)

================================================================================
INSTALLATION STEPS
================================================================================

1. INSTALL PYTHON:
   - Download Python 3.8+ from https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify installation: open terminal/command prompt and run:
     python --version

2. INSTALL PROJECT DEPENDENCIES:
   - Navigate to project directory: cd Milestone3/backend
   - Create virtual environment (recommended):
     python -m venv .venv
   - Activate virtual environment:
     Windows: .venv\Scripts\activate
     macOS/Linux: source .venv/bin/activate
   - Install Flask:
     pip install -r requirements.txt

3. SETUP DATABASE:
   - Navigate to: cd Milestone3/backend
   - Create database schema:
     python -c "from db import get_db; conn = get_db(); exec(open('schema.sql').read()); conn.close()"
   - Import CSV data:
     python data_import.py
   - This creates library.db in the backend folder

4. RUN BACKEND SERVER:
   - From Milestone3/backend directory:
     python app.py
   - Server starts at http://127.0.0.1:5000
   - Keep this terminal window open

5. RUN FRONTEND:
   - Open a new terminal/command prompt
   - Navigate to: cd Milestone3/frontend
   - Start simple HTTP server:
     python -m http.server 8000
   - Open browser and go to: http://localhost:8000/landingpage.html
   - OR simply double-click landingpage.html to open directly

================================================================================
PROJECT STRUCTURE
================================================================================

Milestone3/
├── frontend/          - HTML/CSS/JavaScript frontend files
│   ├── landingpage.html
│   ├── search.html
│   ├── loans.html
│   ├── borrower.html
│   ├── fines.html
│   ├── css/
│   └── js/
├── backend/           - Flask backend application
│   ├── app.py         - Main Flask application
│   ├── db.py          - Database connection helper
│   ├── schema.sql     - Database schema
│   ├── data_import.py - CSV import script
│   ├── library.db     - SQLite database (created after setup)
│   ├── routes/        - API endpoint implementations
│   └── requirements.txt
├── data/              - CSV data files
│   ├── book.csv
│   ├── authors.csv
│   ├── book_authors.csv
│   └── borrower.csv
└── specs/             - API and business rules documentation

================================================================================
RESETTING THE DATABASE
================================================================================

To reset the database to initial state:
1. Delete library.db from Milestone3/backend/
2. Run schema creation and data import again (steps 3 above)

================================================================================
TROUBLESHOOTING
================================================================================

- Port 5000 already in use: Change port in app.py (line 25) to another port
- Port 8000 already in use: Change port in http.server command
- Module not found errors: Ensure virtual environment is activated and dependencies installed
- Database errors: Ensure schema.sql and data_import.py ran successfully
- Frontend not connecting: Ensure backend server is running on port 5000

================================================================================
SUBMISSION FILES
================================================================================

All source code is included in the Milestone3/ directory.
Design document: submission/design_document.txt
User guide: submission/user_guide.txt
This file: submission/readme.txt

