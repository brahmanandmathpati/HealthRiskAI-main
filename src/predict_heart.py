import joblib
import numpy as np

model = joblib.load("models/heart_model.pkl")

def predict_heart(data):
    data = np.array(data).reshape(1, -1)
    result = model.predict(data)[0]
    prob = model.predict_proba(data)[0][1]
    return result, prob