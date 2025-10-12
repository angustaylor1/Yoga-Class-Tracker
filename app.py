from flask import jsonify
from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_file, session, jsonify
from flask_session import Session
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta

def apology(message):
    return render_template("apology.html", message=message)


# configure application
app = Flask(__name__)

# configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def index():
    if request.method == "GET":
        return render_template("index.html")


@app.route("/calendar")
def calendar():
    con = sqlite3.connect("information.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute(
        "SELECT name, description, date_time, studio_id FROM classes JOIN studios ON classes.studio_id = studios.id;").fetchall()
    con.close()

    events = []

    for row in rows:
        dt = datetime.strptime(row["date_time"], "%Y-%m-%d %H:%M:%S")

        time_str = dt.strftime("%H:%M")
        events.append({
            "title": row["name"] + "-" + row["description"] + "-" + time_str,
            "studio": row["studio_id"]
        })

    return render_template("calendar.html", events=events)


@app.route('/events')
def events():
    con = sqlite3.connect("information.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    now = datetime.now()
    six_months_from_now = now + relativedelta(months=6)

    # --- Load saved classes ---
    saved_rows = cur.execute("SELECT * FROM monthly_summary;").fetchall()

    saved_events = []
    saved_slots = set()
    saved_months = set()

    for row in saved_rows:
        dt = datetime.strptime(row["date_time"], "%Y-%m-%d %H:%M:%S")

        # Build saved events list
        saved_events.append({
            "title": row["title"],
            "description": row["title"],
            "start": dt.isoformat(),
            "studio": row["studio"],
            "class_id": row["class_id"]
        })

        # Track unique time/studio/class combos
        saved_slots.add(
            f"{dt.strftime('%Y-%m-%d %H:%M:%S')}-{row['studio']}-{row['class_id']}"
        )

        # Track months already saved
        saved_months.add(row["month"])

    # --- Load default repeating classes from weekly_summary ---
    default_rows = cur.execute("""
        SELECT weekly_summary.id AS class_id, name, description, date_time, studio_id
        FROM weekly_summary
        JOIN studios ON weekly_summary.studio_id = studios.id;
    """).fetchall()

    default_events = []

    for row in default_rows:
        base_dt = datetime.strptime(row["date_time"], "%Y-%m-%d %H:%M:%S")
        class_time = base_dt.strftime("%H:%M")

        current_dt = base_dt
        while current_dt <= six_months_from_now:
            current_month = current_dt.strftime("%Y-%m")

            if current_month not in saved_months:
                slot_key = f"{current_dt.strftime('%Y-%m-%d %H:%M:%S')}-{row['studio_id']}-{row['class_id']}"
                if slot_key not in saved_slots:
                    default_events.append({
                        "title": row["name"] + " " + row["description"],
                        "start": current_dt.isoformat(),
                        "studio": row["studio_id"],
                        "class_id": row["class_id"]
                    })

            # Move to next week
            current_dt += timedelta(weeks=1)

    con.close()

    # Combine saved and valid default events
    return jsonify(saved_events + default_events)


@app.route("/save_month", methods=["POST"])
def save_month():
    data = request.get_json()
    print("recieved Data:", data)

    if not data:
        return jsonify({"error": "No event data received"}), 400

    try:
        con = sqlite3.connect("information.db", timeout=5)
        cur = con.cursor()

        first_date = datetime.fromisoformat(data[0]['start'])
        month = first_date.strftime("%Y-%m")

        cur.execute("DELETE FROM monthly_summary WHERE month = ?", (month,))

        for event in data:
            start_dt = datetime.fromisoformat(event['start'])
            studio = event['studio']
            class_id = event["class"]

            cur.execute("""
                INSERT INTO monthly_summary (studio, title, date_time, month, class_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                studio,
                event['title'],
                start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                month,
                class_id
            ))

        con.commit()
        return jsonify({"status": "success", "message": f"Saved month: {month}"})

    except sqlite3.OperationalError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    finally:
        con.close()


@app.route("/history", methods=["GET", "POST"])
def history():
    # Create a connection that gets all of the relevant stuff.
    con = sqlite3.connect("Information.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    data = cur.execute("""
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
                    monthly_summary.month, monthly_summary.studio
                ORDER BY
                    monthly_summary.month, studio_name;
                """).fetchall()
    history = {}

    for row in data:
        month = row["month"]
        if month not in history:
            history[month] = []
        history[month].append({
            "studio": row["studio_name"],
            "total_owed": row["total_owed"],
            "class_count": row["class_count"]
        })

    return render_template("history.html", history=history)
