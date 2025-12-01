const API = "/api/tasks/";  // ← This is your real API path

// Load all tasks from DB and calculate scores
async function loadTasks() {
    try {
        const res = await fetch(API);
        const tasks = await res.json();

        // Sort by score (highest first)
        tasks.sort((a, b) => (b.score || 0) - (a.score || 0));
        displayTasks(tasks);
    } catch (err) {
        document.getElementById("results").innerHTML = "<p style='color:#ff6b6b'>Failed to load tasks</p>";
    }
}

// Add new task
async function addTask() {
    const task = {
        title: document.getElementById("title").value.trim(),
        due_date: document.getElementById("due_date").value || null,
        estimated_hours: parseInt(document.getElementById("estimated_hours").value) || 1,
        importance: parseInt(document.getElementById("importance").value) || 5,
        dependencies: []
    };

    if (!task.title) {
        alert("Please enter a task title!");
        return;
    }

    await fetch(API + "add/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(task)
    });

    // Clear form
    document.getElementById("title").value = "";
    document.getElementById("due_date").value = "";
    document.getElementById("estimated_hours").value = "0";
    document.getElementById("importance").value = "0";

    loadTasks();
}

// Top 3 Today — FIXED!
async function suggestToday() {
    try {
        const res = await fetch(API);
        const tasks = await res.json();

        const top3 = tasks
            .sort((a, b) => (b.score || 0) - (a.score || 0))
            .slice(0, 3);

        const div = document.getElementById("suggestions");
        div.innerHTML = `
            <div class="card" style="background:#10b981; color:white; padding:25px; border-radius:20px; margin:25px 0;">
                <h2 style="margin-bottom:15px;">Top 3 Tasks for Today</h2>
                ${top3.map((t, i) => `
                    <div style="background:rgba(255,255,255,0.2); margin:12px 0; padding:18px; border-radius:15px; font-size:1.1rem;">
                        <strong>#${i+1} → ${t.title}</strong><br>
                        <em>Score: ${Math.round(t.score || 0)} • ${t.explanation || "High priority"}</em>
                    </div>
                `).join("")}
            </div>
        `;
    } catch (err) {
        alert("Failed to load suggestions");
    }
}

// Delete task
async function deleteTask(id) {
    if (confirm("Delete this task permanently?")) {
        await fetch(API + "delete/" + id + "/", { method: "DELETE" });
        loadTasks();
    }
}

// Clear all tasks
async function clearAllTasks() {
    if (!confirm("Delete ALL tasks permanently? This cannot be undone!")) return;

    const res = await fetch(API);
    const tasks = await res.json();
    for (const task of tasks) {
        await fetch(API + "delete/" + task.id + "/", { method: "DELETE" });
    }
    loadTasks();
    document.getElementById("suggestions").innerHTML = "";
}

// Display tasks
function displayTasks(tasks) {
    const container = document.getElementById("results");
    container.innerHTML = "";

    // Always show Clear All button
    container.innerHTML += `
        <div style="text-align:center; margin:20px 0;">
            <button onclick="clearAllTasks()" 
                    style="padding:14px 32px; background:#dc2626; color:white; border:none; border-radius:12px; font-weight:bold; font-size:16px; cursor:pointer;">
                Clear All Tasks
            </button>
        </div>
    `;

    if (tasks.length === 0) {
        container.innerHTML += `<h2 style="text-align:center; opacity:0.8; color:white; margin:40px 0;">No tasks yet. Add one above!</h2>`;
        return;
    }

    tasks.forEach(task => {
        const score = Math.round(task.score || 0);
        const level = score > 200 ? "high" : score > 100 ? "medium" : "low";

        const card = document.createElement("div");
        card.className = `task-card ${level}`;
        card.innerHTML = `
            <div class="score">${score}</div>
            <h3>${task.title}</h3>
            <p>Due: <strong>${task.due_date || "No deadline"}</strong> | 
               Effort: <strong>${task.estimated_hours}h</strong> | 
               Importance: <strong>${task.importance}/10</strong></p>
            <div class="explanation">${task.explanation || "Smart priority"}</div>
            <button onclick="deleteTask(${task.id})" class="delete-btn">Delete This Task</button>
        `;
        container.appendChild(card);
    });
}
// DELETE TASK — WORKS 100% & REFRESHES BOTH VIEWS
async function deleteTask(id) {
    if (!confirm("Delete this task permanently from database?")) {
        return;
    }

    try {
        const response = await fetch(API + "delete/" + id + "/", {
            method: "DELETE"
        });

        if (response.ok) {
            alert("Task deleted permanently!");
            loadTasks();  // Refresh main page

            // Optional: Also refresh the public database view if it's open
            if (window.opener) {
                window.opener.location.reload();
            }
        } else {
            alert("Failed to delete task");
        }
    } catch (err) {
        alert("Network error. Try again.");
    }
}
// Load on start
loadTasks();