# API Contract (Milestone 3)

All endpoints return JSON. Errors use: `{ "error": "message" }`.

## Search
- `GET /api/search?q=TEXT`
- Response: array of
  - `isbn` (string)
  - `title` (string)
  - `authors` (array of strings)
  - `checked_out` (boolean)
  - `borrower_id` (string|null)

## Checkout
- `POST /api/checkout`
- Body: `{ "isbn": "", "borrower_card_no": "" }`
- Rules: max 3 active loans per borrower; block if book already out; block if unpaid fines (team to enforce).
- Response: `{ "loan_id": number, "isbn": "", "card_no": "", "date_out": "YYYY-MM-DD", "due_date": "YYYY-MM-DD" }`

## Batch Checkout
- `POST /api/checkout/batch`
- Body: `{ "isbns": [], "borrower_card_no": "" }`
- Response: array of `{ "isbn": "", "status": "ok|error", "loan_id"?: number, "error"?: "" }`

## Checkin
- `POST /api/checkin`
- Body: `{ "loan_id": number }`
- Response: `{ "loan_id": number, "date_in": "YYYY-MM-DD" }`

## Borrower Creation
- `POST /api/borrowers`
- Body: `{ "ssn": "", "bname": "", "address": "", "phone": "" }`
- Rules: SSN unique; required ssn/bname/address; generate `card_no` as `ID######`.
- Response: `{ "card_no": "" }`

## Fines
- `POST /api/fines/refresh`
  - No body. Recompute fines at $0.25/day for late items; do not alter paid fines.
  - Response: `{ "refreshed": number }`
- `GET /api/fines?card_no=IDxxxxxx`
  - Response: array of `{ "card_no": "", "total_fines": number, "paid": 0|1 }`
- `POST /api/fines/pay`
  - Body: `{ "card_no": "" }`
  - Rules: allow only if all related loans are returned.
  - Response: `{ "paid": number }`

## Status Codes
- 200 for success, 4xx for validation/logic errors, 5xx for unexpected failures.

## Data Notes
- SQLite DB recommended; import CSVs from `Milestone3/demo/data/`.
- Dates use `YYYY-MM-DD`.

