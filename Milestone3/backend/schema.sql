PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS BOOK (
    isbn_primary TEXT NOT NULL,
    isbn10       TEXT,
    isbn13       TEXT,
    title        TEXT NOT NULL,
    PRIMARY KEY (isbn_primary)
);

CREATE TABLE IF NOT EXISTS AUTHORS (
    author_id INTEGER NOT NULL,
    name      TEXT NOT NULL,
    PRIMARY KEY (author_id)
);

CREATE TABLE IF NOT EXISTS BOOK_AUTHORS (
    isbn_primary TEXT NOT NULL,
    author_id    INTEGER,
    PRIMARY KEY (isbn_primary, author_id),
    FOREIGN KEY (isbn_primary) REFERENCES BOOK(isbn_primary),
    FOREIGN KEY (author_id) REFERENCES AUTHORS(author_id)
);

CREATE TABLE IF NOT EXISTS BORROWER (
    card_id TEXT NOT NULL,
    ssn     TEXT NOT NULL,
    bname   TEXT NOT NULL,
    address TEXT NOT NULL,
    phone   TEXT,
    PRIMARY KEY (card_id),
    UNIQUE (ssn)
);

CREATE TABLE IF NOT EXISTS BOOK_LOANS (
    loan_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn     TEXT NOT NULL,
    card_id  TEXT NOT NULL,
    date_out TEXT NOT NULL,
    due_date TEXT NOT NULL,
    date_in  TEXT,
    FOREIGN KEY (isbn) REFERENCES BOOK(isbn_primary),
    FOREIGN KEY (card_id) REFERENCES BORROWER(card_id)
);

CREATE TABLE IF NOT EXISTS FINES (
    loan_id  INTEGER NOT NULL,
    fine_amt REAL NOT NULL,
    paid     INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (loan_id),
    FOREIGN KEY (loan_id) REFERENCES BOOK_LOANS(loan_id)
);
