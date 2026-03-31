/* ============================================================
   OphtalmoClinique - JavaScript principal
   ============================================================ */

'use strict';

document.addEventListener('DOMContentLoaded', function () {

    // ============================================================
    // Auto-dismiss alerts after 5 seconds
    // ============================================================
    const autoDismissAlerts = document.querySelectorAll('.alert.alert-success, .alert.alert-info');
    autoDismissAlerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // ============================================================
    // Confirm dangerous actions
    // ============================================================
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(el.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // ============================================================
    // Sidebar mobile toggle
    // ============================================================
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function (e) {
            if (window.innerWidth <= 768 &&
                sidebar.classList.contains('show') &&
                !sidebar.contains(e.target) &&
                e.target !== sidebarToggle) {
                sidebar.classList.remove('show');
            }
        });
    }

    // ============================================================
    // Form validation: highlight invalid fields
    // ============================================================
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                // Scroll to first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalid.focus();
                }
            }
            form.classList.add('was-validated');
        });
    });

    // ============================================================
    // Tension oculaire: real-time alert indicator
    // ============================================================
    const tensionFields = document.querySelectorAll('input[id*="tension"]');
    tensionFields.forEach(function (field) {
        field.addEventListener('input', function () {
            const val = parseFloat(field.value);
            if (!isNaN(val)) {
                if (val < 10 || val > 21) {
                    field.classList.add('is-invalid');
                    field.classList.remove('is-valid');
                } else {
                    field.classList.add('is-valid');
                    field.classList.remove('is-invalid');
                }
            } else {
                field.classList.remove('is-valid', 'is-invalid');
            }
        });
    });

    // ============================================================
    // Patient search autocomplete (if search input exists)
    // ============================================================
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            const q = searchInput.value.trim();
            if (q.length >= 2) {
                searchTimeout = setTimeout(function () {
                    // Just submit the form for server-side search
                    // (could be enhanced with AJAX autocomplete)
                }, 300);
            }
        });
    }

    // ============================================================
    // Dynamic consultation loading for payment form
    // ============================================================
    const patientSelect = document.querySelector('select[name="patient"]');
    const consultationSelect = document.querySelector('select[name="consultation"]');

    if (patientSelect && consultationSelect) {
        patientSelect.addEventListener('change', function () {
            const patientId = this.value;
            const currentVal = consultationSelect.value;

            // Clear options
            consultationSelect.innerHTML = '<option value="">---------</option>';

            if (!patientId) return;

            fetch('/paiements/api/consultations/?patient_id=' + patientId, {
                credentials: 'same-origin'
            })
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    data.consultations.forEach(function (c) {
                        const opt = document.createElement('option');
                        opt.value = c.id;
                        opt.textContent = c.text;
                        if (String(c.id) === currentVal) opt.selected = true;
                        consultationSelect.appendChild(opt);
                    });
                })
                .catch(function () { /* silent fail */ });
        });
    }

    // ============================================================
    // Tooltips initialization
    // ============================================================
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    // ============================================================
    // Popovers initialization
    // ============================================================
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    popoverTriggerList.forEach(function (el) {
        new bootstrap.Popover(el);
    });

    // ============================================================
    // Date inputs: set max to today for birth dates
    // ============================================================
    const birthDateInputs = document.querySelectorAll('input[name="date_naissance"]');
    birthDateInputs.forEach(function (input) {
        const today = new Date().toISOString().split('T')[0];
        input.setAttribute('max', today);
    });

    // ============================================================
    // Calendar: highlight current time slot
    // ============================================================
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes() < 30 ? '00' : '30';
    const currentSlot = String(currentHour).padStart(2, '0') + ':' + currentMinute;

    document.querySelectorAll('.calendar-table tbody tr').forEach(function (row) {
        const timeCell = row.querySelector('td:first-child');
        if (timeCell && timeCell.textContent.trim() === currentSlot) {
            row.style.backgroundColor = 'rgba(13, 110, 253, 0.05)';
        }
    });

    // ============================================================
    // Print button handler
    // ============================================================
    document.querySelectorAll('[data-action="print"]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            window.print();
        });
    });

    // ============================================================
    // Copy to clipboard
    // ============================================================
    document.querySelectorAll('[data-copy]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const text = btn.dataset.copy;
            navigator.clipboard.writeText(text).then(function () {
                const original = btn.innerHTML;
                btn.innerHTML = '<i class="bi bi-check-lg"></i>';
                setTimeout(function () { btn.innerHTML = original; }, 1500);
            });
        });
    });

    // ============================================================
    // Prescription type tab switcher
    // ============================================================
    const typeButtons = document.querySelectorAll('[data-pres-type]');
    typeButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const type = btn.dataset.presType;
            const input = document.querySelector('input[name="type_prescription"]');
            if (input) input.value = type;
        });
    });

    // ============================================================
    // Clickable table rows (data-href attribute)
    // ============================================================
    document.querySelectorAll('tr[data-href]').forEach(function (row) {
        row.classList.add('clickable-row');
        row.addEventListener('click', function (e) {
            // Ne pas naviguer si on clique sur un lien ou bouton dans la ligne
            if (e.target.closest('a, button, form, input, select')) return;
            window.location.href = row.dataset.href;
        });
    });

    // ============================================================
    // Number inputs: prevent negative values
    // ============================================================
    document.querySelectorAll('input[type="number"][min="0"]').forEach(function (input) {
        input.addEventListener('change', function () {
            if (parseFloat(this.value) < 0) this.value = 0;
        });
    });

});

/* ============================================================
   Global utility functions
   ============================================================ */

/**
 * Format a number as currency (EUR)
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

/**
 * Format a date as French locale string
 */
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('fr-FR', {
        day: '2-digit', month: '2-digit', year: 'numeric'
    });
}

/**
 * Show a temporary toast notification
 */
function showToast(message, type) {
    type = type || 'info';
    const toast = document.createElement('div');
    toast.className = 'position-fixed bottom-0 end-0 p-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="toast show align-items-center text-bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>`;
    document.body.appendChild(toast);
    setTimeout(function () {
        toast.remove();
    }, 4000);
}
