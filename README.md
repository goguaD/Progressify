# Progressify

Progressify is a web application designed to support users in their fitness journey through workout planning, diet guidance, progress tracking, and simple social features.

The project is split into two parts:

- **`backend/`** — FastAPI + SQLite (Python)
- **`frontend/`** — React + Vite (JavaScript)

You need **both** running at the same time, in **two separate terminals**.

---

## Prerequisites

- **Python 3.10+** (`python3 --version`)
- **Node.js 18+** and **npm** (`node --version`, `npm --version`)
- **git**

---

## First-time setup

### 1. Backend (Terminal #1)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

You should see:

```
Uvicorn running on http://127.0.0.1:8000
✅ Admin user created: admin@progressify.ge / admin123
```

Verify it works by opening <http://localhost:8000/> in the browser — you should see `{"message": "Progressify API is running"}`. The interactive API docs live at <http://localhost:8000/docs>.

**Leave this terminal running.**

### 2. Frontend (Terminal #2)

Open a **new** terminal — do not close terminal #1.

```bash
cd frontend
npm install
npm run dev
```

You should see:

```
VITE vX.X.X  ready in XXX ms
➜  Local:   http://localhost:5173/
```

Open <http://localhost:5173> in your browser. You should be able to register, log in, and use the app.

---

## Daily use (after first-time setup)

You don't need to reinstall every time. Just start both servers.

### Terminal #1 — backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Terminal #2 — frontend

```bash
cd frontend
npm run dev
```

---

## Default admin account

The backend auto-seeds an admin user on first run:

- **Email:** `admin@progressify.ge`
- **Password:** `admin123`

> Note: this email is reserved for the seeded admin. Use a different email when testing the registration form.

---

## Troubleshooting

### "რეგისტრაცია ვერ მოხერხდა" / generic error on registration

This almost always means the backend is **not running**. Check terminal #1:

- Is `uvicorn` still running? If it crashed, scroll up to read the error.
- Open <http://localhost:8000/> in the browser. If it doesn't load, the backend is down.

### `npm error ENOENT ... package.json` in `backend/`

You ran an `npm` command in the wrong directory. `npm` belongs in `frontend/`. `python` / `uvicorn` belong in `backend/`.

### Port already in use

- **Backend (port 8000):** `uvicorn main:app --reload --port 8001` (then update `baseURL` in `frontend/src/api/client.js`).
- **Frontend (port 5173):** Vite will offer the next free port automatically.

### Reset the database

If the DB gets into a bad state, delete it — it will be recreated and reseeded on next backend start:

```bash
rm backend/progressify.db
```

### `bcrypt` / `passlib` errors at backend startup

Make sure the venv is active and dependencies are installed cleanly:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

---

## Project layout

```
progressify/
├── backend/
│   ├── main.py             # FastAPI app + routes
│   ├── auth.py             # password hashing + JWT
│   ├── database.py         # SQLAlchemy engine + session
│   ├── models.py           # ORM models
│   ├── schemas.py          # Pydantic schemas
│   ├── requirements.txt
│   └── progressify.db      # auto-generated SQLite DB (gitignored)
└── frontend/
    ├── src/
    │   ├── pages/          # Login, SignUp, Main
    │   ├── components/
    │   ├── contexts/
    │   ├── api/client.js   # axios instance, baseURL = http://localhost:8000
    │   └── i18n.js
    ├── index.html
    ├── package.json
    └── vite.config.js
```
