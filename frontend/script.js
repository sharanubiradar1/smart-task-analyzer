// ==================== Configuration ====================
const API_BASE_URL = 'http://localhost:8000/api/tasks';

// ==================== State Management ====================
const state = {
    tasks: [],
    currentStrategy: 'smart_balance',
    nextTaskId: 1
};

// Strategy descriptions
const strategyDescriptions = {
    smart_balance: 'Balances all factors (urgency, importance, effort, dependencies) for optimal prioritization.',
    fastest_wins: 'Prioritizes quick, low-effort tasks to help you build momentum with easy wins.',
    high_impact: 'Focuses on importance above all else, ensuring high-value work gets done first.',
    deadline_driven: 'Emphasizes due dates to ensure nothing slips through the cracks.'
};

// ==================== DOM Elements ====================
const elements = {
    strategySelect: document.getElementById('strategy-select'),
    strategyDescription: document.getElementById('strategy-description'),
    tabButtons: document.querySelectorAll('.tab-button'),
    taskForm: document.getElementById('task-form'),
    jsonInput: document.getElementById('json-input'),
    loadJsonBtn: document.getElementById('load-json-btn'),
    analyzeBtn: document.getElementById('analyze-btn'),
    suggestBtn: document.getElementById('suggest-btn'),
    clearBtn: document.getElementById('clear-btn'),
    loading: document.getElementById('loading'),
    errorDisplay: document.getElementById('error-display'),
    resultsSection: document.getElementById('results-section'),
    resultsContent: document.getElementById('results-content'),
    suggestionsSection: document.getElementById('suggestions-section'),
    suggestionsContent: document.getElementById('suggestions-content'),
    taskCount: document.getElementById('task-count'),
    taskItems: document.getElementById('task-items')
};

// ==================== Initialization ====================
function init() {
    setupEventListeners();
    updateStrategyDescription();
    updateTaskPreview();
}

function setupEventListeners() {
    // Strategy selection
    elements.strategySelect.addEventListener('change', handleStrategyChange);

    // Tab switching
    elements.tabButtons.forEach(button => {
        button.addEventListener('click', () => switchTab(button.dataset.tab));
    });

    // Form submission
    elements.taskForm.addEventListener('submit', handleTaskFormSubmit);

    // JSON import
    elements.loadJsonBtn.addEventListener('click', handleJsonImport);

    // Action buttons
    elements.analyzeBtn.addEventListener('click', handleAnalyzeTasks);
    elements.suggestBtn.addEventListener('click', handleSuggestTasks);
    elements.clearBtn.addEventListener('click', handleClearAll);
}

// ==================== Tab Management ====================
function switchTab(tabName) {
    // Update tab buttons
    elements.tabButtons.forEach(button => {
        button.classList.toggle('active', button.dataset.tab === tabName);
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
}

// ==================== Strategy Management ====================
function handleStrategyChange(e) {
    state.currentStrategy = e.target.value;
    updateStrategyDescription();
}

function updateStrategyDescription() {
    elements.strategyDescription.textContent = strategyDescriptions[state.currentStrategy];
}

// ==================== Task Management ====================
function handleTaskFormSubmit(e) {
    e.preventDefault();

    const title = document.getElementById('task-title').value.trim();
    const dueDate = document.getElementById('task-due-date').value;
    const estimatedHours = parseFloat(document.getElementById('task-hours').value);
    const importance = parseInt(document.getElementById('task-importance').value);
    const dependenciesInput = document.getElementById('task-dependencies').value.trim();

    // Parse dependencies
    let dependencies = [];
    if (dependenciesInput) {
        dependencies = dependenciesInput
            .split(',')
            .map(d => parseInt(d.trim()))
            .filter(d => !isNaN(d));
    }

    // Create task object
    const task = {
        task_id: state.nextTaskId++,
        title,
        due_date: dueDate,
        estimated_hours: estimatedHours,
        importance,
        dependencies
    };

    // Validate task
    const validation = validateTask(task);
    if (!validation.valid) {
        showError(validation.error);
        return;
    }

    // Add task to state
    state.tasks.push(task);

    // Reset form
    elements.taskForm.reset();

    // Update preview
    updateTaskPreview();

    // Clear any errors
    hideError();
}

function validateTask(task) {
    if (!task.title || task.title.length === 0) {
        return { valid: false, error: 'Task title is required' };
    }

    if (!task.due_date) {
        return { valid: false, error: 'Due date is required' };
    }

    if (task.estimated_hours < 0.1) {
        return { valid: false, error: 'Estimated hours must be at least 0.1' };
    }

    if (task.importance < 1 || task.importance > 10) {
        return { valid: false, error: 'Importance must be between 1 and 10' };
    }

    // Check for self-dependency
    if (task.dependencies.includes(task.task_id)) {
        return { valid: false, error: 'Task cannot depend on itself' };
    }

    return { valid: true };
}

function handleJsonImport() {
    const jsonText = elements.jsonInput.value.trim();

    if (!jsonText) {
        showError('Please enter JSON data');
        return;
    }

    try {
        const tasks = JSON.parse(jsonText);

        if (!Array.isArray(tasks)) {
            showError('JSON must be an array of tasks');
            return;
        }

        // Validate all tasks
        for (let i = 0; i < tasks.length; i++) {
            const task = tasks[i];
            
            // Ensure task_id exists
            if (!task.task_id) {
                task.task_id = state.nextTaskId++;
            } else {
                state.nextTaskId = Math.max(state.nextTaskId, task.task_id + 1);
            }

            // Ensure dependencies array exists
            if (!task.dependencies) {
                task.dependencies = [];
            }

            const validation = validateTask(task);
            if (!validation.valid) {
                showError(`Task ${i + 1}: ${validation.error}`);
                return;
            }
        }

        // Add all tasks
        state.tasks = tasks;
        updateTaskPreview();
        hideError();

        // Clear JSON input
        elements.jsonInput.value = '';

        // Switch to manual tab to show imported tasks
        switchTab('manual');

    } catch (error) {
        showError(`Invalid JSON: ${error.message}`);
    }
}

function updateTaskPreview() {
    elements.taskCount.textContent = state.tasks.length;

    if (state.tasks.length === 0) {
        elements.taskItems.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 20px;">No tasks added yet</p>';
        return;
    }

    elements.taskItems.innerHTML = state.tasks.map((task, index) => `
        <div class="task-item-preview">
            <div class="task-item-info">
                <strong>${task.title}</strong>
                <small>
                    Due: ${task.due_date} | 
                    ${task.estimated_hours}h | 
                    Importance: ${task.importance}/10
                    ${task.dependencies.length > 0 ? ` | Depends on: ${task.dependencies.join(', ')}` : ''}
                </small>
            </div>
            <button class="btn btn-danger" onclick="removeTask(${index})">Remove</button>
        </div>
    `).join('');
}

function removeTask(index) {
    state.tasks.splice(index, 1);
    updateTaskPreview();
}

function handleClearAll() {
    if (state.tasks.length === 0) {
        return;
    }

    if (confirm('Are you sure you want to clear all tasks?')) {
        state.tasks = [];
        state.nextTaskId = 1;
        updateTaskPreview();
        hideResults();
        hideSuggestions();
        hideError();
    }
}

// ==================== API Calls ====================
async function handleAnalyzeTasks() {
    if (state.tasks.length === 0) {
        showError('Please add at least one task to analyze');
        return;
    }

    showLoading();
    hideError();
    hideResults();
    hideSuggestions();

    try {
        const response = await fetch(`${API_BASE_URL}/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: state.tasks,
                strategy: state.currentStrategy
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to analyze tasks');
        }

        displayResults(data);

    } catch (error) {
        showError(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

async function handleSuggestTasks() {
    if (state.tasks.length === 0) {
        showError('Please add at least one task to get suggestions');
        return;
    }

    showLoading();
    hideError();
    hideResults();
    hideSuggestions();

    try {
        const response = await fetch(`${API_BASE_URL}/suggest/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: state.tasks,
                strategy: state.currentStrategy,
                limit: 3
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to get suggestions');
        }

        displaySuggestions(data);

    } catch (error) {
        showError(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// ==================== Display Functions ====================
function displayResults(data) {
    const tasks = data.tasks;

    elements.resultsContent.innerHTML = `
        <div style="margin-bottom: 20px; padding: 15px; background-color: var(--bg-color); border-radius: 8px;">
            <strong>Strategy:</strong> ${formatStrategyName(data.strategy)} | 
            <strong>Total Tasks:</strong> ${data.total_tasks}
        </div>
        ${tasks.map(task => createTaskCard(task)).join('')}
    `;

    elements.resultsSection.classList.remove('hidden');
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function createTaskCard(task) {
    const priorityClass = task.priority_level.toLowerCase();
    const scorePercentage = task.priority_score;

    return `
        <div class="task-card">
            <div class="task-card-header">
                <h3 class="task-title">${task.title}</h3>
                <span class="priority-badge ${priorityClass}">
                    ${getPriorityIcon(task.priority_level)} ${task.priority_level}
                </span>
            </div>
            
            <div class="task-card-body">
                <div class="task-details">
                    <div class="detail-item">
                        <span>📅</span>
                        <span><strong>Due:</strong> ${task.due_date}</span>
                    </div>
                    <div class="detail-item">
                        <span>⏱️</span>
                        <span><strong>Effort:</strong> ${task.estimated_hours} hours</span>
                    </div>
                    <div class="detail-item">
                        <span>⭐</span>
                        <span><strong>Importance:</strong> ${task.importance}/10</span>
                    </div>
                    <div class="detail-item">
                        <span>🔗</span>
                        <span><strong>Dependencies:</strong> ${task.dependencies.length || 'None'}</span>
                    </div>
                </div>

                <div class="task-explanation">
                    <strong>Why this priority:</strong> ${task.explanation}
                </div>

                <div class="score-bar-container">
                    <div class="score-bar-label">
                        <span>Priority Score</span>
                        <span><strong>${task.priority_score.toFixed(2)}</strong> / 100</span>
                    </div>
                    <div class="score-bar">
                        <div class="score-bar-fill" style="width: ${scorePercentage}%"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function displaySuggestions(data) {
    const suggestions = data.suggestions;

    elements.suggestionsContent.innerHTML = `
        <div style="margin-bottom: 20px; padding: 15px; background-color: #eff6ff; border-radius: 8px; border-left: 4px solid var(--info-color);">
            <strong>💡 Recommendation:</strong> Start with these tasks to maximize your productivity today.
        </div>
        ${suggestions.map((suggestion, index) => createSuggestionCard(suggestion, index + 1)).join('')}
    `;

    elements.suggestionsSection.classList.remove('hidden');
    elements.suggestionsSection.scrollIntoView({ behavior: 'smooth' });
}

function createSuggestionCard(suggestion, rank) {
    return `
        <div class="suggestion-card">
            <div class="suggestion-rank">${rank}</div>
            <h3 class="suggestion-title">${suggestion.title}</h3>
            
            <div class="task-details" style="margin-bottom: 15px;">
                <div class="detail-item">
                    <span>📅</span>
                    <span><strong>Due:</strong> ${suggestion.due_date}</span>
                </div>
                <div class="detail-item">
                    <span>⏱️</span>
                    <span><strong>Effort:</strong> ${suggestion.estimated_hours} hours</span>
                </div>
                <div class="detail-item">
                    <span>⭐</span>
                    <span><strong>Importance:</strong> ${suggestion.importance}/10</span>
                </div>
                <div class="detail-item">
                    <span>🎯</span>
                    <span><strong>Score:</strong> ${suggestion.priority_score.toFixed(2)}</span>
                </div>
            </div>

            <div class="suggestion-reason">
                <strong>Why this task?</strong><br>
                ${suggestion.reason}
            </div>

            <div class="action-items">
                <h4>✅ Action Items:</h4>
                <ul>
                    ${suggestion.action_items.map(item => `<li>${item}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
}

// ==================== Utility Functions ====================
function formatStrategyName(strategy) {
    const names = {
        smart_balance: 'Smart Balance',
        fastest_wins: 'Fastest Wins',
        high_impact: 'High Impact',
        deadline_driven: 'Deadline Driven'
    };
    return names[strategy] || strategy;
}

function getPriorityIcon(level) {
    const icons = {
        High: '🔴',
        Medium: '🟡',
        Low: '🟢'
    };
    return icons[level] || '⚪';
}

function showLoading() {
    elements.loading.classList.remove('hidden');
}

function hideLoading() {
    elements.loading.classList.add('hidden');
}

function showError(message) {
    elements.errorDisplay.innerHTML = `
        <h3>⚠️ Error</h3>
        <p>${message}</p>
    `;
    elements.errorDisplay.classList.remove('hidden');
    elements.errorDisplay.scrollIntoView({ behavior: 'smooth' });
}

function hideError() {
    elements.errorDisplay.classList.add('hidden');
}

function hideResults() {
    elements.resultsSection.classList.add('hidden');
}

function hideSuggestions() {
    elements.suggestionsSection.classList.add('hidden');
}

// ==================== Initialize App ====================
document.addEventListener('DOMContentLoaded', init);