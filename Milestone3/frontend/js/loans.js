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

  function renderCheckinResults(loans) {
    const tbody = document.getElementById('checkinResultsBody');
    const resultsDiv = document.getElementById('checkinResults');
    tbody.innerHTML = '';
    
    if (!loans || !loans.length) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No active loans found.</td></tr>';
      resultsDiv.style.display = 'block';
      return;
    }
    
    loans.forEach(loan => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${loan.loan_id}</td>
        <td>${loan.isbn}</td>
        <td>${loan.title || 'N/A'}</td>
        <td>${loan.card_id}</td>
        <td>${loan.borrower_name || 'N/A'}</td>
        <td>${loan.date_out}</td>
        <td>${loan.due_date}</td>
        <td><button class="btn btn-sm btn-success" onclick="checkinLoan(${loan.loan_id})">Checkin</button></td>
      `;
      tbody.appendChild(tr);
    });
    
    resultsDiv.style.display = 'block';
  }

  async function handleCheckinSearch() {
    const isbn = document.getElementById('checkinSearchIsbn')?.value.trim() || '';
    const card = document.getElementById('checkinSearchCard')?.value.trim() || '';
    const name = document.getElementById('checkinSearchName')?.value.trim() || '';
    
    setStatus('Searching...', 'primary');
    try {
      const loans = await api.searchCheckinLoans(isbn, card, name);
      renderCheckinResults(loans);
      setStatus(`Found ${loans.length} active loan(s).`, 'success');
    } catch (err) {
      setStatus(`Error: ${err.message}`, 'danger');
    }
  }

  window.checkinLoan = async function(loanId) {
    setStatus('Processing checkin...', 'primary');
    try {
      const res = await api.checkin(loanId);
      setStatus(`Checked in loan_id ${res.loan_id}.`, 'success');
      // Refresh search results
      await handleCheckinSearch();
    } catch (err) {
      setStatus(`Error: ${err.message}`, 'danger');
    }
  };

  async function handleCheckin() {
    const loanId = Number(document.getElementById('checkinLoanId').value.trim());
    if (!loanId) return setStatus('Loan ID is required.', 'danger');
    setStatus('Processing checkin...', 'primary');
    try {
      const res = await api.checkin(loanId);
      setStatus(`Checked in loan_id ${res.loan_id}.`, 'success');
      document.getElementById('checkinLoanId').value = '';
      // Refresh search results if visible
      const resultsDiv = document.getElementById('checkinResults');
      if (resultsDiv && resultsDiv.style.display === 'block') {
        await handleCheckinSearch();
      }
    } catch (err) {
      setStatus(`Error: ${err.message}`, 'danger');
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('checkoutBtn').addEventListener('click', handleCheckout);
    document.getElementById('batchBtn').addEventListener('click', handleBatch);
    document.getElementById('checkinBtn').addEventListener('click', handleCheckin);
    const searchBtn = document.getElementById('checkinSearchBtn');
    if (searchBtn) {
      searchBtn.addEventListener('click', handleCheckinSearch);
    }
  });
})();

