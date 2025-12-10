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
    async listFines(card_no) {
      return realFetch(`/fines?card_no=${encodeURIComponent(card_no)}`);
    },
    async payFines(card_no) {
      return realFetch('/fines/pay', { method: 'POST', body: JSON.stringify({ card_no }) });
    },
  };

  window.demoApi = api;
})();

