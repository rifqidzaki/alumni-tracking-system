/**
 * Alumni Tracking System - Main JavaScript
 */

// ─── Sidebar Toggle ────────────────────────────────────────

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');

    if (window.innerWidth <= 991) {
        sidebar.classList.toggle('show');
    } else {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
    }
}

// Close sidebar on mobile when clicking outside
document.addEventListener('click', function(e) {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.querySelector('.sidebar-toggle');

    if (window.innerWidth <= 991 && sidebar.classList.contains('show')) {
        if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
            sidebar.classList.remove('show');
        }
    }
});


// ─── Copy to Clipboard ─────────────────────────────────────

function copyQuery(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const text = el.textContent || el.innerText;
    navigator.clipboard.writeText(text).then(function() {
        // Show feedback
        const btn = el.closest('.query-card').querySelector('.btn-outline-primary');
        if (btn) {
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="bi bi-check2 me-1"></i> Tersalin!';
            btn.classList.remove('btn-outline-primary');
            btn.classList.add('btn-success');
            setTimeout(function() {
                btn.innerHTML = originalHTML;
                btn.classList.remove('btn-success');
                btn.classList.add('btn-outline-primary');
            }, 2000);
        }
    }).catch(function() {
        // Fallback
        const range = document.createRange();
        range.selectNodeContents(el);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        alert('Tekan Ctrl+C untuk menyalin query.');
    });
}


// ─── Auto-dismiss alerts ────────────────────────────────────

document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
