import json
import math
import os
import time
import urllib.request
from itertools import zip_longest
from flask import Flask, render_template, request

app = Flask(__name__)

# ---------- Settings you can edit ----------

# (minimum percentage, grade). Checked from top to bottom.
GRADES = [(90, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D"), (0, "F")]

# Backup rates (how much you get for 1 INR), used only if live rates can't load.
FALLBACK_RATES = {
    "INR": 1, "USD": 0.012, "EUR": 0.011, "GBP": 0.0095, "JPY": 1.8, "AUD": 0.018,
    "CAD": 0.016, "CHF": 0.0105, "CNY": 0.085, "SGD": 0.0155, "AED": 0.044,
    "SAR": 0.045, "NPR": 1.6, "BDT": 1.4, "PKR": 3.3, "LKR": 3.6, "RUB": 1.1,
    "KRW": 16.5, "HKD": 0.093, "NZD": 0.02, "ZAR": 0.21, "BRL": 0.065, "THB": 0.4,
    "MYR": 0.052, "IDR": 190, "SEK": 0.12, "NOK": 0.125, "TRY": 0.45, "MXN": 0.22,
}

# Names shown in the dropdown. Codes not listed here just show the code.
CURRENCY_NAMES = {
    "INR": "Indian Rupee", "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound",
    "JPY": "Japanese Yen", "AUD": "Australian Dollar", "CAD": "Canadian Dollar",
    "CHF": "Swiss Franc", "CNY": "Chinese Yuan", "SGD": "Singapore Dollar",
    "AED": "UAE Dirham", "SAR": "Saudi Riyal", "NPR": "Nepalese Rupee",
    "BDT": "Bangladeshi Taka", "PKR": "Pakistani Rupee", "LKR": "Sri Lankan Rupee",
    "RUB": "Russian Ruble", "KRW": "South Korean Won", "HKD": "Hong Kong Dollar",
    "NZD": "New Zealand Dollar", "ZAR": "South African Rand", "BRL": "Brazilian Real",
    "THB": "Thai Baht", "MYR": "Malaysian Ringgit", "IDR": "Indonesian Rupiah",
    "SEK": "Swedish Krona", "NOK": "Norwegian Krone", "DKK": "Danish Krone",
    "TRY": "Turkish Lira", "MXN": "Mexican Peso", "PHP": "Philippine Peso",
    "VND": "Vietnamese Dong", "EGP": "Egyptian Pound", "NGN": "Nigerian Naira",
    "KES": "Kenyan Shilling", "QAR": "Qatari Riyal", "KWD": "Kuwaiti Dinar",
    "OMR": "Omani Rial", "BHD": "Bahraini Dinar", "BTN": "Bhutanese Ngultrum",
    "MVR": "Maldivian Rufiyaa", "AFN": "Afghan Afghani", "MMK": "Myanmar Kyat",
    "PLN": "Polish Zloty", "CZK": "Czech Koruna", "HUF": "Hungarian Forint",
    "ILS": "Israeli Shekel", "TWD": "Taiwan Dollar", "ARS": "Argentine Peso",
    "CLP": "Chilean Peso", "COP": "Colombian Peso", "PEN": "Peruvian Sol",
    "UAH": "Ukrainian Hryvnia", "KZT": "Kazakhstani Tenge", "IQD": "Iraqi Dinar",
    "IRR": "Iranian Rial", "JOD": "Jordanian Dinar", "MAD": "Moroccan Dirham",
}

# Live rates from a free API (no key needed), refreshed once an hour.
RATES_URL = "https://open.er-api.com/v6/latest/INR"
_rate_cache = {"rates": None, "time": 0, "live": False}


def get_rates():
    """Return (rates, is_live). Falls back to FALLBACK_RATES if offline."""
    if _rate_cache["rates"] and time.time() - _rate_cache["time"] < 3600:
        return _rate_cache["rates"], _rate_cache["live"]
    try:
        with urllib.request.urlopen(RATES_URL, timeout=4) as reply:
            data = json.load(reply)
        if data.get("result") != "success":
            raise ValueError("bad reply")
        rates, live = data["rates"], True
    except Exception:
        rates, live = FALLBACK_RATES, False
    _rate_cache.update(rates=rates, time=time.time(), live=live)
    return rates, live

REQUIRED_ATTENDANCE = 75      # percent
MAX_AMOUNT = 1_000_000_000    # biggest amount allowed, stops silly inputs

# Demo bank account. Lives in memory, so it resets when the server restarts.
account = {"balance": 0.0}

# Tabs shown on the page: (id, icon, name)
TABS = [
    ("grades", "🎓", "Grades"),
    ("bmi", "⚖️", "BMI"),
    ("currency", "💱", "Currency"),
    ("attendance", "📊", "Attendance"),
    ("bank", "🏦", "Banking"),
]


# ---------- Helper ----------

def get_number(field, label):
    """Read a number from the form. Raises ValueError with a friendly message."""
    raw = request.form.get(field, "").strip()
    if raw == "":
        raise ValueError(f"{label} is empty.")
    try:
        value = float(raw)
    except ValueError:
        raise ValueError(f"{label} must be a number.")
    if not math.isfinite(value):   # blocks 'nan' and 'inf'
        raise ValueError(f"{label} must be a real number.")
    return value


# ---------- The five tools ----------
# Each one returns a list of (label, value) rows to show on the page.

def get_grade(percent):
    for minimum, letter in GRADES:
        if percent >= minimum:
            return letter


def grades():
    names = request.form.getlist("subject")
    marks = request.form.getlist("mark")
    outs = request.form.getlist("outof")

    rows, total, total_out = [], 0.0, 0.0
    for i, (name, mark, out) in enumerate(zip_longest(names, marks, outs, fillvalue=""), start=1):
        name, mark, out = name.strip(), mark.strip(), out.strip()
        if not mark and not name:
            continue                      # skip empty rows
        name = name or f"Subject {i}"
        if not mark:
            raise ValueError(f"Enter marks for {name}.")
        try:
            got = float(mark)
            full = float(out or 100)
        except ValueError:
            raise ValueError(f"Marks for {name} must be numbers.")
        if not (math.isfinite(got) and math.isfinite(full)) or full <= 0:
            raise ValueError(f"'Out of' for {name} must be more than 0.")
        if not 0 <= got <= full:
            raise ValueError(f"{name}: marks must be between 0 and {full:g}.")
        pct = got / full * 100
        rows.append((name, f"{got:g} / {full:g} · {get_grade(pct)}"))
        total += got
        total_out += full

    if not rows:
        raise ValueError("Please enter at least one subject.")

    percent = total / total_out * 100
    return rows + [
        ("Total marks", f"{total:g} / {total_out:g}"),
        ("Percentage", f"{percent:.2f}%"),
        ("Overall grade", get_grade(percent)),
    ]


def bmi():
    age = get_number("age", "Age")
    if not age.is_integer() or not 2 <= age <= 120:
        raise ValueError("Age must be a whole number between 2 and 120.")
    if request.form.get("gender") not in ("male", "female"):
        raise ValueError("Please choose male or female.")

    # Turn whatever the user typed into meters and kilograms
    if request.form.get("unit") == "metric":
        height = get_number("cm", "Height") / 100              # cm to meters
        weight = get_number("kg", "Weight")                    # already kg
    else:
        feet = get_number("feet", "Feet")
        inches = get_number("inches", "Inches")
        if not 0 <= inches < 12:
            raise ValueError("Inches must be between 0 and 11.")
        height = (feet * 12 + inches) * 0.0254                 # inches to meters
        weight = get_number("pounds", "Weight") * 0.45359237   # pounds to kg

    if height <= 0 or weight <= 0:
        raise ValueError("Height and weight must be more than 0.")
    if not 0.5 <= height <= 2.5:
        raise ValueError("That height looks unrealistic. Check your value and units.")
    if not 1 <= weight <= 500:
        raise ValueError("That weight looks unrealistic. Check your value and units.")

    value = weight / (height * height)
    if age < 20:
        category = "Not shown for ages 2 to 19"   # kids use growth charts
    elif value < 18.5:
        category = "Underweight"
    elif value < 25:
        category = "Normal weight"
    elif value < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return [("BMI", f"{value:.1f}"), ("Category", category)]


def currency():
    amount = get_number("cur_amount", "Amount")
    source = request.form.get("cur_from")
    target = request.form.get("cur_to")
    RATES, _ = get_rates()
    if source not in RATES or target not in RATES:
        raise ValueError("Please pick valid currencies.")
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")
    if amount > MAX_AMOUNT:
        raise ValueError("Amount is too large for this demo.")

    converted = amount / RATES[source] * RATES[target]   # go through INR
    rate = RATES[target] / RATES[source]
    return [
        ("You entered", f"{amount:,.2f} {source}"),
        ("Converted", f"{converted:,.2f} {target}"),
        ("Rate used", f"1 {source} = {rate:,.4f} {target}"),
    ]


def attendance():
    total = get_number("total", "Total classes")
    attended = get_number("attended", "Attended classes")
    if not (total.is_integer() and attended.is_integer()):
        raise ValueError("Classes must be whole numbers.")
    total, attended = int(total), int(attended)
    if total <= 0:
        raise ValueError("Total classes must be more than 0.")
    if attended < 0:
        raise ValueError("Attended classes cannot be negative.")
    if attended > total:
        raise ValueError("Attended classes cannot be more than total classes.")

    percent = attended / total * 100
    if percent >= REQUIRED_ATTENDANCE:
        status = "Attendance requirement met ✅"
    else:
        status = "Attendance requirement not met ❌"
    return [
        ("Total classes", total),
        ("Attended", attended),
        ("Absent", total - attended),
        ("Attendance", f"{percent:.2f}%"),
        ("Status", status),
    ]


def bank():
    action = request.form.get("action")
    if action == "check":
        return [("Current balance", f"₹{account['balance']:,.2f}")]

    amount = get_number("bank_amount", "Amount")
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")
    if amount > MAX_AMOUNT:
        raise ValueError("Amount is too large for this demo.")

    if action == "deposit":
        account["balance"] += amount
        done = "Deposited"
    elif action == "withdraw":
        if amount > account["balance"]:
            raise ValueError(f"Not enough balance. You only have ₹{account['balance']:,.2f}.")
        account["balance"] -= amount
        done = "Withdrawn"
    else:
        raise ValueError("Unknown action.")

    account["balance"] = round(account["balance"], 2)
    return [(done, f"₹{amount:,.2f}"), ("New balance", f"₹{account['balance']:,.2f}")]


# Maps the tool name from the form to the function that handles it
TOOLS = {"grades": grades, "bmi": bmi, "currency": currency,
         "attendance": attendance, "bank": bank}


# ---------- The one page ----------

@app.route("/", methods=["GET", "POST"])
def index():
    tool = request.form.get("tool", "grades")   # which tab is open
    if tool not in TOOLS:
        tool = "grades"
    unit = "metric" if request.form.get("unit") == "metric" else "us"   # BMI units
    result = None
    error = None

    if request.method == "POST":
        try:
            result = TOOLS[tool]()
        except ValueError as problem:
            error = str(problem)

    rates, live_rates = get_rates()
    if tool == "grades" and request.method == "POST":
        grade_rows = list(zip_longest(request.form.getlist("subject"), request.form.getlist("mark"),
                                      request.form.getlist("outof"), fillvalue=""))
    else:
        grade_rows = [("", "", "100")] * 3

    return render_template(
        "index.html", grade_rows=grade_rows, live_rates=live_rates, names=CURRENCY_NAMES, tabs=TABS, tool=tool, unit=unit, result=result, error=error,
        form=request.form, rates=sorted(rates), balance=account["balance"],
        required=REQUIRED_ATTENDANCE,
    )


# Only for local testing. On Render, Gunicorn starts the app instead.
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)