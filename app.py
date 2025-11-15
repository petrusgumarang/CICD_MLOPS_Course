from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os

app = FastAPI()

MODEL_PATH = "model.pkl"

# Load model on startup
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None


class PredictRequest(BaseModel):
    x: float


@app.get("/")
def root():
    return {
        "message": "Hello Astra team! CI/CD is working 🎉",
        "info": "Gunakan POST /predict dengan JSON {'x': number}"
    }


@app.post("/predict")
def predict(req: PredictRequest):
    if model is None:
        return {"error": "Model belum diload. Jalankan train.py dulu."}

    pred = model.predict([[req.x]])[0]
    return {"x": req.x, "predicted_y": float(pred)}
