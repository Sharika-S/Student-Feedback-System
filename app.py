from flask import Flask, request, redirect, render_template_string
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB = Path(__file__).with_name("feedback.db")

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                rating INTEGER NOT NULL,
                message TEXT NOT NULL
            )
        """)

init_db()

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Student Feedback System</title>
<style>
* {box-sizing:border-box}
body {font-family:Arial,sans-serif;background:#eef5ff;margin:0;color:#203047}
header {background:#1769aa;color:white;text-align:center;padding:25px}
main {max-width:850px;margin:25px auto;padding:15px}
.card {background:white;padding:22px;margin:16px 0;border-radius:12px;
box-shadow:0 3px 12px #0001}
input,textarea,select {width:100%;padding:12px;margin:8px 0 16px;
border:1px solid #ccd8e5;border-radius:7px;font-size:15px}
button {background:#1769aa;color:white;border:0;padding:12px 18px;
border-radius:7px;cursor:pointer}
.stars {color:#e5a000;font-size:22px}
.count {color:#1769aa;font-weight:bold}
</style>
</head>
<body>
<header>
<h1>Student Feedback System</h1>
<p>Share your experience and help us improve</p>
</header>
<main>
<div class="card">
<h2>Submit Your Feedback</h2>
<form method="POST" action="/submit">
<label>Student Name</label>
<input name="name" placeholder="Enter your name" maxlength="100" required>
<label>Rating</label>
<select name="rating" required>
<option value="5">5 - Excellent</option>
<option value="4">4 - Very Good</option>
<option value="3">3 - Good</option>
<option value="2">2 - Fair</option>
<option value="1">1 - Needs Improvement</option>
</select>
<label>Your Feedback</label>
<textarea name="message" rows="4" maxlength="1000"
placeholder="Write your feedback here..." required></textarea>
<button type="submit">Submit Feedback</button>
</form>
</div>
<h2>Submitted Feedback <span class="count">({{ feedback|length }})</span></h2>
{% for item in feedback %}
<div class="card">
<h3>{{ item[1] }}</h3>
<div class="stars">{{ "★" * item[2] }}{{ "☆" * (5-item[2]) }}</div>
<p>{{ item[3] }}</p>
</div>
{% else %}
<div class="card">No feedback yet. Be the first to submit!</div>
{% endfor %}
</main>
</body>
</html>
"""

@app.route("/")
def home():
    with sqlite3.connect(DB) as con:
        feedback = con.execute(
            "SELECT * FROM feedback ORDER BY id DESC"
        ).fetchall()
    return render_template_string(PAGE, feedback=feedback)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()
    try:
        rating = int(request.form.get("rating", "0"))
    except ValueError:
        rating = 0

    if name and message and 1 <= rating <= 5:
        with sqlite3.connect(DB) as con:
            con.execute(
                "INSERT INTO feedback (name, rating, message) VALUES (?, ?, ?)",
                (name, rating, message)
            )
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=5003)
