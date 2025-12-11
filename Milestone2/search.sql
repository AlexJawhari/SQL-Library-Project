-- 1. Create Tables
CREATE TABLE IF NOT EXISTS book (
    isbn TEXT PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS book_authors (
    isbn TEXT,
    author_id INTEGER,
    PRIMARY KEY (isbn, author_id),
    FOREIGN KEY (isbn) REFERENCES book(isbn),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

CREATE TABLE IF NOT EXISTS book_loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id TEXT,
    isbn TEXT,
    date_out DATE,
    due_date DATE,
    date_in DATE,
    FOREIGN KEY (isbn) REFERENCES book(isbn)
);

-- 2. Insert Sample Data
INSERT INTO book (isbn, title) VALUES
('0923398364', 'Houses of Williamsburg, Virginia'),
('0891787631', 'College Algebra'),
('T619875682', 'Wills and Trusts for Retirement'),
('X2723786q6', 'The History of the Han Dynasty');

INSERT INTO authors (author_id, name) VALUES
(1, 'John Smith'),
(2, 'Will McDaniels, Mary Jones'),
(3, 'Barbara Brown, ESQ'),
(4, 'Dawn Williamson');

INSERT INTO book_authors (isbn, author_id) VALUES
('0923398364', 1),
('0891787631', 2),
('T619875682', 3),
('X2723786q6', 4);

INSERT INTO book_loans (loan_id, card_id, isbn, date_out, due_date, date_in) VALUES
(1, 'ID000001', '0923398364', '2025-11-01', '2025-11-15', '2025-11-15'),
(2, 'ID000002', '0891787631', '2025-11-02', '2025-11-16', '2025-11-15'),
(3, 'ID000003', 'T619875682', '2025-11-03', '2025-11-17', NULL),
(4, 'ID000004', 'X2723786q6', '2025-11-04', '2025-11-18', '2025-11-15');

-- 3. Book Search
WITH search_term AS (
    SELECT 'will' AS term
)
SELECT
    b.isbn AS ISBN,
    b.title AS Title,
    (
        SELECT GROUP_CONCAT(name, ', ')
        FROM (
            SELECT DISTINCT a.name
            FROM authors a
            JOIN book_authors ba ON ba.author_id = a.author_id
            WHERE ba.isbn = b.isbn
        )
    ) AS Authors,
    CASE 
        WHEN EXISTS (
            SELECT 1
            FROM book_loans bl
            WHERE bl.isbn = b.isbn
            AND bl.date_in IS NULL
        )
        THEN 'OUT'
        ELSE 'IN'
    END AS Status,
    (
        SELECT bl.card_id
        FROM book_loans bl
        WHERE bl.isbn = b.isbn
        AND bl.date_in IS NULL
        LIMIT 1
    ) AS Borrower_ID
FROM book b, search_term st
WHERE 
    LOWER(b.isbn) LIKE LOWER('%' || st.term || '%') OR
    LOWER(b.title) LIKE LOWER('%' || st.term || '%') OR
    EXISTS (
        SELECT 1
        FROM authors a
        JOIN book_authors ba ON ba.author_id = a.author_id
        WHERE ba.isbn = b.isbn
        AND LOWER(a.name) LIKE LOWER('%' || st.term || '%')
    )
ORDER BY b.title;