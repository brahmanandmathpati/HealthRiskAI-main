import joblib
import numpy as np

# Load model
model = joblib.load("models/diabetes_model.pkl")

def predict_diabetes(data):
    data = np.array(data).reshape(1, -1)
    
    prediction = model.predict(data)[0]
    probability = model.predict_proba(data)[0][1]
    
    return prediction, probability