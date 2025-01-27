document.addEventListener("DOMContentLoaded", function () {
    const roleFilter = document.getElementById("role-filter");

    function filterUsers() {
        const selectedRole = roleFilter.value.toLowerCase();

        document.querySelectorAll("#users-table tbody tr").forEach(row => {
            const role = row.getAttribute("data-role").toLowerCase();
            row.style.display = (selectedRole === "all" || role === selectedRole) ? "" : "none";
        });
    }

    roleFilter.addEventListener("change", filterUsers);

    // Initialize pagination on page load
    filterUsers();
});
