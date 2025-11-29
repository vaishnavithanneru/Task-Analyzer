const API = '/api/tasks';

async function addTask() {
  const task = {
    title: document.getElementById('title').value.trim(),
    due_date: document.getElementById('due_date').value || null,
    estimated_hours: parseInt(document.getElementById('estimated_hours').value) || 0,
    importance: parseInt(document.getElementById('importance').value),
    dependencies: []
  };

  if (!task.title) return alert("Enter a title!");

  await fetch(`${API}/create/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(task)
  });

  document.getElementById('title').value = '';
  document.getElementById('due_date').value = '';           // clears date completely
  document.getElementById('estimated_hours').value = '0';   // back to 2 hours
  document.getElementById('importance').value = '0';
  loadTasks();
}
function openPublicTasks() {
  // This opens the public page and forces a fresh reload (no cache!)
  window.open('/public-tasks/?t=' + Date.now(), '_blank');
}
// NEW: Clear All Tasks Button (visible even when empty)
async function clearAllTasks() {
  if (!confirm("Delete ALL tasks permanently?")) return;
  
  const res = await fetch(`${API}/all/`);
  const tasks = await res.json();
  
  for (const task of tasks) {
    await fetch(`${API}/delete/${task.id}/`, { method: 'DELETE' });
  }
  loadTasks();
}

async function deleteTask(id) {
  if (!confirm("Delete this task?")) return;
  await fetch(`${API}/delete/${id}/`, { method: 'DELETE' });
  loadTasks();
}

async function loadTasks() {
  const strategy = document.getElementById('strategy').value;
  const res = await fetch(`${API}/analyze/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify([])
  });

  const tasks = await res.json();
  displayTasks(tasks);
}

function displayTasks(tasks) {
  const container = document.getElementById('results');
  container.innerHTML = '';

  // Always show "Clear All" button (even when empty)
  const clearBtn = document.createElement('div');
  clearBtn.style.textAlign = 'center';
  clearBtn.style.margin = '20px 0';
  clearBtn.innerHTML = `
    <button onclick="clearAllTasks()" 
            style="padding:12px 30px; background:#dc2626; color:white; border:none; border-radius:12px; font-weight:bold; cursor:pointer; font-size:16px;">
      Clear All Tasks
    </button>
  `;
  container.appendChild(clearBtn);

  if (tasks.length === 0) {
    container.innerHTML += '<h2 style="text-align:center; opacity:0.7; color:white;">No tasks yet. Add one above!</h2>';
    return;
  }

  tasks.forEach(task => {
    const score = Math.round(task.score);
    const level = score > 300 ? 'high' : score > 150 ? 'medium' : 'low';

    const card = document.createElement('div');
    card.className = `task-card ${level}`;
    card.innerHTML = `
      <div class="score">${score}</div>
      <h3>${task.title}</h3>
      <p>Due: <strong>${task.due_date || 'No deadline'}</strong> | 
         Effort: <strong>${task.estimated_hours}h</strong> | 
         Importance: <strong>${task.importance}/10</strong></p>
      <div class="explanation">${task.explanation}</div>

      <button onclick="deleteTask(${task.id})" class="delete-btn">
        Delete This Task
      </button>
    `;
    container.appendChild(card);
  });
}

async function suggestToday() {
  const res = await fetch(`${API}/all/`);
  const tasks = await res.json();
  const payload = tasks.map(t => ({ id: t.id, title: t.title, due_date: t.due_date, 
    estimated_hours: t.estimated_hours, importance: t.importance, dependencies: [] }));

  const sug = await fetch(`${API}/suggest/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await sug.json();

  const div = document.getElementById('suggestions');
  div.innerHTML = `<h2 style="text-align:center; margin:2rem 0; color:white;">Top 3 Tasks for Today</h2>`;
  data.today_suggestions.forEach(s => {
    div.innerHTML += `<div class="task-card high" style="margin:1rem 0; text-align:center">
      <h3>#${s.rank} ${s.title}</h3>
      <em style="color:#ddd">${s.why}</em>
    </div>`;
  });
}

loadTasks();