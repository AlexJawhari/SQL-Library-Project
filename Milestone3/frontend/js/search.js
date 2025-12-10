(() => {
  const api = window.demoApi;

  function renderResults(rows) {
    const tbody = document.getElementById('resultsBody');
    tbody.innerHTML = '';
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No results.</td></tr>';
      return;
    }
    rows.forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${row.isbn}</td>
        <td>${row.title}</td>
        <td>${(row.authors || []).join(', ')}</td>
        <td>${row.checked_out ? 'Yes' : 'No'}</td>
        <td>${row.borrower_id ?? ''}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  async function doSearch() {
    const q = document.getElementById('searchInput').value || '';
    const status = document.getElementById('searchStatus');
    status.textContent = 'Searching...';
    try {
      const rows = await api.searchBooks(q);
      renderResults(rows);
      status.textContent = `${rows.length} result(s).`;
    } catch (err) {
      status.textContent = `Error: ${err.message}`;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('searchBtn').addEventListener('click', doSearch);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') doSearch();
    });
  });
})();

