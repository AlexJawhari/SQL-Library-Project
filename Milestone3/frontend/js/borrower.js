(() => {
  const api = window.demoApi;

  function setStatus(text, variant = 'muted') {
    const el = document.getElementById('borrowerStatus');
    el.className = `small text-${variant}`;
    el.textContent = text;
  }

  async function handleCreate() {
    const payload = {
      ssn: document.getElementById('ssn').value.trim(),
      bname: document.getElementById('bname').value.trim(),
      address: document.getElementById('address').value.trim(),
      phone: document.getElementById('phone').value.trim(),
    };
    if (!payload.ssn || !payload.bname || !payload.address) {
      return setStatus('SSN, name, and address are required.', 'danger');
    }
    setStatus('Creating borrower...', 'primary');
    try {
      const res = await api.createBorrower(payload);
      setStatus(`Created borrower ${res.card_id}.`, 'success');
    } catch (err) {
      setStatus(`Error: ${err.message}`, 'danger');
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('createBorrowerBtn').addEventListener('click', handleCreate);
  });
})();
