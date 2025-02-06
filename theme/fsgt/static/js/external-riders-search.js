document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('externalRidersSearch');
    const licencesTable = document.getElementById('externalRidersTable');

    // Return early if elements don't exist
    if (!searchInput || !licencesTable) return;

    const tableRows = licencesTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    // Add a CSS class for hiding rows
    const style = document.createElement('style');
    style.textContent = `
        #externalRidersTable > tbody > tr.row-hidden {
            display: none !important;
        }
    `;
    document.head.appendChild(style);

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();

        Array.from(tableRows).forEach(row => {
            // Get all cells including those that might be empty
            const cells = Array.from(row.getElementsByTagName('td'));
            const rowText = cells.map(cell => (cell.textContent || '').toLowerCase().trim());

            // Show row if search term matches any cell content
            if (rowText.some(text => text.includes(searchTerm))) {
                row.classList.remove('row-hidden');
            } else {
                row.classList.add('row-hidden');
            }
        });
    });
});
