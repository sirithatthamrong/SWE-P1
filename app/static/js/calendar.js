document.addEventListener("DOMContentLoaded", function () {
    if (typeof FullCalendar === "undefined") {
        console.error("❌ FullCalendar is not loaded! Check script order.");
        return;
    }

    console.log("✅ FullCalendar loaded successfully!");

    const calendarEl = document.getElementById("calendar");

    if (!calendarEl) {
        console.error("❌ Calendar element not found!");
        return;
    }

    console.log("Reservations Data:", reservations);
    console.log("Tasks Data:", tasks);

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek",
        },
        events: [
            // Add reservations
            ...reservations.map(res => ({
                title: `Room: ${res.room_name}`,
                start: `${res.date}T${res.start_time}`,
                end: `${res.date}T${res.end_time}`,
                color: "#007bff",
            })),

            // Add tasks
            ...tasks.map(task => ({
                title: `[Task] ${task.task_name}`,
                start: task.due_date,
                color: task.priority === "high" ? "red" :
                       task.priority === "medium" ? "orange" : "green"
            }))
        ],
        eventClick: function (info) {
            alert(`Title: ${info.event.title}\nDate: ${info.event.start.toISOString()}`);
        },
        themeSystem: "bootstrap",
    });

    calendar.render();
});
