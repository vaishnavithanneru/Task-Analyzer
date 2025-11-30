# Smart Task Analyzer

Smart Task Analyzer is a Django + JS + Python + HTML + CSS app that computes priority scores for tasks using several strategies and offers "Top 3 for Today" suggestions.

## Features
- 4 scoring strategies: Smart Balance, Fastest Wins, High Impact, Deadline Driven
- Add / delete tasks (Django ORM)
- Re-scored public task list (public_tasks.html)
- "Top 3 for Today" suggestions endpoint
- Small single-file frontend served by Django

## Quick start (Windows)
1. Clone
   ```
   git clone https://github.com/vaishnavithanneru/Smart-Task-Analyzer.git
   cd Task-Analyzer
   ```
2. Create & activate venv
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install
   ```
   pip install -r requirements.txt
   ```
4. Migrate & run
   ```
   python manage.py migrate
   python manage.py runserver
   ```
5. Open browser:
   - App: http://127.0.0.1:8000/
   - Public tasks: http://127.0.0.1:8000/public-tasks/

## Important API endpoints
- GET /api/tasks/all/ — all saved tasks
- POST /api/tasks/create/ — create task (JSON body)
- POST /api/tasks/analyze/ — returns tasks with computed score & explanation (accepts tasks array or {strategy, tasks})
- POST /api/tasks/suggest/ — returns top suggestions { today_suggestions: [...] }
- DELETE /api/tasks/delete/<id>/ — delete single task

## Public page / Top-3 troubleshooting
- The public page re-scores tasks server-side via calculate_priority_score in tasks/scoring.py.
- Top-3 uses POST /api/tasks/suggest/. Ensure frontend sends the tasks array (or {tasks: [...], strategy: "smart_balance"}) and that the suggest endpoint accepts both payload shapes (array or object). If Top-3 doesn't work:
  - Check browser console for JS errors.
  - Check Django server logs for 4xx/5xx errors.
  - Ensure the button has id="public-top3-btn" (or linked to suggestToday) and that public_script.js is included.
  - Hard refresh (Ctrl+F5) to clear cached JS.

## Development notes
- Strategy is passed as `strategy` query param or body value; default is `smart_balance`.
- calculate_priority_score returns {"score": float, "explanation": str} — the frontend displays these values.
- The suggest endpoint sorts tasks by score and returns top 3 with rank, title, why, and score.

## Contributing
Fork, create a branch, add tests, and open a PR.

smart-task-analyzer/

├─ backend/ (Django project)
│ ├─ tasks/
│ │ ├─ views.py
│ │ ├─ models.py
│ │ ├─ scoring.py
│ │ └─ serializers.py
│ ├─ manage.py
│ └─ ...django settings/apps...
├─ frontend/
│ ├─ index.html
│ ├─ public_tasks.html
│ ├─ script.js
│ └─ public_script.js
├─ docs/
│ ├─ explanation.md ← explanation file you mentioned
│ └─ screenshots/
│ ├─ screen1.png
│ └─ screen2.png
├─ requirements.txt
└─ README.md


## Docs & screenshots
- Put the detailed explanation you mentioned in docs/explanation.md. Example contents:
  - Purpose of the app
  - How scoring works (reference tasks/scoring.py)
  - How to change strategy and test Top-3 suggestions
- Save UI screenshots under docs/screenshots/ (PNG or JPG).


## License
See repository license file.
