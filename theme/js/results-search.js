document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('resultsSearch');
    const resultsTable = document.getElementById('calendarTable');

    // Return early if elements don't exist
    if (!searchInput || !resultsTable) return;

    const tableRows = resultsTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

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

        // If search is empty, show all rows
        if (!searchTerm) {
            Array.from(tableRows).forEach(row => {
                row.classList.remove('row-hidden');
            });
            return;
        }

        let currentMonthHeader = null;
        let hasVisibleEvents = false;

        Array.from(tableRows).forEach(row => {
            const isMonthHeader = row.querySelector('td[colspan]');

            if (isMonthHeader) {
                currentMonthHeader = row;
                hasVisibleEvents = false;
                row.classList.add('row-hidden');
                return;
            }

            // Check event rows
            const rowText = Array.from(row.children)
                .map(cell => cell.textContent)
                .join(' ')
                .toLowerCase();

            if (rowText.includes(searchTerm)) {
                row.classList.remove('row-hidden');
                // Show the current month header if there's a match
                if (currentMonthHeader) {
                    currentMonthHeader.classList.remove('row-hidden');
                }
                hasVisibleEvents = true;
            } else {
                row.classList.add('row-hidden');
            }
        });
    });
});