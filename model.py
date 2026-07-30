import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

MODEL_PATH = "model_gnb.joblib"

FITUR = [
    "download_speed",
    "upload_speed",
    "latency",
    "packet_loss",
    "skor_keluhan"
]

LABEL = "label_kelas"


# ======================================
# LOAD DATASET
# ======================================

def load_dataset(path):

    df = pd.read_csv(path)

    return df


# ======================================
# TRAIN MODEL
# ======================================

def train_model(df):

    X = df[FITUR]

    y = df[LABEL]

    # Cek apakah setiap kelas punya minimal 2 data (syarat stratifikasi).
    # Jika ada kelas dengan data kurang dari 2, splitting dilakukan TANPA
    # stratifikasi agar aplikasi tidak berhenti (error) saat dijalankan.
    jumlah_per_kelas = y.value_counts()
    bisa_stratifikasi = (jumlah_per_kelas >= 2).all()

    if bisa_stratifikasi:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

    model = GaussianNB()

    model.fit(X_train, y_train)

    prediksi = model.predict(X_test)

    hasil = {

        "akurasi": accuracy_score(
            y_test,
            prediksi
        ),

        "presisi": precision_score(
            y_test,
            prediksi,
            average="weighted",
            zero_division=0
        ),

        "recall": recall_score(
            y_test,
            prediksi,
            average="weighted",
            zero_division=0
        ),

        "f1": f1_score(
            y_test,
            prediksi,
            average="weighted",
            zero_division=0
        ),

        "confusion_matrix": confusion_matrix(
            y_test,
            prediksi
        ),

        "model": model
    }

    joblib.dump(
        model,
        MODEL_PATH
    )

    return hasil


# ======================================
# LOAD MODEL
# ======================================

def load_model():

    return joblib.load(MODEL_PATH)


# ======================================
# PREDIKSI SATU DATA
# ======================================

def predict(model, data):

    df = pd.DataFrame(
        [data],
        columns=FITUR
    )

    hasil = model.predict(df)[0]

    probabilitas = model.predict_proba(df)[0]

    kelas = model.classes_

    prob = {}

    for k, p in zip(kelas, probabilitas):

        prob[k] = round(float(p), 4)

    return hasil, prob