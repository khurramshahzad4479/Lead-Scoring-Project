import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

print("📁 Loading CSV...")
df = pd.read_csv('Lead Scoring.csv')
print(f"📊 Original shape: {df.shape}")

# Remove useless columns
useless_cols = [
    'Prospect ID', 'Lead Number', 'Do Not Email', 'Do Not Call', 'Country', 
    'Search', 'Magazine', 'Newspaper Article', 'X Education Forums', 'Newspaper',
    'Digital Advertisement', 'Through Recommendations', 'Receive More Updates About Our Courses',
    'Update me on Supply Chain Content', 'Get updates on DM Content', 
    'I agree to pay the amount through cheque', 'A free copy of Mastering The Interview', 
    'Tags', 'Lead Quality', 'Lead Profile'
]
df = df.drop(useless_cols, axis=1, errors='ignore')

# Replace "Select" with NaN
df = df.replace('Select', pd.NA)

# Drop columns with >30% missing
df = df.dropna(axis=1, thresh=int(0.7 * len(df)))

# Fill missing values
for col in df.columns:
    try:
        df[col] = df[col].fillna(df[col].median())
    except (TypeError, ValueError):
        mode_val = df[col].mode()
        if len(mode_val) > 0:
            df[col] = df[col].fillna(mode_val[0])
        else:
            df[col] = df[col].fillna('Unknown')

print(f"📊 After cleaning: {df.shape}")

# Separate target
target = df['Converted']
features = df.drop('Converted', axis=1)

# One-Hot Encoding
features = pd.get_dummies(features, drop_first=True)
print(f"📊 Features: {len(features.columns)}")

# Split
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Train with tuning
print("🔧 Training model...")
rf = RandomForestClassifier(random_state=42)

param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5]
}

grid_search = GridSearchCV(rf, param_grid, cv=3, n_jobs=-1, verbose=1)
grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_
print(f"✅ Best params: {grid_search.best_params_}")

# Evaluate
predictions = best_model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"🎯 Accuracy: {accuracy * 100:.2f}%")

# Save
joblib.dump(best_model, 'real_model.pkl')
joblib.dump(features.columns.tolist(), 'model_columns.pkl')
print("\n💾 Model saved!")