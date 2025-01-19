document.addEventListener("DOMContentLoaded", function () {
    const bookBtn = document.getElementById("book-btn");
    const checkboxes = document.querySelectorAll("input[name='time_slot']");

    function updateButtonState() {
        const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
        bookBtn.disabled = !anyChecked;
        bookBtn.style.opacity = anyChecked ? "1" : "0.6";
    }

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", updateButtonState);
    });

    document.getElementById("booking-form").addEventListener("submit", function (e) {
        e.preventDefault();

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
                window.location.href = "/booking";
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
