# ======================================================================
# relabel_dan_retrain.py
#
# Tujuan:
#   1. Menghitung ULANG label_kelas di dataset_wifi.csv menggunakan
#      LOGIKA RULE-BASED YANG SAMA dengan kartu "Analisis Informasi
#      Jaringan" dan "Analisis Keluhan Pengguna" (modules/user_hasil.py),
#      bukan lagi memakai label subjektif hasil isian manual pengguna.
#   2. Melatih ulang model GaussianNB dengan label yang sudah konsisten.
#
# Kenapa ini perlu:
#   Label lama (label_kelas) diisi manual lewat st.radio() oleh
#   responden -> subjektif & tidak konsisten dengan angka teknisnya.
#   Akibatnya model belajar pola yang bertentangan dengan hasil
#   rule-based, sehingga "Hasil Akhir" bisa beda jauh dari kartu
#   analisis (walau kartu analisis menunjukkan "Sangat Baik").
#
# Cara pakai:
#   python relabel_dan_retrain.py
#
# Output:
#   - dataset_wifi_relabeled.csv   (dataset dengan label baru)
#   - model_gnb.joblib             (model baru, menimpa yang lama)
#   - backup_model_gnb_lama.joblib (cadangan model lama)
#   - backup_dataset_wifi_lama.csv (cadangan dataset lama)
# ======================================================================

import shutil
import pandas as pd

from model import load_dataset, train_model, FITUR, LABEL, MODEL_PATH


# ----------------------------------------------------------------------
# 1. FUNGSI RULE-BASED (disalin persis dari modules/user_hasil.py,
#    tanpa dependensi streamlit, supaya bisa dipakai untuk batch process
#    seluruh dataset).
# ----------------------------------------------------------------------

def kualitas_jaringan(download, upload, latency, packet_loss):

    skor = 0

    if download >= 8.5:
        skor += 3
    elif download >= 6:
        skor += 2
    elif download >= 3:
        skor += 1

    if upload >= 4:
        skor += 3
    elif upload >= 2:
        skor += 2
    elif upload >= 1:
        skor += 1

    if latency <= 30:
        skor += 3
    elif latency <= 70:
        skor += 2
    elif latency <= 150:
        skor += 1

    if packet_loss <= 1:
        skor += 3
    elif packet_loss <= 3:
        skor += 2
    elif packet_loss <= 8:
        skor += 1

    if skor >= 11:
        return "Sangat Baik"
    elif skor >= 8:
        return "Baik"
    elif skor >= 5:
        return "Sedang"
    else:
        return "Buruk"


def kualitas_keluhan(skor):

    if skor >= 4.5:
        return "Sangat Baik"
    elif skor >= 3.5:
        return "Baik"
    elif skor >= 2:
        return "Sedang"
    else:
        return "Buruk"


# ----------------------------------------------------------------------
# 2. FUNGSI PENGGABUNG
#
#    "Hasil Akhir" mencerminkan KUALITAS JARINGAN dan KELUHAN PENGGUNA
#    sekaligus. Digabung dengan cara mengubah tiap label ke skor 1-4,
#    dirata-rata, lalu dibulatkan ke label terdekat. Ini membuat hasil
#    akhir konsisten dengan dua kartu analisis: kalau keduanya
#    "Sangat Baik", hasil akhir otomatis "Sangat Baik".
# ----------------------------------------------------------------------

RANK = {"Buruk": 1, "Sedang": 2, "Baik": 3, "Sangat Baik": 4}
RANK_TERBALIK = {v: k for k, v in RANK.items()}


def gabungkan_label(label_jaringan, label_keluhan):

    skor_gabungan = (RANK[label_jaringan] + RANK[label_keluhan]) / 2

    skor_bulat = round(skor_gabungan)

    skor_bulat = max(1, min(4, skor_bulat))

    return RANK_TERBALIK[skor_bulat]


def hitung_label_final(row):

    label_jaringan = kualitas_jaringan(
        row["download_speed"],
        row["upload_speed"],
        row["latency"],
        row["packet_loss"]
    )

    label_keluhan = kualitas_keluhan(row["skor_keluhan"])

    return gabungkan_label(label_jaringan, label_keluhan)


# ----------------------------------------------------------------------
# 3. PROSES UTAMA
# ----------------------------------------------------------------------

def main():

    DATASET_PATH = "dataset_wifi.csv"

    print("=" * 70)
    print("LANGKAH 1: Backup file lama")
    print("=" * 70)

    shutil.copy(DATASET_PATH, "backup_dataset_wifi_lama.csv")
    shutil.copy(MODEL_PATH, "backup_model_gnb_lama.joblib")
    print("Backup dataset -> backup_dataset_wifi_lama.csv")
    print("Backup model   -> backup_model_gnb_lama.joblib")

    print()
    print("=" * 70)
    print("LANGKAH 2: Hitung ulang label_kelas dengan rule-based scoring")
    print("=" * 70)

    df = load_dataset(DATASET_PATH)

    label_lama = df["label_kelas"].copy()

    df["label_kelas"] = df.apply(hitung_label_final, axis=1)

    jumlah_berubah = (label_lama != df["label_kelas"]).sum()

    print(f"Total data           : {len(df)}")
    print(f"Label yang berubah   : {jumlah_berubah} ({jumlah_berubah/len(df)*100:.1f}%)")
    print()
    print("Distribusi label LAMA (subjektif):")
    print(label_lama.value_counts().to_string())
    print()
    print("Distribusi label BARU (rule-based):")
    print(df["label_kelas"].value_counts().to_string())

    df.to_csv("dataset_wifi_relabeled.csv", index=False)
    print()
    print("Dataset baru disimpan -> dataset_wifi_relabeled.csv")

    # Timpa dataset_wifi.csv juga, supaya admin_data.py / export.py yang
    # baca dataset ini otomatis konsisten
    df.to_csv(DATASET_PATH, index=False)
    print(f"Dataset utama diperbarui -> {DATASET_PATH}")

    print()
    print("=" * 70)
    print("LANGKAH 3: Retrain model GaussianNB dengan label baru")
    print("=" * 70)

    hasil = train_model(df)

    print(f"Akurasi   : {hasil['akurasi']:.4f}")
    print(f"Presisi   : {hasil['presisi']:.4f}")
    print(f"Recall    : {hasil['recall']:.4f}")
    print(f"F1-score  : {hasil['f1']:.4f}")
    print()
    print("Confusion matrix:")
    print(hasil["confusion_matrix"])
    print()
    print(f"Model baru disimpan -> {MODEL_PATH}")

    print()
    print("=" * 70)
    print("LANGKAH 4: Verifikasi dengan kasus dari screenshot")
    print("=" * 70)

    from model import load_model, predict

    model = load_model()

    kasus_uji = [
        # (download, upload, latency, packet_loss, skor_keluhan)
        [11.00, 10.00, 20.00, 0.00, 4.87],
        [1069.71, 390.51, 65.44, 0.10, 4.80],
    ]

    for kasus in kasus_uji:
        kelas, prob = predict(model, kasus)
        lj = kualitas_jaringan(kasus[0], kasus[1], kasus[2], kasus[3])
        lk = kualitas_keluhan(kasus[4])
        print(f"Input: {kasus}")
        print(f"  -> Analisis Informasi Jaringan : {lj}")
        print(f"  -> Analisis Keluhan Pengguna    : {lk}")
        print(f"  -> Hasil Akhir (GaussianNB baru): {kelas}")
        print()


if __name__ == "__main__":
    main()
