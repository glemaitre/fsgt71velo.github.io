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
            // Check if this is a month header row
            const isMonthHeader = row.querySelector('td[colspan]');

            if (isMonthHeader) {
                // If we were processing a previous month, hide/show its header based on visible events
                if (currentMonthHeader && !hasVisibleEvents) {
                    currentMonthHeader.classList.add('row-hidden');
                }
                // Reset for new month
                currentMonthHeader = row;
                hasVisibleEvents = false;
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
                hasVisibleEvents = true;
            } else {
                row.classList.add('row-hidden');
            }
        });

        // Handle the last month section
        if (currentMonthHeader && !hasVisibleEvents) {
            currentMonthHeader.classList.add('row-hidden');
        }
    });
});
