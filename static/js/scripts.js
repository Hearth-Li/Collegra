document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.delete-course').forEach(link => {
        link.addEventListener('click', (e) => {
            let confirmMessage = link.dataset.confirm;
            try {
                confirmMessage = JSON.parse(confirmMessage);
            } catch {
                // If not JSON, use the raw value
            }
            if (!confirm(confirmMessage)) {
                e.preventDefault();
            }
        });
    });
});