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

        // First pass: check events and month headers for matches
        Array.from(tableRows).forEach(row => {
            const isMonthHeader = row.querySelector('td[colspan]');

            if (isMonthHeader) {
                // Check if the month name matches the search
                const monthText = row.textContent.toLowerCase();
                if (monthText.includes(searchTerm)) {
                    row.classList.remove('row-hidden');
                    // If month matches, show all events in that month
                    let nextRow = row.nextElementSibling;
                    while (nextRow && !nextRow.querySelector('td[colspan]')) {
                        nextRow.classList.remove('row-hidden');
                        nextRow = nextRow.nextElementSibling;
                    }
                    return;
                }
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
