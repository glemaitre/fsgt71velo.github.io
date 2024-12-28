document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('calendarSearch');
    const calendarTable = document.getElementById('calendarTable');
    const tableRows = calendarTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    // Add CSS for hiding rows
    const style = document.createElement('style');
    style.textContent = `
        #calendarTable > tbody > tr.row-hidden {
            display: none !important;
        }
    `;
    document.head.appendChild(style);

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();

        Array.from(tableRows).forEach(row => {
            // Skip header rows (those with colspan)
            if (row.querySelector('td[colspan]')) {
                return;
            }

            // Get text from all cells
            const rowText = Array.from(row.children)
                .map(cell => cell.textContent)
                .join(' ')
                .toLowerCase();

            // Show/hide row based on search term
            if (rowText.includes(searchTerm)) {
                row.classList.remove('row-hidden');
            } else {
                row.classList.add('row-hidden');
            }
        });
    });
});
