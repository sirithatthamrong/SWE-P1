document.addEventListener("DOMContentLoaded", function () {
    // Select the "Book" button
    const bookBtn = document.getElementById("book-btn");

    // Select all checkboxes
    const checkboxes = document.querySelectorAll("input[name='time_slot']");

    // Function to enable/disable the button
    function updateButtonState() {
        const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
        bookBtn.disabled = !anyChecked; // Enable if at least one slot is checked
    }

    // Add event listeners to all checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", updateButtonState);
    });

    // Form submission logic
    document.getElementById("booking-form").addEventListener("submit", function (e) {
        e.preventDefault(); // Prevent default form submission

        let selectedSlots = [];
        document.querySelectorAll("input[name='time_slot']:checked").forEach((checkbox) => {
            selectedSlots.push(checkbox.value);
        });

        if (selectedSlots.length === 0) {
            alert("⚠️ Please select at least one time slot.");
            return;
        }

        let formData = new FormData(this);
        formData.append("time_slots", JSON.stringify(selectedSlots));

        fetch(window.location.href, {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("✅ Booking confirmed!");
                window.location.href = "/booking"; // Redirect after successful booking
            } else {
                alert(`❌ Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("❌ Booking failed. Please try again.");
        });
    });
});


document.getElementById("date").addEventListener("change", function() {
    document.getElementById("book-btn").disabled = true;
});
