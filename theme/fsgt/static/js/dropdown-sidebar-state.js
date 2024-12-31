document.addEventListener('DOMContentLoaded', function() {
    // Restore collapse states from localStorage
    const collapseElements = document.querySelectorAll('.collapse');
    collapseElements.forEach(collapse => {
        const id = collapse.id;
        const isExpanded = localStorage.getItem(`collapse_${id}`);
        if (isExpanded === 'true') {
            collapse.classList.add('show');
            // Update the button's aria-expanded attribute
            const button = document.querySelector(`[data-bs-target="#${id}"]`);
            if (button) {
                button.setAttribute('aria-expanded', 'true');
                button.classList.remove('collapsed');
            }
        }
    });

    // Add event listeners to store collapse states
    collapseElements.forEach(collapse => {
        collapse.addEventListener('shown.bs.collapse', function() {
            localStorage.setItem(`collapse_${this.id}`, 'true');
        });
        collapse.addEventListener('hidden.bs.collapse', function() {
            localStorage.setItem(`collapse_${this.id}`, 'false');
        });
    });
});
