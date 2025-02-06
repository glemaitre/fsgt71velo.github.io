document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('doubleLicencesSearch');
    const licencesTable = document.getElementById('doubleLicencesTable');

    // Return early if elements don't exist
    if (!searchInput || !licencesTable) return;

    const tableRows = licencesTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    // Add a CSS class for hiding rows
    const style = document.createElement('style');
    style.textContent = `
        #doubleLicencesTable > tbody > tr.row-hidden {
            display: none !important;
        }
    `;
    document.head.appendChild(style);

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();

        Array.from(tableRows).forEach(row => {
            // Check all cells in the row
            const cells = Array.from(row.children);
            const rowText = cells.map(cell => cell.textContent.toLowerCase());

            // Show row if search term matches any cell content
            if (rowText.some(text => text.includes(searchTerm))) {
                row.classList.remove('row-hidden');
            } else {
                row.classList.add('row-hidden');
            }
        });
    });
});
