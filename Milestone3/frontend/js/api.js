(() => {
  const config = window.appConfig;

  async function realFetch(path, options = {}) {
    const res = await fetch(`${config.apiBase}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    const data = await res.json();
    if (!res.ok) {
      const message = data?.error || 'Request failed';
      throw new Error(message);
    }
    return data;
  }

  const api = {
    async searchBooks(query) {
      return realFetch(`/search?q=${encodeURIComponent(query)}`);
    },
    async checkout(isbn, card_no) {
      return realFetch('/checkout', { method: 'POST', body: JSON.stringify({ isbn, borrower_card_no: card_no }) });
    },
    async checkoutBatch(isbns, card_no) {
      return realFetch('/checkout/batch', { method: 'POST', body: JSON.stringify({ isbns, borrower_card_no: card_no }) });
    },
    async checkin(loan_id) {
      return realFetch('/checkin', { method: 'POST', body: JSON.stringify({ loan_id }) });
    },
    async createBorrower(payload) {
      return realFetch('/borrowers', { method: 'POST', body: JSON.stringify(payload) });
    },
    async refreshFines() {
      return realFetch('/fines/refresh', { method: 'POST' });
    },
    async listFines(card_no, showPaid = false) {
      const params = new URLSearchParams();
      if (card_no) params.append('card_no', card_no);
      if (showPaid) params.append('show_paid', 'true');
      return realFetch(`/fines?${params.toString()}`);
    },
    async searchCheckinLoans(isbn, card_no, borrower_name) {
      const params = new URLSearchParams();
      if (isbn) params.append('isbn', isbn);
      if (card_no) params.append('card_no', card_no);
      if (borrower_name) params.append('borrower_name', borrower_name);
      return realFetch(`/checkin/search?${params.toString()}`);
    },
    async payFines(card_no) {
      return realFetch('/fines/pay', { method: 'POST', body: JSON.stringify({ card_no }) });
    },
    // Admin endpoints
    async getAllBorrowers(search = '') {
      const params = search ? `?search=${encodeURIComponent(search)}` : '';
      return realFetch(`/admin/borrowers${params}`);
    },
    async getAllLoans(filter = 'all', search = '') {
      const params = new URLSearchParams();
      if (filter !== 'all') params.append('filter', filter);
      if (search) params.append('search', search);
      const query = params.toString() ? `?${params.toString()}` : '';
      return realFetch(`/admin/loans${query}`);
    },
    async getAllFines(filter = 'unpaid', search = '') {
      const params = new URLSearchParams();
      if (filter !== 'all') params.append('filter', filter);
      if (search) params.append('search', search);
      const query = params.toString() ? `?${params.toString()}` : '';
      return realFetch(`/admin/fines${query}`);
    },
    async getBookCount() {
      return realFetch('/admin/stats');
    },
    async applyFine(loanId, fineAmount = null, daysLate = null) {
      const body = { loan_id: loanId };
      if (fineAmount !== null) body.fine_amount = fineAmount;
      if (daysLate !== null) body.days_late = daysLate;
      return realFetch('/admin/fines/apply', { method: 'POST', body: JSON.stringify(body) });
    },
  };

  window.demoApi = api;
})();

