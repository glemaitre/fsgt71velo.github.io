document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('licencesSearch');
    const licencesTable = document.getElementById('licencesTable');

    // Return early if elements don't exist
    if (!searchInput || !licencesTable) return;

    const tableRows = licencesTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    // Add a CSS class for hiding rows
    const style = document.createElement('style');
    style.textContent = `
        #licencesTable > tbody > tr.row-hidden {
            display: none !important;
        }
    `;
    document.head.appendChild(style);

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();

        Array.from(tableRows).forEach(row => {
            const nom = row.children[0].textContent.toLowerCase();
            const prenom = row.children[1].textContent.toLowerCase();
            const club = row.children[2].textContent.toLowerCase();
            const categorie = row.children[3].textContent.toLowerCase();

            // Show row if search term matches nom, prénom, club or category
            if (nom.includes(searchTerm) ||
                prenom.includes(searchTerm) ||
                club.includes(searchTerm) ||
                categorie.includes(searchTerm)) {
                row.classList.remove('row-hidden');
            } else {
                row.classList.add('row-hidden');
            }
        });
    });
});
