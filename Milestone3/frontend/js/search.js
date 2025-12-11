(() => {
  const api = window.demoApi;
  let selectedIsbns = new Set();
  let currentResults = [];

  function updateCheckoutSection() {
    const section = document.getElementById('checkoutSection');
    if (selectedIsbns.size > 0) {
      section.style.display = 'block';
    } else {
      section.style.display = 'none';
    }
  }

  function renderResults(rows) {
    currentResults = rows;
    const tbody = document.getElementById('resultsBody');
    tbody.innerHTML = '';
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No results.</td></tr>';
      selectedIsbns.clear();
      updateCheckoutSection();
      return;
    }
    rows.forEach(row => {
      const tr = document.createElement('tr');
      const isChecked = selectedIsbns.has(row.isbn);
      const isAvailable = !row.checked_out;
      tr.innerHTML = `
        <td>
          <input type="checkbox" class="form-check-input book-checkbox" 
                 data-isbn="${row.isbn}" 
                 ${isChecked ? 'checked' : ''} 
                 ${!isAvailable ? 'disabled' : ''}>
        </td>
        <td>${row.isbn}</td>
        <td>${row.title}</td>
        <td>${(row.authors || []).join(', ')}</td>
        <td>${row.checked_out ? 'Yes' : 'No'}</td>
        <td>${row.borrower_id ?? ''}</td>
      `;
      tbody.appendChild(tr);
    });
    
    // Add event listeners to checkboxes
    document.querySelectorAll('.book-checkbox').forEach(cb => {
      cb.addEventListener('change', function() {
        const isbn = this.getAttribute('data-isbn');
        if (this.checked) {
          selectedIsbns.add(isbn);
        } else {
          selectedIsbns.delete(isbn);
        }
        updateCheckoutSection();
      });
    });
    
    updateCheckoutSection();
  }

  async function doSearch() {
    const q = document.getElementById('searchInput').value || '';
    const status = document.getElementById('searchStatus');
    status.textContent = 'Searching...';
    try {
      const rows = await api.searchBooks(q);
      selectedIsbns.clear();
      renderResults(rows);
      status.textContent = `${rows.length} result(s).`;
    } catch (err) {
      status.textContent = `Error: ${err.message}`;
    }
  }

  async function handleCheckoutSelected() {
    const card = document.getElementById('checkoutCardFromSearch').value.trim();
    if (!card) {
      document.getElementById('checkoutStatus').textContent = 'Please enter a borrower card number.';
      document.getElementById('checkoutStatus').className = 'text-danger small mt-2';
      return;
    }
    
    if (selectedIsbns.size === 0) {
      document.getElementById('checkoutStatus').textContent = 'Please select at least one book.';
      document.getElementById('checkoutStatus').className = 'text-danger small mt-2';
      return;
    }
    
    const isbns = Array.from(selectedIsbns);
    const statusEl = document.getElementById('checkoutStatus');
    statusEl.textContent = 'Processing checkout...';
    statusEl.className = 'text-primary small mt-2';
    
    try {
      const results = await api.checkoutBatch(isbns, card);
      const successCount = results.filter(r => r.status === 'ok').length;
      const errorCount = results.filter(r => r.status === 'error').length;
      
      let message = `Checkout complete: ${successCount} succeeded`;
      if (errorCount > 0) {
        message += `, ${errorCount} failed`;
      }
      statusEl.textContent = message;
      statusEl.className = successCount > 0 ? 'text-success small mt-2' : 'text-danger small mt-2';
      
      // Clear selection and refresh search
      selectedIsbns.clear();
      document.getElementById('checkoutCardFromSearch').value = '';
      await doSearch();
    } catch (err) {
      statusEl.textContent = `Error: ${err.message}`;
      statusEl.className = 'text-danger small mt-2';
    }
  }

  function handleClearSelection() {
    selectedIsbns.clear();
    document.querySelectorAll('.book-checkbox').forEach(cb => {
      cb.checked = false;
    });
    updateCheckoutSection();
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('searchBtn').addEventListener('click', doSearch);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') doSearch();
    });
    document.getElementById('checkoutSelectedBtn').addEventListener('click', handleCheckoutSelected);
    document.getElementById('clearSelectionBtn').addEventListener('click', handleClearSelection);
  });
})();

