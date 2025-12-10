CREATE DATABASE IF NOT EXISTS library_demo
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE library_demo;

CREATE TABLE IF NOT EXISTS BOOK (
    isbn_primary VARCHAR(20) NOT NULL,
    isbn10       VARCHAR(20),
    isbn13       VARCHAR(20),
    title        VARCHAR(255) NOT NULL,
    PRIMARY KEY (isbn_primary)
);

CREATE TABLE IF NOT EXISTS AUTHORS (
    author_id INT NOT NULL,
    name      VARCHAR(255) NOT NULL,
    PRIMARY KEY (author_id)
);

CREATE TABLE IF NOT EXISTS BOOK_AUTHORS (
    isbn_primary VARCHAR(20) NOT NULL,
    author_id    INT,
    PRIMARY KEY (isbn_primary, author_id),
    CONSTRAINT fk_ba_book
        FOREIGN KEY (isbn_primary) REFERENCES BOOK(isbn_primary),
    CONSTRAINT fk_ba_author
        FOREIGN KEY (author_id) REFERENCES AUTHORS(author_id)
);

CREATE TABLE IF NOT EXISTS BORROWER (
    card_id VARCHAR(8)  NOT NULL,
    ssn     VARCHAR(11) NOT NULL,
    bname   VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone   VARCHAR(20),
    PRIMARY KEY (card_id),
    UNIQUE KEY uq_borrower_ssn (ssn)
);

CREATE TABLE IF NOT EXISTS BOOK_LOANS (
    loan_id  INT AUTO_INCREMENT,
    isbn     VARCHAR(20) NOT NULL,
    card_id  VARCHAR(8) NOT NULL,
    date_out DATE NOT NULL,
    due_date DATE NOT NULL,
    date_in  DATE NULL,
    PRIMARY KEY (loan_id),
    CONSTRAINT fk_bl_book
        FOREIGN KEY (isbn) REFERENCES BOOK(isbn_primary),
    CONSTRAINT fk_bl_borrower
        FOREIGN KEY (card_id) REFERENCES BORROWER(card_id)
);

CREATE TABLE IF NOT EXISTS FINES (
    loan_id  INT NOT NULL,
    fine_amt DECIMAL(8,2) NOT NULL,
    paid     TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (loan_id),
    CONSTRAINT fk_fines_loan
        FOREIGN KEY (loan_id) REFERENCES BOOK_LOANS(loan_id)
);
