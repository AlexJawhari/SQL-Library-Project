-- 1. Create the BOOK_LOANS table
CREATE TABLE Book_Loans (
	loan_id INT PRIMARY KEY NOT NULL IDENTITY(1, 1),
	isbn NUMERIC(13, 0) UNIQUE NOT NULL,
	card_id VARCHAR(20) UNIQUE NOT NULL,
	date_out DATE,
	date_in DATE,
	due_date DATE,
	FOREIGN KEY (isbn) REFERENCES Book(isbn),
	FOREIGN KEY (card_id) REFERENCES Borrower(card_id)
);

-- 2. Provide a checkout() function that satisfies the functional requirements in the documentation.
CREATE PROCEDURE checkout(
	@isbn NUMERIC(13, 0), 
	@card_id VARCHAR(20)
	) AS
BEGIN
	DECLARE @num_borrowed INT;

	SELECT @num_borrowed = COUNT(*)
	FROM Book_Loans
	WHERE card_id = @card_id AND date_in IS NULL;

	DECLARE @book_borrowed_flag INT;

	SELECT @book_borrowed_flag = COUNT(*)
	FROM Book_Loans
	WHERE isbn = @isbn AND date_in IS NULL;

	DECLARE @fines_flag INT;

	SELECT @fines_flag = COUNT(*)
	FROM Fines as f
	JOIN Book_Loans as bl on bl.loan_id = f.loan_id
	JOIN Borrower as b on b.card_id = @card_id
	WHERE f.paid = 0;

	IF @num_borrowed > 2 THEN
		-- In this branch, the user has too many books on loan.
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A maximum of three books can be loaned at once.';
	ELSE
		IF @book_borrowed_flag > 0 THEN
			-- In this branch, the user is trying to check out a book that is already on loan.
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Another library member has already checked that book out.';
		ELSE
			IF @fines_flag > 0 THEN
				-- In this branch, the user has a fine and should be prohibited from checking out a book.
				SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Pay all fines before checking out another book.';
			ELSE
				-- In this branch, we insert in the Book_Loans table to update the checked out book.
				INSERT INTO Book_Loans (isbn, card_id, date_out, due_date)
				VALUES (@isbn, @card_id, CURRENT_DATE, DATEADD(day, 14, CURRENT_DATE));
			END IF;
		END IF;
	END IF;
END;

-- 3. Provide a checkin() function that satisfies the functional requirements in the documentation.
CREATE PROCEDURE checkin(
	-- Null definitions included to handle optional parameters.
	@isbn NUMERIC(13, 0) = NULL, 
	@card_id VARCHAR(20) = NULL,
	@bname_str VARCHAR(100) = NULL
	) AS
BEGIN
	IF @isbn IS NOT NULL THEN
		-- Preferred search uses the ISBN, creates one-to-one correspondence.
		UPDATE Book_Loans
		SET date_in = CURRENT_DATE
		WHERE isbn = @isbn AND date_in IS NULL;
	ELSE
		IF @card_id IS NOT NULL THEN
			-- Next most preferred search uses the user's card id, immediately identifies the set of borrowed books.
			UPDATE Book_Loans
			SET date_in = CURRENT_DATE
			WHERE card_id = @card_id AND date_in IS NULL;
		ELSE
			IF @bname_str IS NOT NULL THEN
				-- Least preferred search is using the user's name, may deliver erroneous results if inputs are not sufficient to uniquely identify a record.
				DECLARE @user_card_id VARCHAR(20);
				
				SELECT TOP 1 @user_card_id = bl.card_id
				FROM Book_Loans as bl
				JOIN Borrower as b on b.card_id = bl.card_id
				WHERE b.bname LIKE CONCAT('%', @bname_str, '%')
				ORDER BY bl.card_id ASC; -- Tiebreaker for ambiguous substrings (hence TOP 1 + order by).

				IF @user_card_id IS NULL
					-- In this branch, we found no names including the provided substring.
					SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No such names could be found. Try a different entry.';
				ELSE
					UPDATE Book_Loans
					SET date_in = CURRENT_DATE
					WHERE card_id = @user_card_id AND date_in IS NULL;
				END IF;
			ELSE
				-- In this branch, no parameters were provided.
				SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Please provide a search field for checking in a book.';
			END IF;
		END IF;
	END IF;
END;