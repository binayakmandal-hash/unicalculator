# UniCalc ✦

**Your all-in-one student calculator.** Grades, BMI, currency, attendance and banking, all in one Gen Z-styled Flask app.

🔗 **Live demo:** https://unicalculator.onrender.com

---

## Features

| Tool | What it does |
|---|---|
| 🎓 **Grade Calculator** | Add subjects with their own marks and "out of" (e.g. 42/50, 78/100). Shows each subject's grade plus total, percentage and overall grade. |
| ⚖️ **BMI Calculator** | US or metric units, age and gender. Shows BMI and category (adults 20+). |
| 💱 **Currency Converter** | Converts between 150+ world currencies using live exchange rates (refreshed hourly), with built-in backup rates if offline. |
| 📊 **Attendance Calculator** | Enter total and attended classes. Shows percentage and whether you meet the 75% requirement. |
| 🏦 **Mini Banking** | Demo account starting at ₹0. Deposit, withdraw and check balance. |

**Also:** light/dark mode, mobile-friendly layout, keyboard accessible, and respects reduced-motion settings.

## Grading scale

| Percentage | Grade |
|---|---|
| 90+ | A+ |
| 80 – 89 | A |
| 70 – 79 | B |
| 60 – 69 | C |
| 50 – 59 | D |
| Below 50 | F |

## Tech stack

- **Backend:** Python, Flask
- **Frontend:** HTML (Jinja2), CSS, vanilla JavaScript
- **Currency rates:** [open.er-api.com](https://open.er-api.com)
- **Hosting:** Render (Gunicorn)

## Project structure

```
unicalc/
├── app.py              # Flask app and all calculator logic
├── requirements.txt    # Flask, Gunicorn
├── Procfile            # start command for Render
├── static/
│   ├── style.css       # Gen Z neo-brutalist theme
│   └── script.js       # tabs, theme toggle, subject rows
└── templates/
    ├── index.html      # main page
    └── result.html     # result / error box
```

## Run it locally

```bash
git clone https://github.com/binayakmandal-hash/unicalculator.git
cd unicalculator
python -m venv venv
venv\Scripts\activate        # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000**.

## Deploy on Render

1. Push this repo to GitHub.
2. On Render: **New → Web Service** → pick this repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --workers 1 --bind 0.0.0.0:$PORT`

## Notes

- BMI results are educational only, not medical advice.
- Currency rates are for estimates, not real transactions.
- The banking tool is a demo: the balance is kept in memory, is shared by all visitors, and resets when the server restarts.

## Author

**Binayak Mandal**, BCA student
GitHub: [@binayakmandal-hash](https://github.com/binayakmandal-hash)
