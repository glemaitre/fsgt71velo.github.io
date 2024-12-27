document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('clubSearch');
    const clubTable = document.getElementById('clubTable');
    const tableRows = clubTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    // Add a CSS class that only affects main table rows
    const style = document.createElement('style');
    style.textContent = `
        #clubTable > tbody > tr.row-hidden {
            display: none !important;
        }
    `;
    document.head.appendChild(style);

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();

        Array.from(tableRows).forEach(row => {
            // Get text from the main cells
            const mainText = Array.from(row.children).map(cell => {
                const button = cell.querySelector('.btn-link');
                return button ? button.textContent : cell.textContent;
            }).join(' ');

            // Get text from dropdown content (addresses, phones, emails)
            const dropdownText = Array.from(row.querySelectorAll('.contact-info-table td'))
                .map(td => td.textContent)
                .join(' ');

            // Combine all text and search
            const fullText = (mainText + ' ' + dropdownText).toLowerCase();

            // Show/hide row based on search term
            if (fullText.includes(searchTerm)) {
                row.classList.remove('row-hidden');
            } else {
                row.classList.add('row-hidden');
            }
        });
    });
});
