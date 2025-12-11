# Library Management System - Testing Guide

## 🚀 Starting the Application (Step-by-Step for Demo)

### IMPORTANT: Complete Startup Process

Follow these steps **in order** to start the application from scratch:

### Step 1: Open Terminal/PowerShell
Open PowerShell or Command Prompt and navigate to the project:
```powershell
cd C:\Coding\SQL-Library-Project
```

### Step 2: Kill Any Running Servers
**CRITICAL:** Make sure no other Flask servers are running:
```powershell
# Kill all Python processes
taskkill /F /IM python.exe

# Wait 2-3 seconds, then verify port is free
netstat -ano | findstr :5000
```
If you still see port 5000 in use, wait a few more seconds and check again.

### Step 3: Navigate to Backend Directory
```powershell
cd Milestone3\backend
```

### Step 4: Verify Python Installation
```powershell
python --version
```
Should show **Python 3.8 or higher**.

### Step 5: Install Dependencies (First Time Only)
If this is your first time running:
```powershell
pip install -r requirements.txt
```

### Step 6: Initialize Database (First Time Only)
If database doesn't exist or you want to reset:
```powershell
# Create database schema
python init_db.py

# Import data from CSV files (takes ~1 minute)
python data_import.py
```

**Note:** Database file `library.db` is created in `Milestone3/backend/` directory.

### Step 7: Start the Flask Server

**OPTION 1: Use the batch file (EASIEST)**
```powershell
# From project root
.\START_SERVER.bat
```

**OPTION 2: Manual start**
```powershell
cd Milestone3\backend
python app.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

**⚠️ CRITICAL:** 
- **Keep this terminal window open!** 
- The server MUST stay running for the website to work
- Do NOT close this window during demo
- To stop: Press `CTRL+C` in this window
- **If you see 404 errors, kill all Python processes and restart:**
  ```powershell
  taskkill /F /IM python.exe
  cd Milestone3\backend
  python app.py
  ```

### Step 8: Open the Website
Open your web browser and go to:
```
http://127.0.0.1:5000
```

**DO NOT use `localhost`** - use `127.0.0.1` instead.

### Step 9: Verify Everything Works
1. You should see the **Library Management System** landing page
2. Click on **"🔧 Admin Dashboard"**
3. Click **"Show All"** button in the **Borrowers** tab
4. **Expected:** Table shows borrowers with card IDs, names, etc.
5. If you see borrowers listed → **Everything is working!** ✅

---

## Troubleshooting Startup Issues

### Issue: "Port 5000 already in use"
**Solution:** Another Flask server is running. Close it:
```powershell
# Find Python processes
Get-Process python

# Kill all Python processes (if needed)
Get-Process python | Stop-Process -Force

# Then restart
python app.py
```

### Issue: "Module not found" errors
**Solution:** Install dependencies:
```powershell
pip install -r requirements.txt
```

### Issue: "Database file not found"
**Solution:** Initialize the database:
```powershell
python init_db.py
python data_import.py
```

### Issue: "No data showing"
**Solution:** Make sure data was imported:
```powershell
python data_import.py
```

### Issue: Website shows 404 errors
**Solution:** 
1. Make sure Flask server is running (check terminal)
2. Make sure you're accessing `http://127.0.0.1:5000` (not `localhost`)
3. Check browser console (F12) for errors

---

## Prerequisites
- Flask server running at http://127.0.0.1:5000
- Database initialized with data (run `python init_db.py` and `python data_import.py` if needed)

## Test Checklist

### 1. Book Search Functionality

#### Test 1.1: Basic Search
1. Navigate to http://127.0.0.1:5000/search
2. Enter a search term (e.g., "test", "william", "123")
3. Click "Search" or press Enter
4. **Expected**: Results table shows books matching ISBN, title, or author
5. **Verify**: 
   - Results show ISBN, Title, Authors (comma-separated), Checked Out status, Borrower ID
   - Case-insensitive search works (try "WILLIAM" and "william")
   - Substring matching works (search "will" should find "William")

#### Test 1.2: Search by ISBN
1. Search for a specific ISBN (use one from your database)
2. **Expected**: Book with that ISBN appears in results

#### Test 1.3: Search by Author
1. Search for an author name (partial or full)
2. **Expected**: All books by that author appear

#### Test 1.4: Checkout from Search
1. Perform a search
2. Check the checkbox next to one or more available books (not checked out)
3. **Expected**: "Checkout Selected Books" section appears
4. Enter a borrower card number (e.g., "ID000001")
5. Click "Checkout Selected"
6. **Expected**: 
   - Success message shows
   - Selected books are checked out
   - Search results refresh showing books as checked out

---

### 2. Borrower Management

#### Test 2.1: Create New Borrower
1. Navigate to http://127.0.0.1:5000/borrower
2. Fill in:
   - SSN: 123-45-6789 (or any 9 digits)
   - Name: Test User
   - Address: 123 Test St
   - Phone: (optional)
3. Click "Create borrower"
4. **Expected**: 
   - Success message with new card_id (format: ID######)
   - Card ID is auto-generated

#### Test 2.2: Duplicate SSN Prevention
1. Try to create another borrower with the same SSN
2. **Expected**: Error message "Borrower exists" with existing card_id

#### Test 2.3: Required Fields Validation
1. Try to create borrower without SSN, name, or address
2. **Expected**: Error message "Missing required fields"

#### Test 2.4: SSN Format Validation
1. Try SSN with wrong number of digits
2. **Expected**: Error message "SSN must contain 9 digits"

---

### 3. Book Loans - Checkout

#### Test 3.1: Single Book Checkout
1. Navigate to http://127.0.0.1:5000/loans
2. Enter:
   - ISBN: (use a valid ISBN from your database)
   - Borrower card_no: (use an existing card, e.g., "ID000001")
3. Click "Checkout"
4. **Expected**: 
   - Success message with loan_id and due_date (14 days from today)
   - Book is now checked out

#### Test 3.2: Maximum 3 Loans Rule
1. Checkout 3 books to the same borrower
2. Try to checkout a 4th book
3. **Expected**: Error "Borrower has reached maximum of 3 active loans"

#### Test 3.3: Book Already Checked Out
1. Checkout a book
2. Try to checkout the same book again (to same or different borrower)
3. **Expected**: Error "Book is already checked out"

#### Test 3.4: Unpaid Fines Block
1. Create a borrower with unpaid fines (see Fines section)
2. Try to checkout a book
3. **Expected**: Error "Borrower has unpaid fines and cannot checkout books"

#### Test 3.5: Invalid Book/Borrower
1. Try to checkout with non-existent ISBN
2. **Expected**: Error "Book not found"
3. Try with non-existent card_no
4. **Expected**: Error "Borrower not found"

#### Test 3.6: Batch Checkout
1. Enter multiple ISBNs (one per line) in the textarea
2. Enter a borrower card_no
3. Click "Batch checkout"
4. **Expected**: 
   - Each book processed individually
   - Success/error status for each ISBN
   - Books that succeed are checked out
   - Books that fail show error reasons

---

### 4. Book Loans - Checkin

#### Test 4.1: Checkin by Loan ID
1. Checkout a book (note the loan_id from success message)
2. Enter the loan_id in the "Checkin" section
3. Click "Checkin by ID"
4. **Expected**: Success message "Checked in loan_id X"
5. Verify: Book is now available for checkout again

#### Test 4.2: Checkin Search - By ISBN
1. Checkout a book
2. In "Checkin" section, enter the ISBN in "Search by ISBN"
3. Click "Search Loans"
4. **Expected**: 
   - Table shows active loan(s) matching that ISBN
   - Shows Loan ID, ISBN, Title, Card No, Borrower, Date Out, Due Date
5. Click "Checkin" button next to a loan
6. **Expected**: Book is checked in

#### Test 4.3: Checkin Search - By Card No
1. Enter a borrower's card number
2. Click "Search Loans"
3. **Expected**: All active loans for that borrower appear

#### Test 4.4: Checkin Search - By Borrower Name
1. Enter part of a borrower's name (substring)
2. Click "Search Loans"
3. **Expected**: All active loans for borrowers matching that name appear

#### Test 4.5: Checkin Search - All Active Loans
1. Leave all search fields empty
2. Click "Search Loans"
3. **Expected**: All active loans in the system appear

#### Test 4.6: Already Checked In
1. Try to checkin a book that's already checked in
2. **Expected**: Error "Book is already checked in"

---

### 5. Fines Management

#### Test 5.1: Refresh Fines
1. Navigate to http://127.0.0.1:5000/fines
2. Click "Refresh fines" (card number optional)
3. **Expected**: 
   - Success message showing count of fines refreshed
   - Fines calculated for all late books ($0.25 per day)

#### Test 5.2: List Fines - By Card Number
1. Enter a borrower's card number
2. Click "List fines"
3. **Expected**: 
   - Table shows fines for that borrower
   - Shows Card No, Total Fines (summed), Paid status
   - Only unpaid fines shown by default

#### Test 5.3: List Fines - All Borrowers
1. Leave card number empty
2. Click "List fines"
3. **Expected**: All borrowers with fines listed (grouped by card_no)

#### Test 5.4: Show Paid Fines
1. Check "Include paid" checkbox
2. Click "List fines"
3. **Expected**: Both paid and unpaid fines shown

#### Test 5.5: Pay Fines - Success
1. Ensure borrower has unpaid fines
2. Ensure borrower has NO unreturned books (checkin all their books first)
3. Enter borrower's card number
4. Click "Pay fines"
5. **Expected**: 
   - Success message showing number of fines paid
   - Fines marked as paid
   - List fines now shows them as paid (if "Include paid" is checked)

#### Test 5.6: Pay Fines - With Unreturned Books
1. Create a borrower with unpaid fines
2. Ensure they have at least one unreturned book
3. Try to pay fines
4. **Expected**: Error "Cannot pay fines while borrower has unreturned books"

#### Test 5.7: Fine Calculation
1. Checkout a book
2. Wait or manually set due_date in database to a past date
3. Refresh fines
4. **Expected**: Fine calculated as (days late) * $0.25
5. Checkin the book (after due date)
6. Refresh fines again
7. **Expected**: Fine amount updated based on actual return date

---

### 6. Integration Tests

#### Test 6.1: Complete Workflow
1. Create a new borrower
2. Search for books
3. Checkout 2 books from search results
4. Verify books show as checked out in search
5. Search for loans to checkin
6. Checkin one book
7. Verify it's available again in search
8. Wait or set due date to past
9. Refresh fines
10. List fines for the borrower
11. Checkin the remaining book
12. Pay fines
13. Verify fines are paid

#### Test 6.2: Business Rules Enforcement
1. Try to checkout 4th book (should fail at 3)
2. Try to checkout same book twice (should fail)
3. Try to checkout with unpaid fines (should fail)
4. Try to pay fines with books out (should fail)
5. All should show appropriate error messages

---

### 7. Error Handling Tests

#### Test 7.1: Invalid Inputs
- Empty search query → Error message
- Invalid loan_id → Error message
- Missing required fields → Error message
- Invalid card number format → Error message

#### Test 7.2: Database Errors
- Non-existent ISBN → "Book not found"
- Non-existent borrower → "Borrower not found"
- Non-existent loan_id → "Loan not found"

---

## Quick Smoke Test (5 minutes)

If you're short on time, run these critical tests:

1. ✅ Search for a book → Should return results
2. ✅ Create a borrower → Should get card_id
3. ✅ Checkout a book → Should succeed
4. ✅ Search for loans → Should find the active loan
5. ✅ Checkin the book → Should succeed
6. ✅ Refresh fines → Should complete without error
7. ✅ List fines → Should show results (if any exist)

---

## Common Issues to Watch For

1. **404 Errors**: Make sure Flask server is running
2. **Empty Results**: Check if database has data (run data_import.py)
3. **SQL Errors**: Check browser console and Flask terminal for error messages
4. **CORS Issues**: Shouldn't happen since Flask serves frontend, but check if API calls fail

---

## Testing Tips

- Use browser developer tools (F12) to see API responses
- Check Flask terminal for backend errors
- Test with real data from your CSV files
- Try edge cases (empty strings, special characters, etc.)
- Verify database state directly if needed: `sqlite3 Milestone3/backend/library.db`

---

## Success Criteria

All tests should:
- ✅ Complete without errors
- ✅ Show appropriate success/error messages
- ✅ Update database correctly
- ✅ Reflect changes in UI immediately
- ✅ Enforce all business rules

