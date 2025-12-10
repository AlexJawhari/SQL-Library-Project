(() => {
  const api = window.demoApi;

  function setStatus(text, variant = 'muted') {
    const el = document.getElementById('loanStatus');
    el.className = `small text-${variant}`;
    el.textContent = text;
  }

  async function handleCheckout() {
    const isbn = document.getElementById('checkoutIsbn').value.trim();
    const card = document.getElementById('checkoutCard').value.trim();
    if (!isbn || !card) return setStatus('ISBN and card_no are required.', 'danger');
    setStatus('Processing checkout...', 'primary');
    try {
      const res = await api.checkout(isbn, card);
      setStatus(`Checked out loan_id ${res.loan_id} (due ${res.due_date}).`, 'success');
    } catch (err) {
      setStatus(`Error: ${err.message}`, 'danger');
    }
  }

  async function handleBatch() {
    const card = document.getElementById('batchCard').value.trim();
    const raw = document.getElementById('batchIsbns').value;
    const isbns = raw.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
    if (!card || !isbns.length) return setStatus('Card_no and at least one ISBN required.', 'danger');
    setStatus('Processing batch...', 'primary');
    try {
      const rows = await api.checkoutBatch(isbns, card);
      const summary = rows.map(r => `${r.isbn}: ${r.status}${r.loan_id ? ` (#${r.loan_id})` : r.error ? ` (${r.error})` : ''}`).join(' | ');
      setStatus(`Batch done. ${summary}`, 'success');
    } catch (err) {
      setStatus(`Error: ${err.message}`, 'danger');
    }
  }

  async function handleCheckin() {
    const loanId = Number(document.getElementById('checkinLoanId').value.trim());
    if (!loanId) return setStatus('Loan ID is required.', 'danger');
    setStatus('Processing checkin...', 'primary');
    try {
      const res = await api.checkin(loanId);
      setStatus(`Checked in loan_id ${res.loan_id}.`, 'success');
    } catch (err) {
      setStatus(`Error: ${err.message}`, 'danger');
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('checkoutBtn').addEventListener('click', handleCheckout);
    document.getElementById('batchBtn').addEventListener('click', handleBatch);
    document.getElementById('checkinBtn').addEventListener('click', handleCheckin);
  });
})();

