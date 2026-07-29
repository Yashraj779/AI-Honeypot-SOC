from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import Counter
from database import logs_collection
from ml.predictor import predict_attack

def classify_attack(ip, username, password, country="Unknown", service="web_login"):
    """
    Rule-based attack classification with Machine Learning prediction.
    """

    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    attempt_count = logs_collection.count_documents({
        "ip": ip
    })

    same_password_count = logs_collection.count_documents({
        "ip": ip,
        "password": password
    })

    recent_attempts = logs_collection.count_documents({
        "ip": ip,
        "timestamp": {
            "$gte": now - timedelta(seconds=10)
        }
    })

    attack_type = "Normal"
    risk_level = "Low"

    if attempt_count > 8:
        attack_type = "Brute Force"
        risk_level = "High"

    elif same_password_count > 6:
        attack_type = "Credential Stuffing"
        risk_level = "High"

    elif recent_attempts > 10:
        attack_type = "Bot Attack"
        risk_level = "High"

    # -----------------------------
    # Machine Learning Prediction
    # -----------------------------
    ml_prediction, ml_confidence = predict_attack(
        attempt_count=attempt_count + 1,
        same_password_count=same_password_count,
        recent_attempts=recent_attempts,
        country=country,
        service=service,
        risk_level=risk_level
    )

    return {
        "attack_type": attack_type,
        "risk_level": risk_level,
        "attempt_count": attempt_count + 1,
        "ml_prediction": ml_prediction,
        "ml_confidence": ml_confidence
    }


def generate_risk_score(ip, password):
    """
    Generate a risk score between 0 and 100.
    This is an intelligent scoring layer that
    can later be replaced by an ML model.
    """

    score = 10

    total_attempts = logs_collection.count_documents({
        "ip": ip
    })

    repeated_password = logs_collection.count_documents({
        "ip": ip,
        "password": password
    })

    if total_attempts >= 5:
        score += 25

    if total_attempts >= 10:
        score += 20

    if repeated_password >= 3:
        score += 25

    if repeated_password >= 8:
        score += 20

    return min(score, 100)


def generate_ai_summary():
    """
    Generate an intelligent dashboard summary.
    """

    logs = list(logs_collection.find())

    if not logs:
        return "No attack activity has been recorded yet."

    total = len(logs)

    attack_types = Counter(
        log.get("attack_type", "Unknown")
        for log in logs
    )

    top_attack = attack_types.most_common(1)[0][0]

    countries = Counter(
        log.get("country", "Unknown")
        for log in logs
    )

    top_country = countries.most_common(1)[0][0]

    unique_ips = len(set(
        log.get("ip")
        for log in logs
    ))

    return (
        f"{total} login attempts have been recorded from "
        f"{unique_ips} unique IP addresses. "
        f"The dominant attack pattern is {top_attack}. "
        f"Most activity originated from {top_country}. "
        f"Security monitoring is active."
    )