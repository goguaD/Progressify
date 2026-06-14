# Progressify

A bilingual (Georgian / English) fitness web platform with workout & meal planning, progress tracking, social features, challenges, BMI analysis, and an admin panel.

The project is split into two parts:

- **`backend/`** — FastAPI + SQLite (Python)
- **`frontend/`** — React + Vite (JavaScript)

Both must be running at the same time in **two separate terminals**.

---

## Features

- **Authentication** — JWT-based register/login; two-step signup (personal info + physical stats including age)
- **Workout plans** — browse, filter, rate, set active plan; 1RM tracking; strength-standard classification (Beginner → Elite)
- **Meal plans** — browse, filter, rate; full macro breakdown (calories, protein, carbs, fat, fibre, sugar)
- **Social feed** — trending & new workouts/meals, friends' PRs, muscle achievements, challenge results
- **Friends** — send/accept/reject requests, view friends list
- **Challenges** — H2H challenges between friends with deadlines and results
- **BMI analysis** — speedometer-style SVG gauge with 6 zones, healthy weight range, BMI Prime
- **Anatomy map** — interactive muscle map showing strength level per muscle group
- **Notifications** — friend requests, challenges, PRs, muscle achievements, admin reports
- **Online friends sidebar** — live list of who's currently active
- **Report system** — users report meals/workouts; admin reviews and acts on them
- **Admin panel** — manage users, delete content, review reports (admin-only nav link)
- **Dark / Light theme** — full theme switching
- **Georgian / English UI** — full i18n, switchable per-session and per-modal

---

## Prerequisites

- **Python 3.10 – 3.12** (`python3 --version`)
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

Expected output:

```
Uvicorn running on http://127.0.0.1:8000
✅ Admin user created: admin@progressify.ge / admin123
```

Verify by opening <http://localhost:8000/> — you should see `{"message": "Progressify API is running"}`.  
Interactive API docs: <http://localhost:8000/docs>

**Leave this terminal running.**

### 2. Frontend (Terminal #2)

Open a **new** terminal — do not close terminal #1.

```bash
cd frontend
npm install
npm run dev
```

Expected output:

```
VITE vX.X.X  ready in XXX ms
➜  Local:   http://localhost:5173/
```

Open <http://localhost:5173> in your browser.

---

## Daily use (after first-time setup)

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

> Use a different email when testing registration. The admin link appears in the top navigation bar only for admin accounts.

---

## Troubleshooting

### "რეგისტრაცია ვერ მოხერხდა" / error on registration

The backend is likely not running. Check terminal #1 and open <http://localhost:8000/>.

### `npm error ENOENT ... package.json` in `backend/`

You ran `npm` in the wrong folder. `npm` belongs in `frontend/`; `uvicorn` belongs in `backend/`.

### Port already in use

- **Backend (8000):** `uvicorn main:app --reload --port 8001` then update `baseURL` in `frontend/src/api/client.js`.
- **Frontend (5173):** Vite picks the next free port automatically.

### Reset the database

```bash
rm backend/progressify.db
```

The DB is recreated and re-seeded on next backend start.

### `bcrypt` / `pydantic-core` build errors

Make sure you're on Python 3.10–3.12 and the venv is active:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

---

## Project layout

```
Progressify/
├── backend/
│   ├── main.py                  # entry point
│   └── app/
│       ├── __init__.py          # FastAPI app, CORS, migrations, router registration
│       ├── models.py            # SQLAlchemy ORM models
│       ├── schemas.py           # Pydantic schemas
│       ├── database.py          # engine + session
│       ├── auth.py              # password hashing + JWT
│       ├── migrations.py        # forward-only schema migrations
│       ├── seed.py              # admin user seed
│       ├── routers/
│       │   ├── auth.py          # register, login
│       │   ├── users.py         # profile, avatar, admin endpoints
│       │   ├── workouts.py      # workout plans, 1RM, active plan
│       │   ├── meals.py         # meal plans, ratings, reports
│       │   ├── friends.py       # friend requests
│       │   ├── challenges.py    # H2H challenges
│       │   └── feed.py          # social feed, notifications, online friends
│       └── services/
│           ├── user_service.py
│           ├── workout_service.py
│           └── meal_service.py
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Home.jsx         # social feed
│       │   ├── Workouts.jsx
│       │   ├── MealPlans.jsx
│       │   ├── Friends.jsx
│       │   ├── Challenges.jsx
│       │   ├── Profile.jsx
│       │   ├── Admin.jsx        # admin-only
│       │   ├── Login.jsx
│       │   └── SignUp.jsx
│       ├── components/
│       │   ├── Header.jsx
│       │   ├── ReportModal.jsx
│       │   ├── workouts/        # WorkoutDetail, AddPlanToProfileModal, ...
│       │   ├── meals/           # MealDetail, ...
│       │   └── profile/         # BMIGauge.jsx, AnatomySection.jsx, ...
│       ├── contexts/
│       │   └── AppContext.jsx   # language, theme
│       ├── api/client.js        # axios instance (baseURL: http://localhost:8000)
│       └── i18n.js              # Georgian / English translation strings
└── README.md
```
