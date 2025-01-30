document.addEventListener("DOMContentLoaded", function () {
    fetchAvailableRooms();
    let today = new Date().toISOString().split("T")[0];
    document.getElementById("date").setAttribute("min", today);
});

let roomsPerPage = 16;
let currentPage = 1;
let totalRooms = [];
let totalPages = 1;

function fetchAvailableRooms() {
    const dateField = document.getElementById("date");

    if (!dateField.value) {
        dateField.style.border = "2px solid red";
        return;
    } else {
        dateField.style.border = "";
    }

    const formData = new FormData(document.getElementById("booking-form"));

    fetch('/booking', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        totalRooms = data.available_rooms;
        totalPages = Math.ceil(totalRooms.length / roomsPerPage);
        currentPage = 1; // Reset to first page
        displayRooms();
    });
}

function displayRooms() {
    let roomsContainer = document.getElementById("available-rooms");
    roomsContainer.innerHTML = "";

    let start = (currentPage - 1) * roomsPerPage;
    let end = start + roomsPerPage;
    let roomsToShow = totalRooms.slice(start, end);

    roomsToShow.forEach(room => {
        let roomElement = document.createElement("button");
        roomElement.classList.add("room-btn");
        roomElement.innerHTML = room.name;
        roomElement.onclick = function () {
            selectRoom(room.lab_room_id);
        };
        roomsContainer.appendChild(roomElement);
    });

    document.getElementById("page-number").innerText = `${currentPage} / ${totalPages}`;
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        displayRooms();
    }
}

function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        displayRooms();
    }
}

function selectRoom(roomId) {
    const selectedDate = document.getElementById("date").value;
    window.location.href = `/booking/room/${roomId}?date=${selectedDate}`;
}

let cancelId = null;

function confirmCancel(bookingId) {
    cancelId = bookingId;
    document.getElementById("confirmModal").style.display = "block";
}

function closeModal() {
    document.getElementById("confirmModal").style.display = "none";
}

function cancelBooking() {
    if (!cancelId) {
        console.error("No cancelId found.");
        return;
    }

    console.log("Canceling booking with ID:", cancelId); // Debugging

    fetch(`/booking/cancel/${cancelId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("Booking canceled successfully!"); // Debugging
            document.getElementById(`booking-${cancelId}`).remove();
            alert("Booking canceled successfully!");
        } else {
            console.error("Error:", data.error);
            alert("Failed to cancel booking.");
        }
        closeModal();
    })
    .catch(error => console.error("Error:", error));
}