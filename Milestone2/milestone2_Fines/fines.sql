-- 1. Create the Fines table
CREATE TABLE Fines (
    loan_id INT PRIMARY KEY,
    -- fine_amt attribute is a dollar amount that should have two decimal places. The data type should be fixed-decimal, not float or real.
    fine_amt DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    -- paid attribute is a boolean value (or integer 0/1) that idicates whether a fine has been paid. 
    paid TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (loan_id) REFERENCES book_loans(loan_id)
);

-- 2. Procedure to refresh fines
DELIMITER //
CREATE PROCEDURE refresh_fines()
BEGIN
    -- Case 1: Returned late
    -- Fines are assessed at a rate of $0.25/day (twenty-five cents per day)
    -- Provide a mechanism (i.e. method/function) that updates/refreshes entries in the FINES table
    -- Late books that have been returned — the fine will be [(the difference in days between the due_date and date_in) * $0.25]

    INSERT INTO fines (loan_id, fine_amt, paid)
    SELECT loan_id,
            ROUND((DATEDIFF(date_in, due_date) * 0.25), 2),
            0
    FROM book_loans
    WHERE date_in IS NOT NULL AND date_in > due_date
    ON DUPLICATE KEY UPDATE
        -- When updating fines, If paid  == FALSE, do not create a new row, only update the fine_amt if different than current value
        -- If paid == TRUE, do nothing
        fine_amt = IF(fines.paid = 0, VALUES(fine_amt), fines.fine_amt);

    -- Case 2: Still out late
    -- Late book that are still out — the estimated fine will be [(the difference between the due_date and TODAY) * $0.25]
    INSERT INTO fines (loan_id, fine_amt, paid)
    SELECT loan_id,
            ROUND((DATEDIFF(CURDATE(), due_date) * 0.25), 2),
            0
    FROM book_loans
    WHERE date_in IS NULL AND due_date < CURDATE()
    ON DUPLICATE KEY UPDATE
        -- When updating fines, If paid  == FALSE, update, if paid == TRUE, do nothing
        fine_amt = IF(fines.paid = 0, VALUES(fine_amt), fines.fine_amt);
END //
DELIMITER;

-- 3.Procedure to pay fine
DELIMITER //
CREATE PROCEDURE pay_all_fines(IN p_card_id VARCHAR(20))
BEGIN
    -- Block payment if borrower has unpaid fines for books not yet returned
    IF EXISTS (
        SELECT 1
        FROM fines f
        JOIN book_loans bl ON f.loan_id = bl.loan_id
        WHERE bl.card_id = p_card_id AND f.paid = 0 AND bl.date_in IS NULL
    ) THEN
        SIGNAL SQLSTATE '45000'
         SET MESSAGE_TEXT = 'Cannot pay fines: Unreturned books with unpaid fines.';
    END IF;
    -- all umpaid fines are paid
    UPDATE fines f
    JOIN book_loans bl ON f.loan_id = bl.loan_id
    SET f.paid = 1
    WHERE bl.card_id = p_card_id AND f.paid = 0;
    
END //
DELIMITER ;

-- 4. Queries to display fines for a borrower

-- Display of Fines should be grouped by card_no. i.e. SUM the fine_amt for each Borrower
-- Display of Fines should provide a mechanism to filter out previously paid fines 
SELECT bl.card_id, SUM(f.fine_amt) AS total_fines
FROM fines f
JOIN book_loans bl ON f.loan_id = bl.loan_id
GROUP BY bl.card_id
