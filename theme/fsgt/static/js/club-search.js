document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('clubSearch');
    const table = document.getElementById('clubTable');

    if (searchInput && table) {
        searchInput.addEventListener('input', function (e) {
            const searchTerm = e.target.value.toLowerCase().trim();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                // Get all text content from the row, including dropdown buttons
                const clubName = row.querySelector('td:first-child').textContent.toLowerCase();
                const contacts = Array.from(row.querySelectorAll('.dropdown-toggle'))
                    .map(btn => btn.textContent.toLowerCase());

                // Check if search term matches club name or any contact name
                const matchClub = clubName.includes(searchTerm);
                const matchContact = contacts.some(contact => contact.includes(searchTerm));

                // Show/hide row based on matches
                row.style.display = (matchClub || matchContact) ? '' : 'none';
            });
        });

        // Add clear search functionality
        searchInput.addEventListener('keyup', function (e) {
            if (e.key === 'Escape') {
                this.value = '';
                this.dispatchEvent(new Event('input'));
            }
        });
    }
});