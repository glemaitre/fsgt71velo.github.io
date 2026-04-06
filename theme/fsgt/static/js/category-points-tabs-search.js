document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('categoryPointsSearch');
    if (!searchInput) return;

    if (!document.getElementById('category-points-search-styles')) {
        const style = document.createElement('style');
        style.id = 'category-points-search-styles';
        style.textContent = `
            .category-points-table > tbody > tr.row-hidden {
                display: none !important;
            }
        `;
        document.head.appendChild(style);
    }

    function getActiveTable() {
        const pane = document.querySelector(
            '#categoryPointsTabContent .tab-pane.active'
        );
        if (!pane) return null;
        return pane.querySelector('table.category-points-table');
    }

    function filterActiveTable() {
        const table = getActiveTable();
        if (!table || !table.tBodies[0]) return;
        const term = searchInput.value.toLowerCase();
        const rows = table.tBodies[0].rows;
        Array.from(rows).forEach(function(row) {
            const text = row.textContent.toLowerCase();
            if (text.includes(term)) {
                row.classList.remove('row-hidden');
            } else {
                row.classList.add('row-hidden');
            }
        });
    }

    searchInput.addEventListener('input', filterActiveTable);

    const tabList = document.getElementById('categoryPointsTabs');
    if (tabList) {
        tabList.addEventListener('shown.bs.tab', filterActiveTable);
    }
});
