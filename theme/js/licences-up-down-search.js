document.addEventListener('DOMContentLoaded', function() {
    // Setup search functionality for the single table
    setupSearch('categorySearch', 'categoryTable');
    // Setup category filters
    setupCategoryFilters();
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
        filterTable();
    });
}

function setupCategoryFilters() {
    const showUpgrades = document.getElementById('showUpgrades');
    const showDowngrades = document.getElementById('showDowngrades');

    if (!showUpgrades || !showDowngrades) return;

    showUpgrades.addEventListener('change', filterTable);
    showDowngrades.addEventListener('change', filterTable);
}

function filterTable() {
    const table = document.getElementById('categoryTable');
    const searchInput = document.getElementById('categorySearch');
    const showUpgrades = document.getElementById('showUpgrades');
    const showDowngrades = document.getElementById('showDowngrades');

    if (!table || !searchInput || !showUpgrades || !showDowngrades) return;

    const searchTerm = searchInput.value.toLowerCase();
    const tableRows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    Array.from(tableRows).forEach(row => {
        const cells = Array.from(row.children);
        const rowText = cells.map(cell => cell.textContent.toLowerCase());
        const matchesSearch = rowText.some(text => text.includes(searchTerm));

        const isUpgrade = row.classList.contains('category-up');
        const matchesFilter = (isUpgrade && showUpgrades.checked) ||
                            (!isUpgrade && showDowngrades.checked);

        if (matchesSearch && matchesFilter) {
            row.classList.remove('row-hidden');
        } else {
            row.classList.add('row-hidden');
        }
    });
}
