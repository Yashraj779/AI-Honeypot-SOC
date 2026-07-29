from collections import Counter, defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, redirect, render_template, request

from ai_engine import classify_attack, generate_ai_summary, generate_risk_score
from config import Config
from database import logs_collection
from utils import get_client_ip, get_geo, get_user_agent

app = Flask(__name__)
app.config.from_object(Config)

IST = ZoneInfo("Asia/Kolkata")


def to_ist_display_time(timestamp):
    """Convert a MongoDB timestamp to IST display text."""

    if not timestamp:
        return "N/A"

    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    return timestamp.astimezone(IST).strftime("%H:%M:%S")


def to_ist_timeline_bucket(timestamp):
    """Convert a timestamp to an IST timeline bucket label."""

    if not timestamp:
        return None

    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    return timestamp.astimezone(IST).strftime("%H:%M")


# =====================================================
# LOG ATTACK
# =====================================================
def log_attack(service, username, password):
    """Save a login attempt to MongoDB using UTC timestamps."""

    ip = get_client_ip()
    user_agent = get_user_agent()
    timestamp = datetime.now(timezone.utc)
    country, city, lat, lon = get_geo(ip)

    attack = classify_attack(
        ip=ip,
        username=username,
        password=password,
        country=country,
        service=service,
    )

    risk_score = generate_risk_score(ip, password)

    log = {
        "service": service,
        "ip": ip,
        "username": username,
        "password": password,
        "user_agent": user_agent,
        "timestamp": timestamp,
        "attempt_count": attack["attempt_count"],
        "attack_type": attack["attack_type"],
        "risk_level": attack["risk_level"],
        "ml_prediction": attack["ml_prediction"],
        "ml_confidence": attack["ml_confidence"],
        "risk_score": risk_score,
        "country": country,
        "city": city,
        "lat": lat,
        "lon": lon,
    }

    logs_collection.insert_one(log)


# =====================================================
# HOME LOGIN
# =====================================================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Allow admin to access dashboard
        if username == "admin" and password == "secure123":
            return redirect("/dashboard")

        # Log attacker
        log_attack(
            service="web_login",
            username=username,
            password=password,
        )

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# =====================================================
# ADMIN HONEYPOT
# =====================================================
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        log_attack(
            service="admin_panel",
            username=username,
            password=password,
        )

        return render_template("login.html", error="Access Denied")

    return render_template("login.html")


# =====================================================
# DASHBOARD
# =====================================================
@app.route("/dashboard")
def dashboard():
    logs = list(logs_collection.find().sort("timestamp", -1))

    for log in logs:
        log["display_time"] = to_ist_display_time(log.get("timestamp"))

    total_attempts = len(logs)

    attack_counter = Counter(log.get("attack_type", "Unknown") for log in logs)

    brute_force_count = attack_counter.get("Brute Force", 0)
    suspicious_count = attack_counter.get("Credential Stuffing", 0)
    bot_attack_count = attack_counter.get("Bot Attack", 0)
    normal_count = attack_counter.get("Normal", 0)

    service_counter = Counter(
        log.get("service") for log in logs if log.get("service")
    )

    web_login_count = service_counter.get("web_login", 0)
    admin_panel_count = service_counter.get("admin_panel", 0)

    unique_ips = len({log.get("ip") for log in logs})

    ips = [log.get("ip") for log in logs]
    users = [log.get("username") for log in logs]
    attempts = [log.get("attempt_count", 0) for log in logs]
    attacks = [log.get("attack_type") for log in logs]

    top_ip = Counter(ips).most_common(1)[0][0] if ips else "N/A"
    top_user = Counter(users).most_common(1)[0][0] if users else "N/A"
    top_attack = Counter(attacks).most_common(1)[0][0] if attacks else "N/A"
    highest_attempt = max(attempts) if attempts else 0

    # -------------------------
    # Timeline
    # -------------------------
    timeline = defaultdict(int)

    for log in logs:
        bucket = to_ist_timeline_bucket(log.get("timestamp"))
        if bucket:
            timeline[bucket] += 1

    timeline_labels = sorted(timeline.keys())
    timeline_counts = [timeline[label] for label in timeline_labels]

    # -------------------------
    # Attack Map
    # -------------------------
    attack_locations = []

    for log in logs:
        lat = log.get("lat")
        lon = log.get("lon")

        if lat is not None and lon is not None:
            attack_locations.append({"lat": lat, "lon": lon})

    # -------------------------
    # AI Summary
    # -------------------------
    ai_summary = generate_ai_summary()

    average_risk_score = 0
    if logs:
        average_risk_score = round(
            sum(log.get("risk_score", 0) for log in logs) / len(logs),
            2,
        )

    return render_template(
        "dashboard.html",
        logs=logs,
        total_attempts=total_attempts,
        brute_force_count=brute_force_count,
        suspicious_count=suspicious_count,
        bot_attack_count=bot_attack_count,
        normal_count=normal_count,
        web_login_count=web_login_count,
        admin_panel_count=admin_panel_count,
        unique_ips=unique_ips,
        top_ip=top_ip,
        top_user=top_user,
        highest_attempt=highest_attempt,
        top_attack=top_attack,
        timeline_labels=timeline_labels,
        timeline_counts=timeline_counts,
        attack_locations=attack_locations,
        ai_summary=ai_summary,
        average_risk_score=average_risk_score,
    )


# =====================================================
# LIVE LOG API
# =====================================================
@app.route("/api/logs")
def api_logs():
    logs = list(
        logs_collection.find().sort("timestamp", -1).limit(100)
    )

    for log in logs:
        timestamp = log.get("timestamp")
        if timestamp:
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

            log["timestamp"] = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    return jsonify(logs)


# =====================================================
# HEALTH CHECK
# =====================================================
@app.route("/health")
def health():
    try:
        logs_collection.database.command("ping")

        return jsonify(
            {
                "status": "online",
                "database": "connected",
                "application": "AI-Honeypot-SOC",
            }
        )

    except Exception as e:
        return jsonify({"status": "error", "database": str(e)}), 500


# =====================================================
# START APPLICATION
# =====================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
