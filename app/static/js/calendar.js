document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        },
        events: [
            // Add reservations
            ...reservations.map(res => ({
                title: "Room Reservation: " + res.room_name,
                start: `${res.date}T${res.start_time}`,
                end: `${res.date}T${res.end_time}`,
                color: "#007bff"
            })),

            // Add tasks
            ...tasks.map(task => ({
                title: task.task_name,
                start: task.due_date,
                color: task.priority === "high" ? "red" :
                       task.priority === "medium" ? "orange" : "green"
            }))
        ]
    });

    calendar.render();
});
