USE library_demo;

-- change path later based on where it is on your pc
-- 'C:/Users/you/Projects/Milestone3/backend/data/book.csv'

LOAD DATA LOCAL INFILE '/ABSOLUTE/PATH/TO/Milestone3/backend/data/book.csv'
INTO TABLE BOOK
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(isbn_primary, isbn10, isbn13, title);

LOAD DATA LOCAL INFILE '/ABSOLUTE/PATH/TO/Milestone3/backend/data/authors.csv'
INTO TABLE AUTHORS
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(author_id, name);

LOAD DATA LOCAL INFILE '/ABSOLUTE/PATH/TO/Milestone3/backend/data/book_authors.csv'
INTO TABLE BOOK_AUTHORS
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(isbn_primary, author_id);

LOAD DATA LOCAL INFILE '/ABSOLUTE/PATH/TO/Milestone3/backend/data/borrower.csv'
INTO TABLE BORROWER
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMININATED BY '\n'
IGNORE 1 LINES
(card_id, ssn, bname, address, phone);
