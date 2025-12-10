-- Create borrower table
CREATE TABLE BORROWER (
    card_id VARCHAR(8) NOT NULL,
    ssn     VARCHAR(11) NOT NULL,
    bname   VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone   VARCHAR(20),
    PRIMARY KEY (card_id),
    UNIQUE KEY uq_borrower_ssn (ssn)
);

-- Create borrower

-- Validates SSN, name, and address (NOT NULL)
-- Rejects creation if SSN existed previously (one per SSN)

DELIMITER //

CREATE PROCEDURE create_borrower(
     IN p_ssn VARCHAR(11),
     IN p_bname VARCHAR(100),
     IN p_address VARCHAR(255),
     IN p_phone VARCHAR(20),
     OUT p_card_no VARCHAR(20)
)

BEGIN
     DECLARE v_max_card_no VARCHAR(20);
     DECLARE v_next_num INT;
     DECLARE v_new_card_no VARCHAR(20);

     --validation of attributes

     IF p_ssn IS NULL OR TRIM(p_ssn) = '' THEN
          SIGNAL SQLSTATE '45000'
               SET MESSAGE_TEXT = 'Borrower cannot be created without SSN.';
     END IF;

     IF p_bname IS NULL OR TRIM(p_bname) = '' THEN
          SIGNAL SQLSTATE '45000' 
               SET MESSAGE_TEXT = 'Borrower cannot be created without name.';
     END IF;


     IF p_address IS NULL OR TRIM(p_address) = '' THEN
          SIGNAL SQLSTATE '45000' 
               SET MESSAGE_TEXT = 'Borrower cannot be created without address.';
     END IF;



     --ensure one borrower per ssn

     IF EXISTS (
          SELECT 1
          FROM Borrower b
          WHERE b.ssn = p_ssn
     ) THEN
         SIGNAL SQLSTATE '45000'
               SET MESSAGE_TEXT = 'A borrower has used this SSN already, one borrower cannot have multiple cards.';
     END IF;


     --generate new card_no compatible with existing IDs

     SELECT MAX(card_no)
     INTO v_max_card_no
     FROM Borrower;

     IF v_max_card_no IS NULL THEN
          SET v_next_num = 1;
     ELSE
           SET v_next_num = CAST(SUBSTRING(v_max_card_no, 3) AS UNSIGNED) + 1;
     END IF;
     

     SET v_new_card_no = CONCAT('ID', LPAD(v_next_num, 6, '0'));
     
     INSERT INTO Borrower (card_no, ssn, bname, address, phone)
     VALUES (v_new_card_no, p_ssn, p_bname, p_address, p_phone);

     SET p_card_no = v_new_card_no;

END //
DELIMITER ;



--Example for test
--SET @new_card_no = NULL;
--CALL create_borrower(
--     '123-45-6789',
--     'Greg John',
--     '123 Utd St, Richardson, TX',
--     '323-415-6923',
--     @new_card_no
--);

--SELECT @new_card_no AS created_card_no;

--duplicate ssn which should cause an error
--CALL create_borrower(
--     '123-45-6789',
--     'Gregory John',
--     '321 Utd St, Richardson, TX',
--     '123-414-2323',
--     @new_card_no
--);
     
