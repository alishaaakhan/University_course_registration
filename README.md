# University Course Registration System (UCRS)

Flask + MySQL + Bootstrap 5 admin application for managing students, courses,
faculty, departments and semester enrollments.

## 1. Prerequisites
- Python 3.10+
- MySQL Server 8.x (running locally or reachable over the network)

## 2. Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
copy .env.example .env       # Windows
cp .env.example .env         # macOS / Linux
# then edit .env with your real MySQL username/password

# 4. Create the database + tables + sample data
mysql -u root -p < database/schema.sql

# 5. Run the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## 3. Default login

| Username | Password  |
|----------|-----------|
| admin    | admin123  |

## 4. Project structure

```
ucrs_flask/
├── app.py                 # Application factory + entry point
├── config.py               # Reads DB credentials from .env
├── extensions.py            # db / login_manager instances
├── models.py                # SQLAlchemy ORM models
├── requirements.txt
├── .env.example
├── database/
│   └── schema.sql          # DDL + trigger + sample data
├── routes/
│   ├── auth.py              # login / logout
│   ├── dashboard.py
│   ├── students.py          # Student CRUD
│   ├── courses.py           # Course CRUD
│   ├── faculty.py           # Faculty CRUD (Permanent/Visiting)
│   ├── departments.py       # Department CRUD
│   └── enrollment.py        # Enrollment CRUD + seat-capacity check
├── templates/
│   ├── base.html             # Sidebar layout shared by all pages
│   ├── login.html
│   ├── dashboard.html
│   ├── students/  courses/  faculty/  departments/  enrollment/
│   │      list.html + form.html for each module
│   └── errors/ 404.html  500.html
└── static/
    ├── css/style.css
    └── js/script.js
```

## 5. Notes

- Bootstrap 5 and Bootstrap Icons are loaded from CDN, so an internet
  connection is needed the first time each page loads in the browser.
- The seat-capacity rule is enforced in **two** places: a friendly check in
  `routes/enrollment.py`, and the authoritative `trg_check_seat_capacity`
  trigger inside MySQL itself (see `database/schema.sql`), so it can't be
  bypassed even by a direct INSERT.
- Set `app.run(debug=True)` to `debug=False` in `app.py` before deploying
  anywhere public.
