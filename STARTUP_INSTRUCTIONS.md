# Library Management System - Startup Instructions

## Complete Startup Guide for Demo

Follow these steps **in order** to start the application from scratch.

---

## Step 1: Open Terminal/PowerShell

Open PowerShell or Command Prompt and navigate to the project directory:
```powershell
cd C:\Coding\SQL-Library-Project
```

---

## Step 2: Check for Running Servers

**IMPORTANT:** Make sure no other Flask servers are running on port 5000.

```powershell
# Check if port 5000 is in use
netstat -ano | findstr :5000

# If you see any results, kill Python processes:
taskkill /F /IM python.exe
```

Wait 2-3 seconds after killing processes.

---

## Step 3: Navigate to Backend Directory

```powershell
cd Milestone3\backend
```

---

## Step 4: Verify Python Installation

```powershell
python --version
```

Should show **Python 3.8 or higher**. If not, install Python first.

---

## Step 5: Install Dependencies (First Time Only)

If this is your first time running the project:

```powershell
pip install -r requirements.txt
```

This installs Flask and other required packages. You only need to do this once (unless requirements.txt changes).

---

## Step 6: Initialize Database (First Time Only)

If the database doesn't exist or you want to reset it:

```powershell
# Create database schema
python init_db.py

# Import data from CSV files (this may take a minute)
python data_import.py
```

**Note:** 
- The database file `library.db` will be created in `Milestone3/backend/` directory
- Data import loads ~25,000 books, ~15,000 authors, and 1,000 borrowers
- You only need to do this once (unless you want to reset the database)

---

## Step 7: Start the Flask Server

```powershell
python app.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

**⚠️ IMPORTANT:** 
- **Keep this terminal window open!** The server must stay running.
- Do NOT close this window or the website will stop working.
- To stop the server, press `CTRL+C` in this window.

---

## Step 8: Open the Website

Open your web browser and navigate to:

```
http://127.0.0.1:5000
```

**DO NOT use `localhost`** - use `127.0.0.1` instead.

You should see the **Library Management System** landing page with 5 cards:
- Search Books
- Loans
- Borrowers
- Fines
- 🔧 Admin Dashboard

---

## Step 9: Verify Everything Works

### Quick Test:
1. Click on **"🔧 Admin Dashboard"**
2. Click **"Show All"** button in the **Borrowers** tab
3. **Expected:** You should see a table with borrowers listed
4. If you see borrowers, **everything is working!** ✅

### If You See Data:
- ✅ Server is running correctly
- ✅ Database is connected
- ✅ All routes are working
- ✅ Ready for demo!

---

## Troubleshooting

### Problem: "Port 5000 already in use"

**Solution:**
```powershell
# Kill all Python processes
taskkill /F /IM python.exe

# Wait 2-3 seconds, then restart
cd Milestone3\backend
python app.py
```

### Problem: "Module not found: flask"

**Solution:**
```powershell
pip install -r requirements.txt
```

### Problem: "Database file not found" or "No such table"

**Solution:**
```powershell
cd Milestone3\backend
python init_db.py
python data_import.py
```

### Problem: Website shows 404 errors

**Check:**
1. Is Flask server running? (Check terminal window)
2. Are you using `http://127.0.0.1:5000` (not `localhost`)?
3. Open browser console (F12) → Check for errors
4. Check Flask terminal for error messages

### Problem: Admin Dashboard shows "No data"

**Check:**
1. Did you run `python data_import.py`? (You need data!)
2. Open browser console (F12) → Check Network tab for failed API calls
3. Check Flask terminal for error messages
4. Try clicking "Show All" button

### Problem: "Multiple servers running"

**Solution:**
```powershell
# Kill all Python processes
taskkill /F /IM python.exe

# Wait, then start fresh
cd Milestone3\backend
python app.py
```

---

## Quick Reference Commands

### Start Server (from project root):
```powershell
cd Milestone3\backend
python app.py
```

### Reset Database:
```powershell
cd Milestone3\backend
python init_db.py
python data_import.py
```

### Kill All Python Processes:
```powershell
taskkill /F /IM python.exe
```

### Check if Server is Running:
```powershell
netstat -ano | findstr :5000
```

---

## For Demo Day

### Before Demo:
1. ✅ Test the site works (follow steps above)
2. ✅ Verify Admin Dashboard shows data
3. ✅ Test at least one checkout/checkin
4. ✅ Have a borrower card ID ready (from Admin Dashboard)

### During Demo:
1. Keep the terminal window visible (shows server is running)
2. Start with Admin Dashboard to show all data
3. Use Admin Dashboard to get borrower card IDs
4. Demonstrate each feature systematically

### Quick Demo Flow:
1. **Admin Dashboard** → Show all borrowers (get a card ID)
2. **Search** → Find a book → Checkout from search
3. **Admin Dashboard → Loans** → Show the new loan
4. **Admin Dashboard → Fines** → Refresh fines → Show fines
5. **Loans** → Checkin the book
6. **Admin Dashboard → Fines** → Pay fines

---

## File Locations

- **Backend:** `Milestone3/backend/`
- **Frontend:** `Milestone3/frontend/`
- **Database:** `Milestone3/backend/library.db`
- **Data CSV files:** `Milestone3/data/`

---

## Need Help?

1. Check Flask terminal for error messages
2. Check browser console (F12) for JavaScript errors
3. Verify database exists: `dir Milestone3\backend\library.db`
4. Verify server is running: Check terminal for "Running on http://127.0.0.1:5000"

