function openTab(event, tabName) {
    const tabContents = document.querySelectorAll('.tab-content');
    const tabButtons = document.querySelectorAll('.tab-button');

    // Hide all tab contents and deactivate buttons
    tabContents.forEach(content => content.classList.remove('active'));
    tabButtons.forEach(button => button.classList.remove('active'));

    // Show selected tab and activate button
    document.getElementById(tabName).classList.add('active');
    event.currentTarget.classList.add('active');
}

function showTaskModal(taskId) {
    const modal = document.getElementById('task-modal');
    const cardSelector = `.task-card[data-task-id="${taskId}"]`;
    const taskCard = document.querySelector(cardSelector);
    if (!taskCard) return;

    const taskName = taskCard.dataset.taskName;
    const taskDesc = taskCard.dataset.taskDesc;
    const taskDueDate = taskCard.dataset.dueDate;
    const taskPriority = taskCard.dataset.priority;
    const taskStatus = taskCard.dataset.status;
    const isOwned = (taskCard.dataset.owned === 'true');

    // Fill modal info
    document.getElementById('modal-task-title').textContent = taskName;
    document.getElementById('modal-task-description').textContent = "Description: " + taskDesc;
    document.getElementById('modal-task-due-date').textContent = taskDueDate;
    document.getElementById('modal-task-priority').textContent = taskPriority;

    // Accept/Complete/Delete forms
    const acceptForm = document.getElementById('acceptForm');
    const completeForm = document.getElementById('completeForm');
    const deleteForm = document.getElementById('deleteForm');

    // Hide all forms by default
    acceptForm.style.display = 'none';
    completeForm.style.display = 'none';
    deleteForm.style.display = 'none';

    // Decide which tab param we want after each action:
    // 'my-tasks' if it's pending, 'in-progress' if it's in progress, etc.
    let afterAcceptTab = 'in-progress';   // e.g. user might want to see in-progress after acceptance
    let afterCompleteTab = 'completed';   // see completed tab after finishing
    let afterDeleteTab = 'my-creations';  // or wherever

    // If the task status is 'pending', show the accept form
    if (taskStatus === 'pending') {
        acceptForm.style.display = 'block';
        // Add ?tab=...
        acceptForm.action = `/tasks/${taskId}/accept?tab=${afterAcceptTab}`;
    }
    // If the task status is 'in progress', show the complete form
    if (taskStatus === 'in progress') {
        completeForm.style.display = 'block';
        completeForm.action = `/tasks/${taskId}/complete?tab=${afterCompleteTab}`;
    }
    // If the user owns the task, show the delete form
    if (isOwned) {
        deleteForm.style.display = 'block';
        deleteForm.action = `/tasks/${taskId}/delete?tab=${afterDeleteTab}`;
    }

    // Display the modal
    modal.style.display = 'block';
}

function closeTaskModal() {
    document.getElementById('task-modal').style.display = 'none';
}

// On DOM load, if there's an 'active_tab' from the server, open that tab:
document.addEventListener('DOMContentLoaded', () => {
    // The server passes "active_tab" into tasks.html (see next snippet).
    const currentTab = document.querySelector('body').getAttribute('data-active-tab');
    if (currentTab) {
        // simulate a click on the corresponding button
        const btn = document.querySelector(`.tab-button[onclick*="${currentTab}"]`);
        if (btn) {
            btn.click();
        }
    }
});

function completeTask(event, taskId) {
    event.stopPropagation(); // Prevents modal from opening when clicking the button
    fetch(`/tasks/${taskId}/complete`, {
        method: "POST",
        headers: {"Content-Type": "application/json"}
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert("Task marked as completed!");
                location.reload();
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => console.error("Error completing task:", error));
}

document.addEventListener("DOMContentLoaded", function () {
    let today = new Date().toISOString().split("T")[0];
    document.getElementById("filter-due-date").setAttribute("min", today);
});

function applyFilters() {
    let selectedTaskTypes = Array.from(document.querySelectorAll(".filter-task-type:checked")).map(cb => cb.value);
    let selectedPriorities = Array.from(document.querySelectorAll(".filter-priority:checked")).map(cb => cb.value);
    let selectedDueDate = document.getElementById("filter-due-date").value;

    document.querySelectorAll(".task-card").forEach(card => {
        let taskType = card.getAttribute("data-task-type").trim();
        let priority = card.getAttribute("data-priority");
        let dueDate = card.getAttribute("data-due-date");

        let show = (!selectedTaskTypes.length || selectedTaskTypes.includes(taskType)) &&
                   (!selectedPriorities.length || selectedPriorities.includes(priority)) &&
                   (!selectedDueDate || dueDate < selectedDueDate); // Change filter logic

        card.style.display = show ? "block" : "none";
    });
}