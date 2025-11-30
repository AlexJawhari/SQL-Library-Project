-- 1. Create Tables
CREATE TABLE IF NOT EXISTS book (
    isbn VARCHAR(20) PRIMARY KEY,
    title VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS authors (
    author_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS book_authors (
    isbn VARCHAR(20),
    author_id INT,
    PRIMARY KEY (isbn, author_id),
    FOREIGN KEY (isbn) REFERENCES book(isbn),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

CREATE TABLE IF NOT EXISTS book_loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    card_id VARCHAR(20),
    isbn VARCHAR(20),
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

-- NULL -> OUT
INSERT INTO book_loans (loan_id, card_id, isbn, date_out, due_date, date_in) VALUES
(1, 'ID000001', '0923398364', '2025-11-01', '2025-11-15', '2025-11-15'), -- IN
(2, 'ID000002', '0891787631', '2025-11-02', '2025-11-16', '2025-11-15'), -- IN
(3, 'ID000003', 'T619875682', '2025-11-03', '2025-11-17', NULL), -- OUT
(4, 'ID000004', 'X2723786q6', '2025-11-04', '2025-11-18', '2025-11-15'); -- IN


-- 3. Book Search
-- case-insensitive search by ISBN, title, or author
-- returns ISBN, title, authors, and status
DELIMITER //

CREATE PROCEDURE search_books(IN p_search VARCHAR(255))
BEGIN
    SELECT
        b.isbn AS ISBN,
        b.title AS TITLE,
        GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') AS AUTHORS,
        IF (
            EXISTS (
                SELECT 1
                FROM book_loans bl
                WHERE bl.isbn = b.isbn
                AND bl.date_in IS NULL
            ),
            'OUT',
            'IN'
        ) AS STATUS
    
    FROM book b
    LEFT JOIN book_authors ba ON b.isbn = ba.isbn
    LEFT JOIN authors a ON ba.author_id = a.author_id
    
    --perform search
    WHERE 
        LOWER(b.isbn) LIKE LOWER(CONCAT('%', p_search, '%')) OR
        LOWER(b.title) LIKE LOWER(CONCAT('%', p_search, '%')) OR
        LOWER(a.name) LIKE LOWER(CONCAT('%', p_search, '%'))
    
    GROUP BY b.isbn, b.title
    ORDER BY b.title;
END //

DELIMITER ;