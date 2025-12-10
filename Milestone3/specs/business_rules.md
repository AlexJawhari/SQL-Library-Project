# Business Rules (Milestone 3)

## Loans
- Max 3 active loans per borrower (active = `date_in IS NULL`).
- On checkout: `date_out = today`, `due_date = today + 14 days`.
- A book already checked out (loan row with `date_in IS NULL`) cannot be checked out again.

## Borrowers
- SSN must be unique.
- Required fields: ssn, bname, address.
- Generate `card_no` as `ID######` (zero-padded).

## Fines
- Rate: $0.25 per day late.
- Returned late: fine = `(date_in - due_date) * $0.25`.
- Still out late: fine = `(today - due_date) * $0.25`.
- Refresh should not overwrite paid fines (keep `paid = 1` intact).
- Pay fines only when all loans for that borrower are returned.
- Display fines grouped by card_no with summed total per borrower.

## Data
- Use SQLite (single file) fed from CSVs in `Milestone3/demo/data/` (copied from Milestone1).
- Keep schema compatible with provided sample SQL in Milestone2; OK to extend if needed while honoring these rules.

