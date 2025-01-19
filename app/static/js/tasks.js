// tasks.js

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

    // Find the card
    const cardSelector = `.task-card[data-task-id="${taskId}"]`;
    const taskCard = document.querySelector(cardSelector);
    if (!taskCard) return;

    const taskName = taskCard.dataset.taskName;
    const taskDesc = taskCard.dataset.taskDesc;
    const taskDueDate = taskCard.dataset.dueDate;
    const taskPriority = taskCard.dataset.priority;
    const taskStatus = taskCard.dataset.status;

    // Fill modal info
    document.getElementById('modal-task-title').textContent = taskName;
    document.getElementById('modal-task-description').textContent = "Description: " + taskDesc;
    document.getElementById('modal-task-due-date').textContent = taskDueDate;
    document.getElementById('modal-task-priority').textContent = taskPriority;

    // Get the forms
    const acceptForm = document.getElementById('acceptForm');
    const completeForm = document.getElementById('completeForm');

    // Hide both by default
    acceptForm.style.display = 'none';
    completeForm.style.display = 'none';

    // If status == 'pending', show acceptForm and set action to /tasks/<id>/accept
    if (taskStatus === 'pending') {
        acceptForm.style.display = 'block';
        acceptForm.action = `/tasks/${taskId}/accept`;
    }

    // If status == 'in progress', show completeForm and set action to /tasks/<id>/complete
    if (taskStatus === 'in progress') {
        completeForm.style.display = 'block';
        completeForm.action = `/tasks/${taskId}/complete`;
    }

    modal.style.display = 'block';
}

function closeTaskModal() {
    document.getElementById('task-modal').style.display = 'none';
}