import os
import joblib
import numpy as np
from collections import deque
from sklearn.ensemble import IsolationForest

MODEL_PATH = "ai_engine/isolation_model.pkl"

TRAIN_SIZE = 500
WINDOW_SIZE = 300

training_buffer = []
recent_window = deque(maxlen=WINDOW_SIZE)

model = None


def load_or_initialize_model():

    global model

    if os.path.exists(MODEL_PATH):

        model = joblib.load(MODEL_PATH)
        print("Loaded trained Isolation Forest model")

    else:

        print("Model not found. Collecting training data...")


def extract_features(metric):

    return [
        metric["cpu"],
        metric["memory"],
        metric["latency"],
        metric["error_rate"]
    ]


def train_model():

    global model

    data = np.array(training_buffer)

    model = IsolationForest(
        n_estimators=120,
        contamination=0.08,
        random_state=42
    )

    model.fit(data)

    joblib.dump(model, MODEL_PATH)

    print("Model trained and saved →", MODEL_PATH)


def detect_anomaly(metric):

    global model

    features = extract_features(metric)

    # PHASE 1 — TRAIN MODEL ON FIRST RUN
    if model is None:

        training_buffer.append(features)

        if len(training_buffer) >= TRAIN_SIZE:

            train_model()

        return False

    # PHASE 2 — STREAM ANALYSIS

    recent_window.append(features)

    arr = np.array(recent_window)

    # Isolation Forest
    iso_pred = model.predict([features])[0]
    iso_anomaly = iso_pred == -1

    # Z-score
    mean = arr.mean(axis=0)
    std = arr.std(axis=0)

    z_scores = np.abs((features - mean) / (std + 1e-6))
    z_anomaly = np.any(z_scores > 2)

    return iso_anomaly or z_anomaly