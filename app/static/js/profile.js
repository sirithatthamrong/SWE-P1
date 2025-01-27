document.addEventListener("DOMContentLoaded", function () {
    const roleFilter = document.getElementById("role-filter");
    const tableBody = document.querySelector("#users-table tbody");
    const rows = Array.from(tableBody.querySelectorAll("tr"));
    const prevButton = document.getElementById("prev-page");
    const nextButton = document.getElementById("next-page");
    const pageInfo = document.getElementById("page-info");

    let currentPage = 1;
    const rowsPerPage = 15;

    function displayPage(page) {
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        rows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? "" : "none";
        });

        pageInfo.textContent = `Page ${page} of ${Math.ceil(rows.length / rowsPerPage)}`;
        prevButton.disabled = (page === 1);
        nextButton.disabled = (page === Math.ceil(rows.length / rowsPerPage));
    }

    function filterUsers() {
        const selectedRole = roleFilter.value.toLowerCase();
        const filteredRows = rows.filter(row => {
            const role = row.getAttribute("data-role").toLowerCase();
            return selectedRole === "all" || role === selectedRole;
        });

        // Hide all rows initially
        rows.forEach(row => row.style.display = "none");

        // Reset pagination and display first page of filtered results
        currentPage = 1;
        displayFilteredPage(filteredRows);
    }

    function displayFilteredPage(filteredRows) {
        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        filteredRows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? "" : "none";
        });

        pageInfo.textContent = `Page ${currentPage} of ${Math.ceil(filteredRows.length / rowsPerPage)}`;
        prevButton.disabled = (currentPage === 1);
        nextButton.disabled = (currentPage === Math.ceil(filteredRows.length / rowsPerPage));
    }

    prevButton.addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage--;
            displayPage(currentPage);
        }
    });

    nextButton.addEventListener("click", () => {
        if (currentPage < Math.ceil(rows.length / rowsPerPage)) {
            currentPage++;
            displayPage(currentPage);
        }
    });

    roleFilter.addEventListener("change", filterUsers);

    // Initialize pagination on page load
    displayPage(currentPage);
});