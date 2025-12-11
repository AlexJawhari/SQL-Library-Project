(() => {
  const api = window.demoApi;

  function setStatus(text, variant = 'muted') {
    const el = document.getElementById('finesStatus');
    el.className = `small text-${variant}`;
    el.textContent = text;
  }

  function renderFines(rows) {
    const tbody = document.getElementById('finesBody');
    tbody.innerHTML = '';
    if (!rows || !rows.length) {
      tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No data.</td></tr>';
      return;
    }
    rows.forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${row.card_no}</td>
        <td>$${Number(row.total_fines || 0).toFixed(2)}</td>
        <td>${row.paid ? 'Yes' : 'No'}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  async function handleRefresh() {
    setStatus('Refreshing fines...', 'primary');
    try {
      const res = await api.refreshFines();
      setStatus(`Refreshed fines (count ${res.refreshed ?? 'n/a'}).`, 'success');
    } catch (err) {
      setStatus(`Error: ${err.message}`, 'danger');
    }
  }

  async function handleList() {
    const card = document.getElementById('finesCard').value.trim();
    const showPaid = document.getElementById('showPaidFines')?.checked || false;
    setStatus('Listing fines...', 'primary');
    try {
      const rows = await api.listFines(card, showPaid);
      renderFines(rows);
      const cardText = card || 'all borrowers';
      setStatus(`Listed fines for ${cardText}.`, 'success');
    } catch (err) {
      setStatus(`Error: ${err.message}`, 'danger');
    }
  }

  async function handlePay() {
    const card = document.getElementById('finesCard').value.trim();
    if (!card) return setStatus('Card number is required to pay fines.', 'danger');
    setStatus('Paying fines...', 'primary');
    try {
      const res = await api.payFines(card);
      setStatus(`Paid ${res.paid ?? 0} fine(s).`, 'success');
      await handleList();
    } catch (err) {
      setStatus(`Error: ${err.message}`, 'danger');
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('refreshFinesBtn').addEventListener('click', handleRefresh);
    document.getElementById('listFinesBtn').addEventListener('click', handleList);
    document.getElementById('payFinesBtn').addEventListener('click', handlePay);
  });
})();

