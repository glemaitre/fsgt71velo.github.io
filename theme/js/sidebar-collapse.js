document.addEventListener('DOMContentLoaded', function() {
    // Function to handle collapse based on hash
    function handleCollapse(hash) {
        if (!hash) return;

        const collapseId = hash.substring(1); // Remove the # from the hash
        const collapseElement = document.getElementById(collapseId);
        if (collapseElement) {
            // Use Bootstrap's collapse method to expand the menu
            new bootstrap.Collapse(collapseElement, {
                show: true
            });
        }
    }

    // Handle initial page load with hash
    handleCollapse(window.location.hash);

    // Handle clicks on links with hashes
    document.addEventListener('click', function(e) {
        const target = e.target.closest('a');
        if (target && target.hash) {
            // Prevent default only if it's on the same page
            if (target.pathname === window.location.pathname) {
                e.preventDefault();
                handleCollapse(target.hash);
                // Update URL without triggering a page reload
                history.pushState(null, '', target.hash);
            } else {
                // For links to other pages, store the hash in sessionStorage
                sessionStorage.setItem('targetHash', target.hash);
            }
        }
    });

    // Check for stored hash from previous page
    const storedHash = sessionStorage.getItem('targetHash');
    if (storedHash) {
        handleCollapse(storedHash);
        sessionStorage.removeItem('targetHash');
    }
});
