document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('[id^="no_expiry_"]').forEach(checkbox => {
        checkbox.addEventListener("change", function () {
            let itemId = this.id.replace("no_expiry_", "");
            let expiryInput = document.getElementById("exp_date_" + itemId);

            if (this.checked) {
                expiryInput.value = ""; // Clear input
                expiryInput.disabled = true; // Disable field
            } else {
                expiryInput.disabled = false; // Enable field
            }
        });
    });
});


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('[name="new_quantity"]').forEach(input => {
        input.addEventListener("input", function () {
            let row = this.closest("tr");
            let expiryInput = row.querySelector('[name="expiration_date"]');
            let hasExpiry = row.querySelector("td span").textContent.trim() === "Has Expiry";

            if (hasExpiry) {
                expiryInput.style.display = "inline-block";
                expiryInput.disabled = false;
            } else {
                expiryInput.style.display = "none";
                expiryInput.disabled = true;
            }
        });
    });
});