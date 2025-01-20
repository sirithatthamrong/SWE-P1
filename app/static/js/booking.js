document.addEventListener("DOMContentLoaded", function () {
    fetchAvailableRooms();
    let today = new Date().toISOString().split("T")[0];
    document.getElementById("date").setAttribute("min", today);
});

let roomsPerPage = 12;
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

function confirmCancel(reservationId) {
    if (!confirm("Are you sure you want to cancel this booking?")) {
        return;
    }

    fetch(`/booking/cancel/${reservationId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("✅ Booking successfully canceled!");
            document.getElementById(`booking-${reservationId}`).remove();
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    })
    .catch(error => {
        console.error("Cancelation failed:", error);
        alert("❌ Unable to cancel booking. Please try again.");
    });
}