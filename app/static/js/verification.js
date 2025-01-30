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

function applyVerificationFilters() {
    const selectedRoles = Array.from(document.querySelectorAll('.filter-role:checked')).map(cb => cb.value.toLowerCase());
    const selectedDate = document.getElementById('filter-creation-date').value;

    document.querySelectorAll('.verification-table tbody tr').forEach(row => {
        const role = row.dataset.role.toLowerCase();
        const creationDate = row.dataset.creationDate;

        const roleMatch = selectedRoles.length === 0 || selectedRoles.includes(role);
        const dateMatch = !selectedDate || creationDate === selectedDate;

        row.style.display = (roleMatch && dateMatch) ? '' : 'none';
    });
}