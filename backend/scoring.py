import joblib
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "real_model.pkl")
columns_path = os.path.join(BASE_DIR, "model_columns.pkl")

# Check if files exist
if not os.path.exists(model_path):
    raise FileNotFoundError(f"❌ Model file not found: {model_path}")
if not os.path.exists(columns_path):
    raise FileNotFoundError(f"❌ Columns file not found: {columns_path}")

model = joblib.load(model_path)
model_columns = joblib.load(columns_path)

print(f"✅ Model loaded! Features: {len(model_columns)}")

def predict_real_lead(form_data: dict) -> str:
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
    prediction = model.predict(df_encoded)[0]
    
    return "Hot Lead 🔥" if prediction == 1 else "Cold Lead ❄️"