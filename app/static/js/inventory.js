document.addEventListener("DOMContentLoaded", function () {
    const searchBar = document.getElementById("search-bar");
    const applyFiltersButton = document.getElementById("apply-filters");
    const categoryFilters = document.querySelectorAll(".category-filter");
    const filterAll = document.getElementById("filter-all");
    const inventoryTable = document.getElementById("inventory-table");
    const tbody = inventoryTable.querySelector("tbody");
    const mainRows = tbody.querySelectorAll("tr[data-name]"); // Only main item rows

    /**
     * Resets the visibility of all rows when the page loads
     */
    function resetVisibility() {
        mainRows.forEach(row => {
            row.style.display = ""; // Show all main rows
            let batchRow = row.nextElementSibling;
            if (batchRow && !batchRow.hasAttribute("data-name")) {
                batchRow.style.display = "";
            }
        });
    }

    /**
     * Filters inventory items based on search term and selected categories
     */
    function filterItems() {
        const searchTerm = searchBar.value.toLowerCase().trim();
        const selectedCategories = Array.from(categoryFilters)
            .filter(filter => filter.checked)
            .map(filter => filter.value);

        mainRows.forEach(row => {
            const itemName = row.getAttribute("data-name").toLowerCase();
            const categoryId = row.getAttribute("data-category");

            // Match conditions
            const matchesSearch = searchTerm === "" || itemName.includes(searchTerm);
            const matchesCategory = selectedCategories.length === 0 || selectedCategories.includes(categoryId);

            // Show/Hide row based on conditions
            const shouldShow = matchesSearch && matchesCategory;
            row.style.display = shouldShow ? "" : "none";

            // Hide/show batch rows accordingly
            let batchRow = row.nextElementSibling;
            if (batchRow && !batchRow.hasAttribute("data-name")) {
                batchRow.style.display = shouldShow ? "" : "none";
            }
        });
    }

    /**
     * Ensure category selection is correctly handled
     */
    categoryFilters.forEach(filter => {
        filter.addEventListener("change", function () {
            if (!this.checked) {
                filterAll.checked = false;
            }
            filterItems();
        });
    });

    /**
     * Handle "All Categories" checkbox behavior
     */
    filterAll.addEventListener("change", function () {
        categoryFilters.forEach(filter => {
            filter.checked = this.checked;
        });
        filterItems();
    });

    /**
     * Event Listeners
     */
    applyFiltersButton.addEventListener("click", filterItems);
    searchBar.addEventListener("input", filterItems);

    // Ensure page starts with full visibility
    resetVisibility();
});