document.addEventListener('DOMContentLoaded', function() {
    // Setup search functionality for both tables
    setupSearch('upSearch', 'upDownCategoryTable');
    setupSearch('downSearch', 'downCategoryTable');
});

function setupSearch(searchInputId, tableId) {
    const searchInput = document.getElementById(searchInputId);
    const table = document.getElementById(tableId);

    // Return early if elements don't exist
    if (!searchInput || !table) return;

    const tableRows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    // Add a CSS class for hiding rows (if not already added)
    if (!document.getElementById('search-styles')) {
        const style = document.createElement('style');
        style.id = 'search-styles';
        style.textContent = `
            #${tableId} > tbody > tr.row-hidden {
                display: none !important;
            }
        `;
        document.head.appendChild(style);
    }

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
}
