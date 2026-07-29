import joblib
import pandas as pd

# Load model
model = joblib.load("ml/model.pkl")

country_encoder = joblib.load("ml/country_encoder.pkl")
service_encoder = joblib.load("ml/service_encoder.pkl")
risk_encoder = joblib.load("ml/risk_encoder.pkl")
attack_encoder = joblib.load("ml/attack_encoder.pkl")


def safe_encode(encoder, value):
    if value not in encoder.classes_:
        value = encoder.classes_[0]

    return encoder.transform([value])[0]


def predict_attack(
    attempt_count,
    same_password_count,
    recent_attempts,
    country,
    service,
    risk_level
):

    country = safe_encode(country_encoder, country)
    service = safe_encode(service_encoder, service)
    risk = safe_encode(risk_encoder, risk_level)

    data = pd.DataFrame([{

        "attempt_count": attempt_count,

        "same_password_count": same_password_count,

        "recent_attempts": recent_attempts,

        "country": country,

        "service": service,

        "risk_level": risk

    }])

    prediction = model.predict(data)[0]

    confidence = max(model.predict_proba(data)[0]) * 100

    attack = attack_encoder.inverse_transform([prediction])[0]

    return attack, round(confidence, 2)