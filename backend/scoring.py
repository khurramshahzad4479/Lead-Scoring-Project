import joblib
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "real_model.pkl")
columns_path = os.path.join(BASE_DIR, "model_columns.pkl")

if not os.path.exists(model_path):
    raise FileNotFoundError(f"❌ Model file not found: {model_path}")
if not os.path.exists(columns_path):
    raise FileNotFoundError(f"❌ Columns file not found: {columns_path}")

model = joblib.load(model_path)
model_columns = joblib.load(columns_path)

# Which predict_proba column is P(class=1)? confirm from classes_ not assuming.
try:
    HOT_IDX = list(model.classes_).index(1)
except (ValueError, AttributeError):
    HOT_IDX = 1  # standard [0, 1] ordering

print(f"✅ Model loaded! Features: {len(model_columns)} | classes: {model.classes_}")

def predict_real_lead(form_data: dict) -> dict:
    data = {
        'Lead Origin': form_data.get("Lead Origin", "Landing Page Submission"),
        'Lead Source': form_data.get("Lead Source", "Organic Search"),
        'TotalVisits': float(form_data.get("TotalVisits", 0)),
        'Total Time Spent on Website': float(form_data.get("Total Time Spent on Website", 0)),
        'Page Views Per Visit': float(form_data.get("Page Views Per Visit", 0)),
        'What is your current occupation': form_data.get("What is your current occupation", "Unemployed")
    }

    df = pd.DataFrame([data])
    df_encoded = pd.get_dummies(df)

    for col in model_columns:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    df_encoded = df_encoded[model_columns]

    # Label: same predict() as before (behavior unchanged)
    prediction = int(model.predict(df_encoded)[0])
    is_hot = prediction == 1

    # Confidence: P(convert) = P(class=1)
    proba = model.predict_proba(df_encoded)[0]
    hot_p = float(proba[HOT_IDX])

    return {
        "label": "Hot Lead 🔥" if is_hot else "Cold Lead ❄️",
        "is_hot": is_hot,
        "confidence": round(hot_p, 4),   # 0.0 – 1.0, P(Hot)
    }