document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    
    // Form submission handler
    document.getElementById('taskForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const task = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            priority: document.getElementById('priority').value,
            status: 'todo'
        };

        try {
            const response = await fetch('/tasks/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(task)
            });

            if (response.ok) {
                document.getElementById('taskForm').reset();
                loadTasks();
            } else {
                alert('Error creating task');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error creating task');
        }
    });
});

async function loadTasks() {
    try {
        const response = await fetch('/tasks/');
        const tasks = await response.json();
        
        const taskList = document.getElementById('taskList');
        taskList.innerHTML = '';
        
        tasks.forEach(task => {
            const taskElement = createTaskElement(task);
            taskList.appendChild(taskElement);
        });
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading tasks');
    }
}

function createTaskElement(task) {
    const div = document.createElement('div');
    div.className = `list-group-item task-item priority-${task.priority}`;
    
    div.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <div class="task-title">${task.title}</div>
                <div class="task-description">${task.description || ''}</div>
                <span class="task-status">${task.status}</span>
            </div>
            <div class="task-actions">
                <button class="btn btn-sm btn-outline-primary" onclick="updateTaskStatus(${task.id})">
                    Update Status
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${task.id})">
                    Delete
                </button>
            </div>
        </div>
    `;
    
    return div;
}

async function updateTaskStatus(taskId) {
    const statuses = ['todo', 'in_progress', 'completed'];
    const task = await fetch(`/tasks/${taskId}`).then(r => r.json());
    const currentIndex = statuses.indexOf(task.status);
    const newStatus = statuses[(currentIndex + 1) % statuses.length];
    
    try {
        const response = await fetch(`/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...task,
                status: newStatus
            })
        });

        if (response.ok) {
            loadTasks();
        } else {
            alert('Error updating task');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error updating task');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadTasks();
        } else {
            alert('Error deleting task');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting task');
    }
}
