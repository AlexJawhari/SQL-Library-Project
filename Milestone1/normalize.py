#!/usr/bin/env python3
"""
normalize.py

Outputs (written to milestone1_output/):
 - book.csv           (isbn_primary,isbn10,isbn13,title)
 - authors.csv        (author_id,name)
 - book_authors.csv   (isbn_primary,author_id)  (empty author_id => NULL)
 - borrower.csv       (card_id,ssn,bname,address,phone)
 - bad_books_rows.csv (original book rows missing both isbn10 and isbn13)
 - normalization_log.txt
"""

import csv
import os
import re
import unicodedata
from collections import OrderedDict

# ---------- Config ----------
INPUT_BOOKS = "books.csv"
INPUT_BORROWERS = "borrowers.csv"
OUTPUT_DIR = "milestone1_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- Text normalization helpers ----------
def normalize_text(value):
    """Trim, normalize, remove common invisible chars, collapse whitespace."""
    if value is None:
        value = ""
    if not isinstance(value, str):
        value = str(value)
    v = value.strip()
    v = unicodedata.normalize("NFC", v)
    v = re.sub(r'[\u200b\u200c\u200d]', '', v)
    v = re.sub(r'\s+', ' ', v)
    return v

def normalize_title(raw):
    raw = normalize_text(raw)
    if raw == "":
        return ""
    return raw.title()

def normalize_person_name(raw):
    raw = normalize_text(raw)
    if raw == "":
        return ""
    raw = re.sub(r'^(by\s+)', '', raw, flags=re.I)
    raw = raw.strip(", ")
    s = raw.title()
    parts = s.split()
    for i, p in enumerate(parts):
        if len(p) == 1 and p.isalpha():
            parts[i] = p + "."
    return " ".join(parts)

# ---------- ISBN and author parsing ----------
def clean_isbn(raw):
    """Remove everything except digits and X/x; preserve leading zeros (return string)."""
    if raw is None:
        return ""
    s = normalize_text(raw)
    s = re.sub(r'[^0-9Xx]', '', s)
    return s

def split_author_field(raw):
    """
    Split an authors string into a list:
      - split on commas, semicolons, ' and ', '&'
      - drop obvious URLs and numeric noise
    """
    raw = normalize_text(raw)
    if raw == "":
        return []
    raw = re.sub(r'\s+&\s+', ',', raw)
    raw = re.sub(r'\s+and\s+', ',', raw, flags=re.I)
    raw = raw.replace(';', ',')
    parts = [p.strip() for p in raw.split(',') if p.strip()]
    out = []
    for p in parts:
        if re.search(r'http[s]?://', p):
            continue
        if re.match(r'^\d{3,}$', re.sub(r'\D', '', p)):
            continue
        out.append(p)
    return out

# ---------- CSV reading helpers ----------
def detect_delimiter(path, sample_lines=20):
    """Simple test to choose comma, tab or semicolon by frequency in a small sample."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        sample = ""
        for _ in range(sample_lines):
            try:
                sample += next(f)
            except StopIteration:
                break
    counts = {',': sample.count(','), '\t': sample.count('\t'), ';': sample.count(';')}
    # return the delimiter with max count (tie favors comma)
    return max(counts, key=counts.get)

def read_csv_rows(path):
    """Return (headers_list, rows_as_dicts, detected_delimiter)."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    delim = detect_delimiter(path)
    with open(path, "r", encoding="utf-8", errors="replace", newline='') as f:
        reader = csv.DictReader(f, delimiter=delim)
        headers = reader.fieldnames or []
        rows = [r for r in reader]
    return headers, rows, delim

# ---------- Column detection  ----------
def detect_book_columns(headers, rows):
    """
    Try to detect isbn10_col, isbn13_col, title_col, authors_col using header names and content.
    Returns tuple (isbn10_col, isbn13_col, title_col, authors_col).
    """
    isbn10_col = None
    isbn13_col = None
    title_col = None
    authors_col = None

    for h in headers:
        lh = h.lower()
        if 'isbn10' in lh or ('isbn' in lh and '10' in lh):
            isbn10_col = isbn10_col or h
        if 'isbn13' in lh or ('isbn' in lh and '13' in lh):
            isbn13_col = isbn13_col or h
        if 'title' in lh and title_col is None:
            title_col = h
        if 'author' in lh and authors_col is None:
            authors_col = h

    # quick content scan (first N rows)
    sample = rows[:200]
    counts = {h: {'len10': 0, 'len13': 0} for h in headers}
    for r in sample:
        for h in headers:
            val = clean_isbn(r.get(h, ""))
            if len(val) == 10:
                counts[h]['len10'] += 1
            elif len(val) == 13:
                counts[h]['len13'] += 1

    if isbn13_col is None:
        best = max(headers, key=lambda h: counts[h]['len13'])
        if counts[best]['len13'] > 5:
            isbn13_col = best
    if isbn10_col is None:
        best = max(headers, key=lambda h: counts[h]['len10'])
        if counts[best]['len10'] > 5:
            isbn10_col = best

    if title_col is None:
        for h in headers:
            if h not in (isbn10_col, isbn13_col):
                sample_vals = [normalize_text(r.get(h, "")) for r in rows[:100]]
                avg_len = sum(len(s) for s in sample_vals) / max(1, len(sample_vals))
                if any(' ' in s for s in sample_vals) and avg_len > 5:
                    title_col = h
                    break

    if authors_col is None:
        for h in headers:
            sample_vals = [r.get(h, "") for r in rows[:200]]
            comma_like = sum(1 for s in sample_vals if ',' in s)
            if comma_like > 0 and (sum(len(s) for s in sample_vals) / max(1, len(sample_vals))) < 200:
                authors_col = h
                break

    return isbn10_col, isbn13_col, title_col, authors_col

def detect_borrower_mapping(headers):
    """
    Map borrower columns to required output: card_id, ssn, bname, address, phone.
    Uses header name test, otherwise falls back to positional mapping.
    """
    mapping = {'card_id': None, 'ssn': None, 'bname': None, 'address': None, 'phone': None}
    for h in headers:
        hl = h.lower()
        if mapping['card_id'] is None and ('card' in hl or hl == 'id' or 'id0' in hl):
            mapping['card_id'] = h
        if mapping['ssn'] is None and 'ssn' in hl:
            mapping['ssn'] = h
        if mapping['bname'] is None and ('name' in hl or 'first_name' in hl or 'last_name' in hl):
            mapping['bname'] = h
        if mapping['address'] is None and ('address' in hl or 'addr' in hl):
            mapping['address'] = h
        if mapping['phone'] is None and ('phone' in hl or 'tel' in hl):
            mapping['phone'] = h

    # fallback positional
    if mapping['card_id'] is None and len(headers) > 0:
        mapping['card_id'] = headers[0]
    if mapping['ssn'] is None and len(headers) > 1:
        mapping['ssn'] = headers[1]
    if mapping['bname'] is None and len(headers) > 2:
        mapping['bname'] = headers[2]
    if mapping['address'] is None and len(headers) > 3:
        mapping['address'] = headers[3]
    if mapping['phone'] is None and len(headers) > 4:
        mapping['phone'] = headers[4]

    return mapping

# ---------- Main normalization logic ----------
def normalize_and_write():
    book_headers, book_rows, books_delim = read_csv_rows(INPUT_BOOKS)
    borrower_headers, borrower_rows, borrowers_delim = read_csv_rows(INPUT_BORROWERS)

    isbn10_col, isbn13_col, title_col, authors_col = detect_book_columns(book_headers, book_rows)

    books_out = []              # (isbn_primary, isbn10, isbn13, title)
    authors_map = OrderedDict() # name -> author_id (string)
    book_authors_out = []       # (isbn_primary, author_id_or_empty)
    bad_book_rows = []

    next_author_id = 1
    def get_author_id(name):
        nonlocal next_author_id
        if name in authors_map:
            return authors_map[name]
        aid = str(next_author_id)
        authors_map[name] = aid
        next_author_id += 1
        return aid

    # Process book rows
    for r in book_rows:
        raw10 = r.get(isbn10_col, "") if isbn10_col else ""
        raw13 = r.get(isbn13_col, "") if isbn13_col else ""
        clean10 = clean_isbn(raw10)
        clean13 = clean_isbn(raw13)

        valid10 = (len(clean10) == 10)
        valid13 = (len(clean13) == 13)

        # attempt to find isbn in other columns if necessary
        if not valid10 and not valid13:
            found = False
            for h in book_headers:
                cand = clean_isbn(r.get(h, ""))
                if len(cand) in (10, 13):
                    if len(cand) == 13:
                        clean13 = cand; valid13 = True
                    else:
                        clean10 = cand; valid10 = True
                    found = True
                    break
            if not found:
                bad_book_rows.append([r.get(h, "") for h in book_headers])
                continue

        # primary selection: prefer isbn13 when valid
        if valid13:
            primary_isbn = clean13
        elif valid10:
            primary_isbn = clean10
        else:
            primary_isbn = clean13 or clean10 or ""

        # Title
        title_raw = r.get(title_col, "") if title_col else ""
        if title_raw == "":
            for h in book_headers:
                if h not in (isbn10_col, isbn13_col) and r.get(h, "").strip():
                    title_raw = r.get(h, "")
                    break
        title = normalize_title(title_raw)

        books_out.append((primary_isbn, clean10, clean13, title))

        # Authors
        authors_field = r.get(authors_col, "") if authors_col else ""
        if not authors_field:
            for h in book_headers:
                v = r.get(h, "")
                if ',' in v and len(v) < 200:
                    authors_field = v
                    break

        parsed_authors = split_author_field(authors_field)
        if not parsed_authors:
            # preserve missing-author state explicitly using an empty author_id
            book_authors_out.append((primary_isbn, ""))
        else:
            for a in parsed_authors:
                a_norm = normalize_person_name(a)
                aid = get_author_id(a_norm)
                book_authors_out.append((primary_isbn, aid))

    # Process borrowers
    borrower_map = detect_borrower_mapping(borrower_headers)
    borrowers_out = []
    for r in borrower_rows:
        card = normalize_text(r.get(borrower_map['card_id'], ""))
        ssn = normalize_text(r.get(borrower_map['ssn'], ""))
        if 'first_name' in r and 'last_name' in r:
            bname = normalize_person_name((r.get('first_name','') + " " + r.get('last_name','')).strip())
        else:
            bname = normalize_person_name(r.get(borrower_map['bname'], "")) if borrower_map['bname'] else ""
        addr = normalize_text(r.get(borrower_map['address'], "")) if borrower_map['address'] else ""
        phone = normalize_text(r.get(borrower_map['phone'], "")) if borrower_map['phone'] else ""
        if card == "" and bname == "":
            continue
        borrowers_out.append((card, ssn, bname, addr, phone))

    # ---------- Write CSV outputs ----------
    book_path = os.path.join(OUTPUT_DIR, "book.csv")
    authors_path = os.path.join(OUTPUT_DIR, "authors.csv")
    book_authors_path = os.path.join(OUTPUT_DIR, "book_authors.csv")
    borrower_path = os.path.join(OUTPUT_DIR, "borrower.csv")
    bad_books_path = os.path.join(OUTPUT_DIR, "bad_books_rows.csv")
    log_path = os.path.join(OUTPUT_DIR, "normalization_log.txt")

    with open(book_path, "w", encoding="utf-8", newline='') as f:
        w = csv.writer(f)
        w.writerow(["isbn_primary", "isbn10", "isbn13", "title"])
        for row in books_out:
            w.writerow(row)

    with open(authors_path, "w", encoding="utf-8", newline='') as f:
        w = csv.writer(f)
        w.writerow(["author_id", "name"])
        for name, aid in sorted(authors_map.items(), key=lambda kv: int(kv[1])):
            w.writerow([aid, name])

    with open(book_authors_path, "w", encoding="utf-8", newline='') as f:
        w = csv.writer(f)
        w.writerow(["isbn_primary", "author_id"])
        for row in book_authors_out:
            w.writerow(row)

    with open(borrower_path, "w", encoding="utf-8", newline='') as f:
        w = csv.writer(f)
        w.writerow(["card_id", "ssn", "bname", "address", "phone"])
        for row in borrowers_out:
            w.writerow(row)

    with open(bad_books_path, "w", encoding="utf-8", newline='') as f:
        w = csv.writer(f)
        w.writerow(book_headers)
        for r in bad_book_rows:
            w.writerow(r)

    # ---------- Write a brief log ----------
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("Normalization log\n")
        f.write("=================\n\n")
        f.write("Decisions & policies:\n")
        f.write("- ISBNs preserved as strings; leading zeros kept; no int casts.\n")
        f.write("- Prefer ISBN-13 as primary when present; otherwise use ISBN-10.\n")
        f.write("- Missing author -> book_authors row with empty author_id (interpreted as NULL).\n")
        f.write("- Rows missing both ISBN10 and ISBN13 saved to bad_books_rows.csv.\n")
        f.write("- Author identity = exact spelling; no fuzzy merges.\n\n")
        f.write("Input summary:\n")
        f.write(f" - books file: {INPUT_BOOKS}\n - detected delimiter: {books_delim}\n")
        f.write(f" - borrowers file: {INPUT_BORROWERS}\n - detected delimiter: {borrowers_delim}\n\n")
        f.write("Output statistics:\n")
        f.write(f" - input book rows: {len(book_rows)}\n")
        f.write(f" - normalized book rows: {len(books_out)}\n")
        f.write(f" - unique author names: {len(authors_map)}\n")
        f.write(f" - book-author links: {len(book_authors_out)}\n")
        f.write(f" - bad book rows (no isbn): {len(bad_book_rows)}\n")

    print("Normalization finished. Files in:", OUTPUT_DIR)

if __name__ == "__main__":
    normalize_and_write()
