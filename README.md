# Breast Cancer ML - Landing, Auth, Dashboard

This patch adds a simple FastAPI web app to provide:
- Responsive landing page with navbar and mobile menu (Bootstrap)
- Register & Login pages with server-side and client-side validation
- SQLite (db.sqlite3) storage for users and records
- Dashboard showing user details
- Records page to add and view test inputs

Run locally
1. python -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. uvicorn app:app --reload

The app will create db.sqlite3 in the repo root on first run. The file is listed in .gitignore.
