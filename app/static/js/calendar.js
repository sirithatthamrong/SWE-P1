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
        themeSystem: "bootstrap",
        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek",
        },
        eventDisplay: "block",
        eventTimeFormat: false,
        events: [
            // Add reservations
            ...reservations.map(res => ({
                title: `Room: ${res.room_name}`,
                start: `${res.date}T${res.start_time}`,
                end: `${res.date}T${res.end_time}`,
                color: "#7e71b5",
                textColor: "#fff",
                allDay: false
            })),

            // Add tasks
            ...tasks.map(task => {
                if (task.priority === "medium") {
                    return ({
                        title: `[Task] ${task.task_name}`,
                        start: task.due_date,
                        color: task.priority === "high" ? "#dc3545" :
                            "#ffc107",
                        textColor: "white",
                        allDay: true
                    });
                } else {
                    return ({
                        title: `[Task] ${task.task_name}`,
                        start: task.due_date,
                        color: task.priority === "high" ? "#dc3545" :
                            "#28a745",
                        textColor: "white",
                        allDay: true
                    });
                }
            })
        ],
        eventClick: function (info) {
            alert(`📌 Title: ${info.event.title}\n📅 Date: ${info.event.start.toISOString()}`);
        }
    });

    calendar.render();
});