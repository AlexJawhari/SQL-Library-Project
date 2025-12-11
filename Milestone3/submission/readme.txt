SQL Library Management System - Milestone 3
CS-4347 Database Systems
Team Boron

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
     python init_db.py
   - Import CSV data:
     python data_import.py
   - This creates library.db in the backend folder

4. RUN BACKEND SERVER:
   - From Milestone3/backend directory:
     python app.py
   - Server starts at http://127.0.0.1:5000
   - Keep this terminal window open

5. ACCESS FRONTEND:
   - The Flask server serves the frontend files automatically
   - Open your web browser and navigate to:
     http://127.0.0.1:5000
   - OR directly to:
     http://127.0.0.1:5000/landingpage.html
   - You should see the Library Management System landing page

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
│   ├── admin.html
│   ├── css/
│   └── js/
├── backend/           - Flask backend application
│   ├── app.py         - Main Flask application
│   ├── db.py          - Database connection helper
│   ├── schema.sql     - Database schema
│   ├── init_db.py     - Database initialization script
│   ├── data_import.py - CSV import script
│   ├── library.db     - SQLite database (created after setup)
│   ├── routes/        - API endpoint implementations
│   │   ├── search.py
│   │   ├── loans.py
│   │   ├── borrowers.py
│   │   ├── fines.py
│   │   └── admin.py
│   └── requirements.txt
├── data/              - CSV data files
│   ├── book.csv
│   ├── authors.csv
│   ├── book_authors.csv
│   └── borrower.csv
└── submission/        - Submission documents
    ├── design_document.txt
    ├── user_guide.txt
    └── readme.txt

================================================================================
RESETTING THE DATABASE
================================================================================

To reset the database to initial state:
1. Delete library.db from Milestone3/backend/
2. Run schema creation and data import again (steps 3 above):
   python init_db.py
   python data_import.py

================================================================================
TROUBLESHOOTING
================================================================================

- Port 5000 already in use: 
  Windows: taskkill /F /IM python.exe
  macOS/Linux: killall python
  Then restart the server

- Module not found errors: 
  Ensure virtual environment is activated and dependencies installed:
  pip install -r requirements.txt

- Database errors: 
  Ensure schema.sql and data_import.py ran successfully:
  python init_db.py
  python data_import.py

- Frontend not connecting: 
  Ensure backend server is running on port 5000
  Use http://127.0.0.1:5000 (not localhost)

- 404 errors on pages: 
  Ensure Flask server is running
  Check that you're accessing http://127.0.0.1:5000/landingpage.html

================================================================================
QUICK START (AFTER INITIAL SETUP)
================================================================================

1. Navigate to backend directory:
   cd Milestone3/backend

2. Start the Flask server:
   python app.py

3. Open browser to:
   http://127.0.0.1:5000

4. The system is ready to use!

================================================================================
SUBMISSION FILES
================================================================================

All source code is included in the Milestone3/ directory.
Design document: submission/design_document.txt
User guide: submission/user_guide.txt
This file: submission/readme.txt

================================================================================
API ENDPOINTS
================================================================================

The system provides the following REST API endpoints:

GET  /api/search?q=TERM          - Search books by ISBN, title, or author
POST /api/checkout                - Checkout a single book
POST /api/checkout/batch          - Checkout multiple books
POST /api/checkin                 - Check in a book by loan_id
GET  /api/checkin/search          - Search for active loans
POST /api/borrowers               - Create a new borrower
POST /api/fines/refresh           - Refresh fines for all late loans
GET  /api/fines?card_no=ID        - List fines grouped by borrower
POST /api/fines/pay               - Pay all fines for a borrower
GET  /api/admin/stats              - Get system statistics
GET  /api/admin/borrowers          - Get all borrowers with search
GET  /api/admin/loans              - Get all loans with filters
GET  /api/admin/fines              - Get detailed fines information
POST /api/admin/fines/apply        - Manually apply a fine (admin only)

All endpoints return JSON responses. Error responses include an "error" field.

================================================================================
BUSINESS RULES
================================================================================

- Maximum 3 active loans per borrower
- Books cannot be checked out if already checked out
- Borrowers with unpaid fines cannot check out books
- Loan period is 14 days from checkout date
- Fines are $0.25 per day for late returns
- Fines can only be paid when all books are returned
- Each borrower can have only one library card (one SSN per card)

================================================================================
