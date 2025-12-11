"""Repair database integrity issues after manual deletions."""
import sqlite3
from db import get_db

def repair_database():
    """Fix orphaned records and integrity issues."""
    try:
        conn = get_db()
    except sqlite3.DatabaseError as e:
        print(f"ERROR: Database file is corrupted or not a valid database.")
        print(f"Error details: {e}")
        print("\nTo fix this, you can:")
        print("1. Delete the corrupted library.db file")
        print("2. Run: python init_db.py")
        print("3. Run: python data_import.py")
        return
    
    try:
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Check for orphaned loans (borrower deleted)
        cursor.execute("""
            SELECT loan_id, card_id 
            FROM BOOK_LOANS 
            WHERE card_id NOT IN (SELECT card_id FROM BORROWER)
        """)
        orphaned_loans = cursor.fetchall()
        
        if orphaned_loans:
            print(f"Found {len(orphaned_loans)} orphaned loans (borrower deleted)")
            # Delete orphaned loans
            for loan in orphaned_loans:
                loan_id = loan["loan_id"]
                # Delete associated fines first
                cursor.execute("DELETE FROM FINES WHERE loan_id = ?", (loan_id,))
                # Delete the loan
                cursor.execute("DELETE FROM BOOK_LOANS WHERE loan_id = ?", (loan_id,))
                print(f"  Deleted orphaned loan {loan_id}")
        
        # Check for orphaned loans (book deleted)
        cursor.execute("""
            SELECT loan_id, isbn 
            FROM BOOK_LOANS 
            WHERE isbn NOT IN (SELECT isbn_primary FROM BOOK)
        """)
        orphaned_book_loans = cursor.fetchall()
        
        if orphaned_book_loans:
            print(f"Found {len(orphaned_book_loans)} orphaned loans (book deleted)")
            # Delete orphaned loans
            for loan in orphaned_book_loans:
                loan_id = loan["loan_id"]
                # Delete associated fines first
                cursor.execute("DELETE FROM FINES WHERE loan_id = ?", (loan_id,))
                # Delete the loan
                cursor.execute("DELETE FROM BOOK_LOANS WHERE loan_id = ?", (loan_id,))
                print(f"  Deleted orphaned loan {loan_id} (book {loan['isbn']} deleted)")
        
        # Check for orphaned fines (loan deleted)
        cursor.execute("""
            SELECT loan_id 
            FROM FINES 
            WHERE loan_id NOT IN (SELECT loan_id FROM BOOK_LOANS)
        """)
        orphaned_fines = cursor.fetchall()
        
        if orphaned_fines:
            print(f"Found {len(orphaned_fines)} orphaned fines")
            # Delete orphaned fines
            for fine in orphaned_fines:
                loan_id = fine["loan_id"]
                cursor.execute("DELETE FROM FINES WHERE loan_id = ?", (loan_id,))
                print(f"  Deleted orphaned fine for loan {loan_id}")
        
        # Check for orphaned book_authors (book deleted)
        cursor.execute("""
            SELECT isbn_primary, author_id 
            FROM BOOK_AUTHORS 
            WHERE isbn_primary NOT IN (SELECT isbn_primary FROM BOOK)
        """)
        orphaned_book_authors = cursor.fetchall()
        
        if orphaned_book_authors:
            print(f"Found {len(orphaned_book_authors)} orphaned book_authors entries")
            cursor.execute("""
                DELETE FROM BOOK_AUTHORS 
                WHERE isbn_primary NOT IN (SELECT isbn_primary FROM BOOK)
            """)
            print(f"  Deleted {len(orphaned_book_authors)} orphaned book_authors entries")
        
        # Check for orphaned book_authors (author deleted)
        cursor.execute("""
            SELECT isbn_primary, author_id 
            FROM BOOK_AUTHORS 
            WHERE author_id NOT IN (SELECT author_id FROM AUTHORS)
        """)
        orphaned_author_refs = cursor.fetchall()
        
        if orphaned_author_refs:
            print(f"Found {len(orphaned_author_refs)} orphaned book_authors entries (author deleted)")
            cursor.execute("""
                DELETE FROM BOOK_AUTHORS 
                WHERE author_id NOT IN (SELECT author_id FROM AUTHORS)
            """)
            print(f"  Deleted {len(orphaned_author_refs)} orphaned book_authors entries")
        
        conn.commit()
        print("\nDatabase repair completed successfully!")
        
        # Verify integrity
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        if result[0] == "ok":
            print("Database integrity check: OK")
        else:
            print(f"WARNING: Database integrity issues detected: {result[0]}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error repairing database: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Repairing database...")
    repair_database()

