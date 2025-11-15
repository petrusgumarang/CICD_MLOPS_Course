import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Contoh training data untuk demo: y = 2x
data = pd.DataFrame({
    "x": [1, 2, 3, 4, 5],
    "y": [20, 40, 60, 80, 100]
})

X = data[["x"]]
y = data["y"]

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "model.pkl")

print("✅ Model trained and saved to model.pkl")
