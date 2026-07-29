import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("ml/training_data.csv")

# -----------------------------
# Encode categorical features
# -----------------------------
country_encoder = LabelEncoder()
service_encoder = LabelEncoder()
risk_encoder = LabelEncoder()
attack_encoder = LabelEncoder()

df["country"] = country_encoder.fit_transform(df["country"])
df["service"] = service_encoder.fit_transform(df["service"])
df["risk_level"] = risk_encoder.fit_transform(df["risk_level"])

# -----------------------------
# Features
# -----------------------------
X = df[
    [
        "attempt_count",
        "same_password_count",
        "recent_attempts",
        "country",
        "service",
        "risk_level"
    ]
]

# -----------------------------
# Labels
# -----------------------------
y = attack_encoder.fit_transform(df["attack_type"])

# -----------------------------
# Train/Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -----------------------------
# Train Model
# -----------------------------
model = RandomForestClassifier(
    n_estimators=300,
    random_state=42
)

model.fit(X_train, y_train)

# -----------------------------
# Evaluate
# -----------------------------
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\n==============================")
print(f"Model Accuracy : {accuracy*100:.2f}%")
print("==============================\n")

print(
    classification_report(
        y_test,
        predictions,
        target_names=attack_encoder.classes_
    )
)

# -----------------------------
# Save Model
# -----------------------------
joblib.dump(model, "ml/model.pkl")

joblib.dump(country_encoder, "ml/country_encoder.pkl")
joblib.dump(service_encoder, "ml/service_encoder.pkl")
joblib.dump(risk_encoder, "ml/risk_encoder.pkl")
joblib.dump(attack_encoder, "ml/attack_encoder.pkl")

print("\n✅ Model trained successfully!")
print("Model saved to ml/model.pkl")