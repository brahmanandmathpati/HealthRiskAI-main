import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Load dataset
df = pd.read_csv("data/heart.csv")

# IMPORTANT: check column name
print(df.columns)

# Features & target
X = df.drop("target", axis=1)
y = df["target"]

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/heart_model.pkl")

print("Heart model trained successfully!")