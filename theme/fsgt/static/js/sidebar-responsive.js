document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggleMobile = document.getElementById('sidebarToggleMobile');
    const sidebarShowMobile = document.getElementById('sidebarShowMobile');
    const sidebarTogglePersistent = document.getElementById('sidebarTogglePersistent');

    // Update toggle icon based on sidebar state
    function updateToggleIcon() {
        const icon = sidebarTogglePersistent.querySelector('i');
        if (sidebar.classList.contains('sidebar-collapsed')) {
            icon.classList.remove('fa-chevron-left');
            icon.classList.add('fa-chevron-right');
        } else {
            icon.classList.remove('fa-chevron-right');
            icon.classList.add('fa-chevron-left');
        }
    }

    // Persistent toggle handler (for desktop)
    sidebarTogglePersistent.addEventListener('click', function () {
        sidebar.classList.toggle('sidebar-collapsed');
        updateToggleIcon();
    });

    // Existing mobile handlers
    sidebarToggleMobile.addEventListener('click', function () {
        sidebar.classList.remove('show');
    });

    sidebarShowMobile.addEventListener('click', function () {
        sidebar.classList.add('show');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (event) {
        if (window.innerWidth < 1000) {
            const isClickInside = sidebar.contains(event.target) ||
                sidebarShowMobile.contains(event.target);
            if (!isClickInside && sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
            }
        }
    });
});
