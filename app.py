from flask import jsonify, Flask, render_template, request, session
from flask_session import Session
import psycopg2
import psycopg2.extras
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def apology(message):
    return render_template("apology.html", message=message)


# Configure Flask application
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def get_db_connection():
    """Return a new connection to the PostgreSQL database."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL environment variable not set.")
    return psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/calendar")
def calendar():
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT name, description, date_time, studio_id
        FROM classes
        JOIN studios ON classes.studio_id = studios.id;
    """)
    rows = cur.fetchall()
    con.close()

    events = []
    for row in rows:
        dt = row["date_time"]
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        time_str = dt.strftime("%H:%M")
        events.append({
            "title": f"{row['name']}-{row['description']}-{time_str}",
            "studio": row["studio_id"]
        })

    return render_template("calendar.html", events=events)


@app.route('/events')
def events():
    con = get_db_connection()
    cur = con.cursor()

    now = datetime.now()
    six_months_from_now = now + relativedelta(months=6)

    # --- Load saved classes ---
    cur.execute("SELECT * FROM monthly_summary;")
    saved_rows = cur.fetchall()

    saved_events = []
    saved_slots = set()
    saved_months = set()

    for row in saved_rows:
        dt = row["date_time"]
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")

        saved_events.append({
            "title": row["title"],
            "description": row["title"],
            "start": dt.isoformat(),
            "studio": row["studio"],
            "class_id": row["class_id"]
        })

        saved_slots.add(f"{dt.strftime('%Y-%m-%d %H:%M:%S')}-{row['studio']}-{row['class_id']}")
        saved_months.add(row["month"])

    # --- Load default repeating classes from weekly_summary ---
    cur.execute("""
        SELECT weekly_summary.id AS class_id, name, description, date_time, studio_id
        FROM weekly_summary
        JOIN studios ON weekly_summary.studio_id = studios.id;
    """)
    default_rows = cur.fetchall()

    default_events = []
    for row in default_rows:
        base_dt = row["date_time"]
        if isinstance(base_dt, str):
            base_dt = datetime.strptime(base_dt, "%Y-%m-%d %H:%M:%S")

        current_dt = base_dt
        while current_dt <= six_months_from_now:
            current_month = current_dt.strftime("%Y-%m")

            if current_month not in saved_months:
                slot_key = f"{current_dt.strftime('%Y-%m-%d %H:%M:%S')}-{row['studio_id']}-{row['class_id']}"
                if slot_key not in saved_slots:
                    default_events.append({
                        "title": f"{row['name']} {row['description']}",
                        "start": current_dt.isoformat(),
                        "studio": row["studio_id"],
                        "class_id": row["class_id"]
                    })

            current_dt += timedelta(weeks=1)

    con.close()
    return jsonify(saved_events + default_events)


@app.route("/save_month", methods=["POST"])
def save_month():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No event data received"}), 400

    con = get_db_connection()
    cur = con.cursor()

    try:
        first_date = datetime.fromisoformat(data[0]['start'])
        month = first_date.strftime("%Y-%m")

        # Delete existing entries for this month
        cur.execute("DELETE FROM monthly_summary WHERE month = %s;", (month,))

        # Insert new events
        for event in data:
            start_dt = datetime.fromisoformat(event['start'])
            cur.execute("""
                INSERT INTO monthly_summary (studio, title, date_time, month, class_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                event['studio'],
                event['title'],
                start_dt,
                month,
                event['class']
            ))

        con.commit()
        return jsonify({"status": "success", "message": f"Saved month: {month}"})
    finally:
        con.close()


@app.route("/history", methods=["GET"])
def history():
    con = get_db_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT
            monthly_summary.month,
            studios.name AS studio_name,
            SUM(classes.rate) AS total_owed,
            COUNT(*) AS class_count
        FROM
            monthly_summary
        JOIN
            studios ON monthly_summary.studio = studios.id
        JOIN
            classes ON monthly_summary.class_id = classes.id
        GROUP BY
            monthly_summary.month, monthly_summary.studio, studio_name
        ORDER BY
            monthly_summary.month DESC, studio_name;
    """)
    data = cur.fetchall()
    con.close()

    history = {}
    for row in data:
        month = row["month"]
        if month not in history:
            history[month] = []
        history[month].append({
            "studio": row["studio_name"],
            "total_owed": row["total_owed"],
            "class_count": row["class_count"],
        })

    return render_template("history.html", history=history)


if __name__ == "__main__":
    app.run(debug=True)
