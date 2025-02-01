document.addEventListener("DOMContentLoaded", function () {
    const searchBar = document.getElementById("search-bar");
    const applyFiltersButton = document.getElementById("apply-filters");
    const categoryFilters = document.querySelectorAll(".category-filter");
    const inventoryTable = document.getElementById("inventory-table");
    const tbody = inventoryTable.querySelector("tbody");
    const mainRows = tbody.querySelectorAll("tr[data-name]"); // Get main item rows

    function filterItems() {
        const searchTerm = searchBar.value.toLowerCase().trim();

        // Get all selected category names
        const selectedCategories = Array.from(categoryFilters)
            .filter(filter => filter.checked)
            .map(filter => filter.nextElementSibling.textContent.toLowerCase().trim()); // Use category name

        mainRows.forEach(row => {
            const itemName = row.getAttribute("data-name").toLowerCase();
            const categoryName = row.children[1].textContent.toLowerCase().trim(); // Get category name from table

            const matchesSearch = searchTerm === "" || itemName.includes(searchTerm);
            const matchesCategory = selectedCategories.length === 0 || selectedCategories.includes(categoryName);

            const shouldShow = matchesSearch && matchesCategory;
            row.style.display = shouldShow ? "" : "none";

            // Also hide/show batch rows immediately following the item row
            let batchRow = row.nextElementSibling;
            if (batchRow && !batchRow.hasAttribute("data-name")) {
                batchRow.style.display = shouldShow ? "" : "none";
            }
        });
    }

    applyFiltersButton.addEventListener("click", filterItems);
    searchBar.addEventListener("input", filterItems);
});
document.addEventListener("DOMContentLoaded", function () {
    const noExpiryCheckbox = document.getElementById("no_expiry");
    const expirationDateInput = document.getElementById("expiration_date");

    // Function to toggle expiry date input
    function toggleExpiryDate() {
        if (noExpiryCheckbox.checked) {
            expirationDateInput.value = "";  // Clear date
            expirationDateInput.disabled = true;
        } else {
            expirationDateInput.disabled = false;
        }
    }

    // Run once when the page loads
    toggleExpiryDate();

    // Attach event listener to checkbox
    noExpiryCheckbox.addEventListener("change", toggleExpiryDate);
});