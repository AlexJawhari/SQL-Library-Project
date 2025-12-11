"""Quick test script to verify database setup"""
from db import get_db

def test_db():
    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Test tables exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        print(f"Tables found: {', '.join(tables)}")
        
        expected_tables = ['BOOK', 'AUTHORS', 'BOOK_AUTHORS', 'BORROWER', 'BOOK_LOANS', 'FINES']
        missing = [t for t in expected_tables if t not in tables]
        if missing:
            print(f"WARNING: Missing tables: {', '.join(missing)}")
        else:
            print("[OK] All tables exist")
        
        # Test data loaded
        cur.execute("SELECT COUNT(*) as count FROM BOOK")
        book_count = cur.fetchone()["count"]
        print(f"Books in database: {book_count}")
        
        cur.execute("SELECT COUNT(*) as count FROM AUTHORS")
        author_count = cur.fetchone()["count"]
        print(f"Authors in database: {author_count}")
        
        cur.execute("SELECT COUNT(*) as count FROM BORROWER")
        borrower_count = cur.fetchone()["count"]
        print(f"Borrowers in database: {borrower_count}")
        
        if book_count > 0 and author_count > 0:
            print("[OK] Database appears to be set up correctly")
        else:
            print("WARNING: Database may be empty - run data_import.py")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_db()

