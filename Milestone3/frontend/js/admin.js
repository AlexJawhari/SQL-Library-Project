(() => {
  const api = window.demoApi;

  // Load stats on page load
  async function loadStats() {
    try {
      const [borrowers, loans, fines, books] = await Promise.all([
        api.getAllBorrowers(),
        api.getAllLoans('active'),
        api.getAllFines('unpaid'),
        api.getBookCount()
      ]);

      document.getElementById('statBorrowers').textContent = borrowers?.length || 0;
      document.getElementById('statActiveLoans').textContent = loans?.length || 0;
      document.getElementById('statUnpaidFines').textContent = fines?.length || 0;
      document.getElementById('statBooks').textContent = books?.count || 0;
    } catch (err) {
      console.error('Error loading stats:', err);
      // Set defaults if stats fail
      document.getElementById('statBorrowers').textContent = '?';
      document.getElementById('statActiveLoans').textContent = '?';
      document.getElementById('statUnpaidFines').textContent = '?';
      document.getElementById('statBooks').textContent = '?';
    }
  }

  // Borrowers section
  async function loadBorrowers(searchTerm = '') {
    const tbody = document.getElementById('borrowersBody');
    tbody.innerHTML = '<tr><td colspan="8" class="text-center">Loading...</td></tr>';

    try {
      console.log('Loading borrowers, searchTerm:', searchTerm);
      const borrowers = await api.getAllBorrowers(searchTerm);
      console.log('Borrowers loaded:', borrowers);
      
      if (!borrowers || borrowers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No borrowers found</td></tr>';
        return;
      }

      tbody.innerHTML = '';
      for (const borrower of borrowers) {
        const activeLoans = borrower.active_loans || 0;
        const unpaidFines = borrower.unpaid_fines || 0;
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${borrower.card_id}</strong></td>
          <td>${borrower.bname}</td>
          <td>${borrower.ssn}</td>
          <td>${borrower.address}</td>
          <td>${borrower.phone || '-'}</td>
          <td><span class="badge ${activeLoans > 0 ? 'bg-warning' : 'bg-success'}">${activeLoans}</span></td>
          <td>${unpaidFines > 0 ? `$${unpaidFines.toFixed(2)}` : '-'}</td>
          <td>
            <button class="btn btn-sm btn-primary" onclick="viewBorrowerDetails('${borrower.card_id}')">View</button>
            <button class="btn btn-sm btn-info" onclick="viewBorrowerLoans('${borrower.card_id}')">Loans</button>
          </td>
        `;
        tbody.appendChild(tr);
      }
    } catch (err) {
      console.error('Error loading borrowers:', err);
      tbody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">Error: ${err.message}<br><small>Check browser console (F12) for details</small></td></tr>`;
    }
  }

  // Loans section
  async function loadLoans(filter = 'all', searchTerm = '') {
    const tbody = document.getElementById('loansBody');
    tbody.innerHTML = '<tr><td colspan="10" class="text-center">Loading...</td></tr>';

    try {
      const loans = await api.getAllLoans(filter, searchTerm);
      
      if (!loans || loans.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center text-muted">No loans found</td></tr>';
        return;
      }

      tbody.innerHTML = '';
      for (const loan of loans) {
        const isActive = !loan.date_in;
        const isOverdue = isActive && new Date(loan.due_date) < new Date();
        const statusBadge = isActive 
          ? (isOverdue ? '<span class="badge bg-danger">Overdue</span>' : '<span class="badge bg-warning">Active</span>')
          : '<span class="badge bg-success">Returned</span>';
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${loan.loan_id}</td>
          <td>${loan.isbn}</td>
          <td>${loan.title || '-'}</td>
          <td><strong>${loan.card_id}</strong></td>
          <td>${loan.borrower_name || '-'}</td>
          <td>${loan.date_out}</td>
          <td class="${isOverdue ? 'text-danger fw-bold' : ''}">${loan.due_date}</td>
          <td>${loan.date_in || '-'}</td>
          <td>${statusBadge}</td>
          <td>
            <div class="btn-group btn-group-sm">
              ${isActive ? `<button class="btn btn-success" onclick="checkinLoan(${loan.loan_id})">Checkin</button>` : ''}
              <button class="btn btn-warning" onclick="showApplyFineModal(${loan.loan_id}, '${(loan.borrower_name || '').replace(/'/g, "\\'")}', '${(loan.title || '').replace(/'/g, "\\'")}', '${loan.due_date}')">Apply Fine</button>
            </div>
          </td>
        `;
        tbody.appendChild(tr);
      }
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="10" class="text-center text-danger">Error: ${err.message}</td></tr>`;
    }
  }

  // Fines section
  async function loadFines(filter = 'unpaid', searchTerm = '') {
    const tbody = document.getElementById('finesBody');
    tbody.innerHTML = '<tr><td colspan="10" class="text-center">Loading...</td></tr>';

    try {
      const fines = await api.getAllFines(filter, searchTerm);
      
      if (!fines || fines.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center text-muted">No fines found</td></tr>';
        return;
      }

      tbody.innerHTML = '';
      for (const fine of fines) {
        const daysLate = fine.days_late || 0;
        const paidBadge = fine.paid 
          ? '<span class="badge bg-success">Paid</span>' 
          : '<span class="badge bg-danger">Unpaid</span>';
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${fine.loan_id}</td>
          <td><strong>${fine.card_id}</strong></td>
          <td>${fine.borrower_name || '-'}</td>
          <td>${fine.isbn}</td>
          <td>${fine.title || '-'}</td>
          <td>${fine.due_date}</td>
          <td>${daysLate}</td>
          <td class="fw-bold">$${fine.fine_amt.toFixed(2)}</td>
          <td>${paidBadge}</td>
          <td>
            ${!fine.paid ? `<button class="btn btn-sm btn-success" onclick="payFineForBorrower('${fine.card_id}')">Pay All</button>` : '-'}
          </td>
        `;
        tbody.appendChild(tr);
      }
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="10" class="text-center text-danger">Error: ${err.message}</td></tr>`;
    }
  }

  // Global functions for buttons
  window.viewBorrowerDetails = function(cardId) {
    alert(`Borrower: ${cardId}\n\nUse the Loans tab to see their loans, or Fines tab to see their fines.`);
  };

  window.viewBorrowerLoans = function(cardId) {
    // Switch to loans tab and filter
    const loansTab = document.getElementById('loans-tab');
    const loansPane = document.getElementById('loans');
    loansTab.click();
    document.getElementById('loanSearch').value = cardId;
    setTimeout(() => {
      document.getElementById('searchLoansBtn').click();
    }, 100);
  };

  window.checkinLoan = async function(loanId) {
    if (!confirm('Check in this book?')) return;
    try {
      await api.checkin(loanId);
      alert('Book checked in successfully!');
      // Reload current view
      const filter = document.getElementById('loanFilter').value;
      const search = document.getElementById('loanSearch').value;
      await loadLoans(filter, search);
      await loadStats();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  window.payFineForBorrower = async function(cardId) {
    if (!confirm(`Pay all fines for borrower ${cardId}?`)) return;
    try {
      const result = await api.payFines(cardId);
      alert(`Paid ${result.paid} fine(s) successfully!`);
      // Reload current view
      const filter = document.getElementById('finesFilter').value;
      const search = document.getElementById('finesSearch').value;
      await loadFines(filter, search);
      await loadStats();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  // Event listeners
  document.addEventListener('DOMContentLoaded', () => {
    loadStats();

    // Borrowers
    document.getElementById('searchBorrowersBtn').addEventListener('click', () => {
      const search = document.getElementById('borrowerSearch').value.trim();
      loadBorrowers(search);
    });
    document.getElementById('showAllBorrowersBtn').addEventListener('click', () => {
      document.getElementById('borrowerSearch').value = '';
      loadBorrowers();
    });
    document.getElementById('borrowerSearch').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') document.getElementById('searchBorrowersBtn').click();
    });

    // Loans
    document.getElementById('searchLoansBtn').addEventListener('click', () => {
      const filter = document.getElementById('loanFilter').value;
      const search = document.getElementById('loanSearch').value.trim();
      loadLoans(filter, search);
    });
    document.getElementById('showAllLoansBtn').addEventListener('click', () => {
      const filter = document.getElementById('loanFilter').value;
      document.getElementById('loanSearch').value = '';
      loadLoans(filter);
    });
    document.getElementById('loanFilter').addEventListener('change', function() {
      loadLoans(this.value, document.getElementById('loanSearch').value.trim());
    });

    // Fines
    document.getElementById('refreshAllFinesBtn').addEventListener('click', async () => {
      try {
        await api.refreshFines();
        alert('Fines refreshed successfully!');
        const filter = document.getElementById('finesFilter').value;
        const search = document.getElementById('finesSearch').value.trim();
        await loadFines(filter, search);
        await loadStats();
      } catch (err) {
        alert(`Error: ${err.message}`);
      }
    });
    document.getElementById('showAllFinesBtn').addEventListener('click', () => {
      const filter = document.getElementById('finesFilter').value;
      document.getElementById('finesSearch').value = '';
      loadFines(filter);
    });
    const searchFinesBtn = document.getElementById('searchFinesBtn');
    if (searchFinesBtn) {
      searchFinesBtn.addEventListener('click', () => {
        const filter = document.getElementById('finesFilter').value;
        const search = document.getElementById('finesSearch').value.trim();
        loadFines(filter, search);
      });
    }
    document.getElementById('finesSearch').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        const filter = document.getElementById('finesFilter').value;
        const search = document.getElementById('finesSearch').value.trim();
        loadFines(filter, search);
      }
    });
    document.getElementById('finesFilter').addEventListener('change', function() {
      loadFines(this.value, document.getElementById('finesSearch').value.trim());
    });

    // Apply Fine Modal
    let currentLoanId = null;
    window.showApplyFineModal = function(loanId, borrowerName, title, dueDate) {
      currentLoanId = loanId;
      document.getElementById('applyFineLoanId').value = loanId;
      document.getElementById('applyFineBorrower').value = borrowerName || '-';
      document.getElementById('applyFineTitle').value = title || '-';
      document.getElementById('applyFineDueDate').value = dueDate || '-';
      document.getElementById('applyFineAmount').value = '';
      document.getElementById('applyFineDaysLate').value = '';
      document.getElementById('applyFineAuto').checked = true;
      const modal = new bootstrap.Modal(document.getElementById('applyFineModal'));
      modal.show();
    };

    document.getElementById('confirmApplyFineBtn').addEventListener('click', async function() {
      if (!currentLoanId) return;

      const fineAmount = document.getElementById('applyFineAmount').value.trim();
      const daysLate = document.getElementById('applyFineDaysLate').value.trim();
      const autoCalculate = document.getElementById('applyFineAuto').checked;

      let amount = null;
      let days = null;

      if (fineAmount) {
        amount = parseFloat(fineAmount);
        if (isNaN(amount) || amount <= 0) {
          alert('Please enter a valid fine amount greater than 0');
          return;
        }
      } else if (daysLate) {
        days = parseInt(daysLate);
        if (isNaN(days) || days <= 0) {
          alert('Please enter a valid number of days late');
          return;
        }
      } else if (!autoCalculate) {
        alert('Please choose a calculation method');
        return;
      }

      try {
        const result = await api.applyFine(currentLoanId, amount, days);
        alert(`Success! Fine applied: $${result.fine_amount.toFixed(2)}`);
        bootstrap.Modal.getInstance(document.getElementById('applyFineModal')).hide();
        // Refresh fines and loans
        const finesFilterEl = document.getElementById('finesFilter');
        const finesSearchEl = document.getElementById('finesSearch');
        const loanFilterEl = document.getElementById('loanFilter');
        const loanSearchEl = document.getElementById('loanSearch');
        
        if (finesFilterEl && finesSearchEl) {
          loadFines(finesFilterEl.value, finesSearchEl.value.trim());
        }
        if (loanFilterEl && loanSearchEl) {
          loadLoans(loanFilterEl.value, loanSearchEl.value.trim());
        }
      } catch (err) {
        alert(`Error: ${err.message}`);
      }
    });

    // Load initial data
    loadBorrowers();
  });
})();

