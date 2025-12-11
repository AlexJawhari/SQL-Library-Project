#!/usr/bin/env python3
"""
Simple script to start the Flask server.
Kills any existing Python processes on port 5000 first.
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def kill_existing_servers():
    """Kill any Python processes that might be using port 5000."""
    try:
        if sys.platform == "win32":
            # Windows
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                         capture_output=True, check=False)
        else:
            # Unix/Linux/Mac
            subprocess.run(["pkill", "-f", "python.*app.py"], 
                         capture_output=True, check=False)
        time.sleep(2)  # Wait for processes to die
        print("✓ Killed existing Python processes")
    except Exception as e:
        print(f"Note: Could not kill existing processes: {e}")

def main():
    """Start the Flask server."""
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("=" * 60)
    print("Library Management System - Starting Server")
    print("=" * 60)
    print()
    
    # Kill existing servers
    kill_existing_servers()
    
    # Check if database exists
    db_file = backend_dir / "library.db"
    if not db_file.exists():
        print("⚠ WARNING: Database file not found!")
        print("   Run 'python init_db.py' and 'python data_import.py' first.")
        print()
    
    # Start server
    print("Starting Flask server on http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        # Import and run the app
        from app import app
        app.run(host="127.0.0.1", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
    except Exception as e:
        print(f"\n\nERROR: Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

