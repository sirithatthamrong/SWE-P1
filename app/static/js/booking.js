document.addEventListener("DOMContentLoaded", function () {
    fetchAvailableRooms(); // Fetch all rooms when page loads
});

function fetchAvailableRooms() {
    const formData = new FormData(document.getElementById("booking-form"));

    fetch('/booking', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        let roomsContainer = document.getElementById("available-rooms");
        roomsContainer.innerHTML = "";

        if (data.available_rooms.length > 0) {
            data.available_rooms.forEach(room => {
                let roomElement = document.createElement("button");
                roomElement.textContent = room.name;
                roomElement.onclick = () => selectRoom(room.lab_room_id);
                roomsContainer.appendChild(roomElement);
            });
        } else {
            roomsContainer.innerHTML = "<p>No available rooms found.</p>";
        }
    });
}

function selectRoom(roomId) {
    alert(`You selected room ID: ${roomId}`);
}
