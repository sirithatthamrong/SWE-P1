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
    const cardSelector = `.task-card[data-task-id="${taskId}"]`;
    const taskCard = document.querySelector(cardSelector);
    if (!taskCard) return;

    const taskName = taskCard.dataset.taskName;
    const taskDesc = taskCard.dataset.taskDesc;
    const taskDueDate = taskCard.dataset.dueDate;
    const taskPriority = taskCard.dataset.priority;
    const taskStatus = taskCard.dataset.status;
    // Determine ownership from the dataset
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

    // If the task status is 'pending', show the accept form
    if (taskStatus === 'pending') {
        acceptForm.style.display = 'block';
        acceptForm.action = `/tasks/${taskId}/accept`;
    }
    // If the task status is 'in progress', show the complete form
    if (taskStatus === 'in progress') {
        completeForm.style.display = 'block';
        completeForm.action = `/tasks/${taskId}/complete`;
    }
    // If the user owns the task, show the delete form
    if (isOwned) {
        deleteForm.style.display = 'block';
        deleteForm.action = `/tasks/${taskId}/delete`;
    }

    // Display the modal
    modal.style.display = 'block';
}

function closeTaskModal() {
    document.getElementById('task-modal').style.display = 'none';
}