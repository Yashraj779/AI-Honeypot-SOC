import pandas as pd
import random

countries = [
    "India",
    "United States",
    "Germany",
    "Russia",
    "China",
    "Brazil",
    "United Kingdom",
    "Canada",
    "Australia",
    "France"
]

services = [
    "web_login",
    "admin_panel"
]

rows = []

for _ in range(5000):

    attack = random.choice([
        "Normal",
        "Brute Force",
        "Credential Stuffing",
        "Bot Attack"
    ])

    country = random.choice(countries)
    service = random.choice(services)

    # -----------------------------
    # Generate realistic features
    # -----------------------------
    if attack == "Normal":

        attempt_count = random.randint(1, 3)
        same_password_count = random.randint(0, 2)
        recent_attempts = random.randint(0, 3)
        risk_level = "Low"

    elif attack == "Brute Force":

        attempt_count = random.randint(10, 40)
        same_password_count = random.randint(5, 12)
        recent_attempts = random.randint(10, 30)
        risk_level = "High"

    elif attack == "Credential Stuffing":

        attempt_count = random.randint(5, 15)
        same_password_count = random.randint(8, 20)
        recent_attempts = random.randint(2, 8)
        risk_level = "High"

    else:   # Bot Attack

        attempt_count = random.randint(20, 60)
        same_password_count = random.randint(3, 8)
        recent_attempts = random.randint(15, 40)
        risk_level = "High"

    rows.append({

        "attempt_count": attempt_count,
        "same_password_count": same_password_count,
        "recent_attempts": recent_attempts,
        "country": country,
        "service": service,
        "risk_level": risk_level,
        "attack_type": attack

    })

df = pd.DataFrame(rows)

df.to_csv("ml/training_data.csv", index=False)

print("Training dataset created successfully.")
print(df.head())