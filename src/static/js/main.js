// DOM Elements
const taskList = document.getElementById('taskList');
const createTaskModal = document.getElementById('createTaskModal');
const editTaskModal = document.getElementById('editTaskModal');
const createTaskForm = document.getElementById('createTaskForm');
const editTaskForm = document.getElementById('editTaskForm');
const noTasksMessage = document.getElementById('noTasks');

// State
let tasks = [];
let isLoading = false;

// API Functions
async function fetchTasks() {
    try {
        setLoading(true);
        showLoadingIndicator();

        const searchParams = new URLSearchParams(window.location.search);
        const status = searchParams.get('status') || '';
        const priority = searchParams.get('priority') || '';
        const search = searchParams.get('search') || '';

        const queryParams = new URLSearchParams({
            ...(status && { status }),
            ...(priority && { priority }),
            ...(search && { search })
        });

        const response = await fetch(`/api/tasks/?${queryParams}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to fetch tasks');
        }

        tasks = await response.json();
        updateTaskStats();
        applyFilters();
    } catch (error) {
        console.error('Error fetching tasks:', error);
        showErrorMessage('Failed to load tasks. Please try again later.');
    } finally {
        setLoading(false);
        hideLoadingIndicator();
    }
}

async function createTask(event) {
    event.preventDefault();
    
    if (!validateForm(createTaskForm)) {
        return;
    }

    try {
        setLoading(true);
        const submitButton = createTaskForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        const formData = new FormData(createTaskForm);
        const task = Object.fromEntries(formData);

        const response = await fetch('/api/tasks/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(task),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to create task');
        }

        closeCreateTaskModal();
        createTaskForm.reset();
        await fetchTasks();
        showSuccessMessage('Task created successfully!');
    } catch (error) {
        console.error('Error creating task:', error);
        showErrorMessage(error.message || 'Failed to create task. Please try again.');
    } finally {
        setLoading(false);
        const submitButton = createTaskForm.querySelector('button[type="submit"]');
        submitButton.disabled = false;
    }
}

async function updateTask(event) {
    event.preventDefault();
    
    if (!validateForm(editTaskForm)) {
        return;
    }

    try {
        setLoading(true);
        const submitButton = editTaskForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        const taskId = document.getElementById('editTaskId').value;
        const formData = new FormData(editTaskForm);
        const task = Object.fromEntries(formData);

        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(task),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to update task');
        }

        closeEditTaskModal();
        await fetchTasks();
        showSuccessMessage('Task updated successfully!');
    } catch (error) {
        console.error('Error updating task:', error);
        showErrorMessage(error.message || 'Failed to update task. Please try again.');
    } finally {
        setLoading(false);
        const submitButton = editTaskForm.querySelector('button[type="submit"]');
        submitButton.disabled = false;
    }
}

function confirmDeleteTask() {
    const taskId = document.getElementById('editTaskId').value;
    const taskTitle = document.getElementById('editTitle').value;
    
    if (confirm(`Are you sure you want to delete the task "${taskTitle}"?`)) {
        deleteTask(taskId);
    }
}

async function deleteTask(taskId) {
    try {
        setLoading(true);
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to delete task');
        }

        closeEditTaskModal();
        await fetchTasks();
        showSuccessMessage('Task deleted successfully!');
    } catch (error) {
        console.error('Error deleting task:', error);
        showErrorMessage(error.message || 'Failed to delete task. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Loading and Error Handling
function setLoading(loading) {
    isLoading = loading;
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        if (!button.classList.contains('close')) {
            button.disabled = loading;
        }
    });
}

function showLoadingIndicator() {
    // Add loading class to task list
    taskList.classList.add('loading');
    taskList.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Loading tasks...</p>
        </div>
    `;
}

function hideLoadingIndicator() {
    // Remove loading class from task list
    taskList.classList.remove('loading');
}

function showErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-error';
    errorDiv.textContent = message;
    
    // Remove any existing alerts
    document.querySelectorAll('.alert').forEach(alert => alert.remove());
    
    // Insert error message at the top of the main content
    const mainContent = document.querySelector('main');
    mainContent.insertBefore(errorDiv, mainContent.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success';
    successDiv.textContent = message;
    
    // Remove any existing alerts
    document.querySelectorAll('.alert').forEach(alert => alert.remove());
    
    // Insert success message at the top of the main content
    const mainContent = document.querySelector('main');
    mainContent.insertBefore(successDiv, mainContent.firstChild);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Form Validation Functions
function validateField(field) {
    const feedback = field.parentElement.querySelector('.form-feedback');
    const charCount = field.parentElement.querySelector('.char-count');
    let isValid = true;
    let message = '';

    // Reset previous validation state
    field.classList.remove('is-valid', 'is-invalid');
    feedback.classList.remove('show');

    // Required field validation
    if (field.required && !field.value.trim()) {
        isValid = false;
        message = 'This field is required';
    }

    // Title validation
    if (field.id === 'title' || field.id === 'editTitle') {
        const minLength = parseInt(field.getAttribute('minlength'));
        const maxLength = parseInt(field.getAttribute('maxlength'));
        const length = field.value.trim().length;

        if (length > 0 && length < minLength) {
            isValid = false;
            message = `Title must be at least ${minLength} characters`;
        } else if (length > maxLength) {
            isValid = false;
            message = `Title cannot exceed ${maxLength} characters`;
        }
    }

    // Description character count
    if (field.id === 'description' || field.id === 'editDescription') {
        const maxLength = parseInt(field.getAttribute('maxlength'));
        const length = field.value.length;
        charCount.textContent = `${length}/${maxLength}`;

        if (length > maxLength) {
            isValid = false;
            message = `Description cannot exceed ${maxLength} characters`;
        }
    }

    // Status and Priority validation
    if (field.tagName === 'SELECT' && field.required && !field.value) {
        isValid = false;
        message = 'Please select an option';
    }

    // Update UI based on validation
    if (!isValid) {
        field.classList.add('is-invalid');
        feedback.textContent = message;
        feedback.classList.add('show');
    } else if (field.value.trim()) {
        field.classList.add('is-valid');
    }

    // Update submit button state
    const form = field.closest('form');
    const submitButton = form.querySelector('button[type="submit"]');
    submitButton.disabled = !form.checkValidity();

    return isValid;
}

function validateForm(form) {
    const fields = form.querySelectorAll('input, select, textarea');
    let isValid = true;

    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    return isValid;
}

// UI Functions
function updateTaskStats() {
    const stats = {
        total: tasks.length,
        todo: tasks.filter(t => t.status === 'todo').length,
        in_progress: tasks.filter(t => t.status === 'in_progress').length,
        completed: tasks.filter(t => t.status === 'completed').length
    };

    document.getElementById('totalTasks').textContent = stats.total;
    document.getElementById('todoTasks').textContent = stats.todo;
    document.getElementById('inProgressTasks').textContent = stats.in_progress;
    document.getElementById('completedTasks').textContent = stats.completed;
}

function applyFilters() {
    const statusFilter = document.getElementById('statusFilter').value;
    const priorityFilter = document.getElementById('priorityFilter').value;
    const sortBy = document.getElementById('sortBy').value;

    let filteredTasks = [...tasks];

    // Apply filters
    if (statusFilter) {
        filteredTasks = filteredTasks.filter(task => task.status === statusFilter);
    }
    if (priorityFilter) {
        filteredTasks = filteredTasks.filter(task => task.priority === priorityFilter);
    }

    // Apply sorting
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    
    switch (sortBy) {
        case 'created_desc':
            filteredTasks.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            break;
        case 'created_asc':
            filteredTasks.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
            break;
        case 'priority_desc':
            filteredTasks.sort((a, b) => priorityOrder[b.priority] - priorityOrder[a.priority]);
            break;
        case 'priority_asc':
            filteredTasks.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
            break;
    }

    renderTasks(filteredTasks);
}

function renderTasks(tasksToRender) {
    taskList.innerHTML = '';
    
    if (tasksToRender.length === 0) {
        noTasksMessage.style.display = 'block';
        return;
    }
    
    noTasksMessage.style.display = 'none';
    
    tasksToRender.forEach(task => {
        const taskCard = document.createElement('div');
        taskCard.className = 'task-card';
        taskCard.onclick = () => openEditTaskModal(task);
        
        taskCard.innerHTML = `
            <h3>${task.title}</h3>
            <p>${task.description || 'No description'}</p>
            <div class="badges">
                <span class="status-badge status-${task.status}">${formatStatus(task.status)}</span>
                <span class="priority-badge priority-${task.priority}">${formatPriority(task.priority)}</span>
            </div>
        `;
        
        taskList.appendChild(taskCard);
    });
}

function formatStatus(status) {
    return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatPriority(priority) {
    return priority.charAt(0).toUpperCase() + priority.slice(1);
}

function openCreateTaskModal() {
    createTaskModal.style.display = 'block';
}

function closeCreateTaskModal() {
    createTaskModal.style.display = 'none';
    createTaskForm.reset();
}

function openEditTaskModal(task) {
    document.getElementById('editTaskId').value = task.id;
    document.getElementById('editTitle').value = task.title;
    document.getElementById('editDescription').value = task.description || '';
    document.getElementById('editStatus').value = task.status;
    document.getElementById('editPriority').value = task.priority;
    editTaskModal.style.display = 'block';
}

function closeEditTaskModal() {
    editTaskModal.style.display = 'none';
    editTaskForm.reset();
}

// Event Listeners
window.onclick = function(event) {
    if (event.target === createTaskModal) {
        closeCreateTaskModal();
    }
    if (event.target === editTaskModal) {
        closeEditTaskModal();
    }
}

// Initial load
document.addEventListener('DOMContentLoaded', fetchTasks);
