document.addEventListener("DOMContentLoaded", function () {
    const approveButtons = document.querySelectorAll(".approve-btn");
    const rejectButtons = document.querySelectorAll(".reject-btn");

    approveButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            if (!confirm("Are you sure you want to approve this user?")) {
                event.preventDefault();
            }
        });
    });

    rejectButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            if (!confirm("Are you sure you want to reject this user?")) {
                event.preventDefault();
            }
        });
    });
});