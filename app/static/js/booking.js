document.addEventListener("DOMContentLoaded", function () {
    fetchAvailableRooms();
});

let roomsPerPage = 12;
let currentPage = 1;
let totalRooms = [];
let totalPages = 1;

function fetchAvailableRooms() {
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
    alert(`You selected room ID: ${roomId}`);
}
