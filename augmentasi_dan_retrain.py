# ======================================================================
# augmentasi_dan_retrain.py
#
# Masalah kedua yang ditemukan setelah relabel_dan_retrain.py:
#   Data training asli hanya mencakup download_speed 1-9.89 Mbps
#   (WiFi lambat). Saat pengguna input nilai realistis modern
#   (misal 11 Mbps atau 1069 Mbps hasil speed test fiber/gigabit),
#   nilainya jauh di luar jangkauan yang pernah "dilihat" model
#   -> GaussianNB mengekstrapolasi dan hasilnya tidak masuk akal
#   (kelas dengan variansi lebar "menang" secara matematis walau
#   salah secara logika).
#
# Solusi:
#   Tambahkan data SINTETIS dengan rentang nilai yang realistis dan
#   lebar (mencakup WiFi lambat s/d fiber gigabit), dilabeli otomatis
#   memakai rule yang SAMA PERSIS dengan kartu analisis, lalu gabung
#   dengan data asli dan retrain.
#
# Cara pakai:
#   python augmentasi_dan_retrain.py
# ======================================================================

import numpy as np
import pandas as pd

from model import train_model, MODEL_PATH
from relabel_dan_retrain import kualitas_jaringan, kualitas_keluhan, gabungkan_label


RANDOM_SEED = 42
JUMLAH_DATA_SINTETIS = 600


def buat_data_sintetis(n, seed=RANDOM_SEED):
    """Membuat n baris data sintetis dengan rentang nilai realistis,
    mencakup WiFi lambat s/d koneksi fiber/gigabit cepat, supaya model
    tidak buta terhadap nilai di luar rentang data asli."""

    rng = np.random.default_rng(seed)

    baris = []

    for _ in range(n):

        # Pilih "skenario" kecepatan secara acak supaya distribusinya
        # tidak menumpuk di satu rentang saja (lambat / sedang / cepat
        # / sangat cepat masing-masing terwakili).
        skenario = rng.choice(
            ["lambat", "sedang", "cepat", "sangat_cepat"],
            p=[0.25, 0.25, 0.25, 0.25]
        )

        if skenario == "lambat":
            download = rng.uniform(0.5, 5)
            upload = rng.uniform(0.2, 2)
            latency = rng.uniform(80, 300)
            packet_loss = rng.uniform(2, 15)

        elif skenario == "sedang":
            download = rng.uniform(5, 20)
            upload = rng.uniform(2, 10)
            latency = rng.uniform(30, 100)
            packet_loss = rng.uniform(0.5, 5)

        elif skenario == "cepat":
            download = rng.uniform(20, 150)
            upload = rng.uniform(10, 80)
            latency = rng.uniform(10, 50)
            packet_loss = rng.uniform(0, 2)

        else:  # sangat_cepat (fiber / gigabit)
            download = rng.uniform(150, 1200)
            upload = rng.uniform(80, 600)
            latency = rng.uniform(3, 30)
            packet_loss = rng.uniform(0, 1)

        skor_keluhan = round(rng.uniform(1, 5), 2)

        baris.append({
            "download_speed": round(download, 2),
            "upload_speed": round(upload, 2),
            "latency": round(latency, 2),
            "packet_loss": round(packet_loss, 2),
            "skor_keluhan": skor_keluhan,
        })

    df = pd.DataFrame(baris)

    df["label_kelas"] = df.apply(
        lambda row: gabungkan_label(
            kualitas_jaringan(
                row["download_speed"],
                row["upload_speed"],
                row["latency"],
                row["packet_loss"]
            ),
            kualitas_keluhan(row["skor_keluhan"])
        ),
        axis=1
    )

    return df


def main():

    print("=" * 70)
    print("LANGKAH 1: Muat data asli (sudah dilabel ulang, rule-based)")
    print("=" * 70)

    df_asli = pd.read_csv("dataset_wifi.csv")
    df_asli = df_asli[
        ["download_speed", "upload_speed", "latency", "packet_loss", "skor_keluhan", "label_kelas"]
    ]
    print(f"Data asli: {len(df_asli)} baris")

    print()
    print("=" * 70)
    print(f"LANGKAH 2: Buat {JUMLAH_DATA_SINTETIS} data sintetis (rentang realistis)")
    print("=" * 70)

    df_sintetis = buat_data_sintetis(JUMLAH_DATA_SINTETIS)
    print(f"Data sintetis: {len(df_sintetis)} baris")
    print()
    print("Contoh rentang data sintetis:")
    print(df_sintetis[["download_speed", "upload_speed", "latency", "packet_loss"]].describe().loc[["min", "max"]])

    print()
    print("=" * 70)
    print("LANGKAH 3: Gabungkan data asli + sintetis")
    print("=" * 70)

    df_gabungan = pd.concat([df_asli, df_sintetis], ignore_index=True)

    print(f"Total data gabungan: {len(df_gabungan)} baris")
    print()
    print("Distribusi label:")
    print(df_gabungan["label_kelas"].value_counts().to_string())

    df_gabungan.to_csv("dataset_wifi.csv", index=False)
    print()
    print("Dataset final disimpan -> dataset_wifi.csv (data asli + sintetis)")

    print()
    print("=" * 70)
    print("LANGKAH 4: Retrain model GaussianNB")
    print("=" * 70)

    hasil = train_model(df_gabungan)

    print(f"Akurasi   : {hasil['akurasi']:.4f}")
    print(f"Presisi   : {hasil['presisi']:.4f}")
    print(f"Recall    : {hasil['recall']:.4f}")
    print(f"F1-score  : {hasil['f1']:.4f}")
    print()
    print(f"Model final disimpan -> {MODEL_PATH}")

    print()
    print("=" * 70)
    print("LANGKAH 5: Verifikasi ulang dengan kasus dari screenshot")
    print("=" * 70)

    from model import load_model, predict

    model = load_model()

    kasus_uji = {
        "Screenshot 2 (download 11 Mbps)": [11.00, 10.00, 20.00, 0.00, 4.87],
        "Screenshot 1 (download 1069 Mbps)": [1069.71, 390.51, 65.44, 0.10, 4.80],
    }

    for nama, kasus in kasus_uji.items():
        kelas, prob = predict(model, kasus)
        lj = kualitas_jaringan(kasus[0], kasus[1], kasus[2], kasus[3])
        lk = kualitas_keluhan(kasus[4])
        print(f"{nama}")
        print(f"  Analisis Informasi Jaringan : {lj}")
        print(f"  Analisis Keluhan Pengguna    : {lk}")
        print(f"  Hasil Akhir (GaussianNB)     : {kelas}")
        print(f"  Probabilitas                 : {prob}")
        print()


if __name__ == "__main__":
    main()
