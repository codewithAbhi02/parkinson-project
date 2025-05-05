import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import pickle

# Load dataset
df = pd.read_csv("parkinsons.csv")

# Select fewer + important features
features = [
    'MDVP:Jitter(%)', 'MDVP:RAP', 'MDVP:PPQ',
    'MDVP:Shimmer', 'Shimmer:APQ3', 'Shimmer:APQ5',
    'HNR'
]

X = df[features]
y = df['status']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train a Logistic Regression model
model = LogisticRegression(class_weight='balanced', max_iter=1000)
model.fit(X_train_scaled, y_train)

# Evaluate
print("Classification Report:\n")
print(classification_report(y_test, model.predict(X_test_scaled)))

# Save model and scaler
pickle.dump(model, open("parkinson_model.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl", "wb"))

print("✅ Model retrained and saved with balanced Logistic Regression")
