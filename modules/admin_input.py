import streamlit as st
import pandas as pd
from datetime import datetime

from database import (
    get_all_users,
    insert_hasil,
    get_or_create_user_by_nama
)
from modules import style


OPSI_KELUHAN = {
    "1 - Sangat sering bermasalah": 1,
    "2 - Sering": 2,
    "3 - Kadang-kadang": 3,
    "4 - Jarang": 4,
    "5 - Tidak pernah bermasalah": 5
}

KOLOM_TEMPLATE = [
    "id_pelanggan",
    "download_speed",
    "upload_speed",
    "latency",
    "packet_loss",
    "skor_keluhan",
    "label_kelas"
]

warna_hasil = style.warna_hasil_style

def show(model, predict):

    style.page_header(
        "Input Data (Admin)",
        "Tambahkan data klasifikasi secara manual atau import dari CSV"
    )

    tab_manual, tab_csv = st.tabs([
        "Input Manual",
        "Import CSV"
    ])

    # ==================================================
    # INPUT MANUAL
    # ==================================================

    with tab_manual:

        df_user = get_all_users()

        if len(df_user) == 0:

            st.warning("Belum ada user terdaftar.")

        else:

           

            df_user["label"] = df_user["nama"] + " (" + df_user["email"] + ")"

            pilih_label = st.selectbox(
                "Atas Nama User",
                df_user["label"]
            )

            user_id = int(
                df_user.loc[df_user["label"] == pilih_label, "id"].iloc[0]
            )

            st.markdown("#### Informasi Jaringan")

            col1, col2 = st.columns(2)

            with col1:

                download = st.number_input(
                    "Download Speed (Mbps)",
                    min_value=0.0,
                    max_value=100.0,
                    value=8.0,
                    step=0.1,
                    key="admin_download"
                )

                latency = st.number_input(
                    "Latency (ms)",
                    min_value=0.0,
                    max_value=500.0,
                    value=20.0,
                    step=1.0,
                    key="admin_latency"
                )

            with col2:

                upload = st.number_input(
                    "Upload Speed (Mbps)",
                    min_value=0.0,
                    max_value=100.0,
                    value=4.0,
                    step=0.1,
                    key="admin_upload"
                )

                packet_loss = st.number_input(
                    "Packet Loss (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=0.1,
                    key="admin_packet_loss"
                )

            st.markdown("#### Skor Keluhan")

            mode_skor = st.radio(
                "Cara mengisi skor keluhan",
                ["Isi Kuesioner", "Masukkan Angka Langsung"],
                horizontal=True
            )

            if mode_skor == "Isi Kuesioner":

                q1 = OPSI_KELUHAN[st.radio("1. Internet lambat?", list(OPSI_KELUHAN.keys()), key="aq1")]
                q2 = OPSI_KELUHAN[st.radio("2. Koneksi terputus?", list(OPSI_KELUHAN.keys()), key="aq2")]
                q3 = OPSI_KELUHAN[st.radio("3. Lag saat akses internet?", list(OPSI_KELUHAN.keys()), key="aq3")]
                q4 = OPSI_KELUHAN[st.radio("4. WiFi tidak stabil?", list(OPSI_KELUHAN.keys()), key="aq4")]
                q5 = OPSI_KELUHAN[st.radio("5. Perlu hubungi teknisi?", list(OPSI_KELUHAN.keys()), key="aq5")]

                skor_keluhan = round((q1 + q2 + q3 + q4 + q5) / 5, 2)

                st.info(f"Skor Keluhan : {skor_keluhan}")

            else:

                skor_keluhan = st.number_input(
                    "Skor Keluhan (1 - 5)",
                    min_value=1.0,
                    max_value=5.0,
                    value=3.0,
                    step=0.1
                )

            if st.button(
                    "Proses & Simpan Semua Data",
                    use_container_width=True
                ):


                kelas, prob = predict(
                    model,
                    [download, upload, latency, packet_loss, skor_keluhan]
                )

                insert_hasil(
                    user_id,
                    download,
                    upload,
                    latency,
                    packet_loss,
                    skor_keluhan,
                    kelas,
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                )

                st.success(f"Data tersimpan untuk **{pilih_label}** — Hasil: **{kelas}**")


    # ==================================================
    # IMPORT CSV
    # ==================================================

    with tab_csv:

       

        st.markdown("#### Import Data dari CSV")

        st.caption(
            "Kolom yang dibutuhkan: **download_speed, upload_speed, latency, packet_loss, skor_keluhan**. "
            "Kolom **id_pelanggan** akan dipakai sebagai nama user — jika user dengan nama tersebut "
            "belum terdaftar, sistem akan membuatkan akunnya secara otomatis saat data disimpan."
        )
        template = pd.DataFrame(columns=KOLOM_TEMPLATE)

        st.download_button(
            "Download Template CSV",
            template.to_csv(index=False).encode(),
            "template_input_wifi.csv",
            "text/csv"
        )

        file_csv = st.file_uploader(
            "Upload File CSV",
            type=["csv"],
        )

        if file_csv is not None:

            try:

                df_csv = pd.read_csv(file_csv)

            except Exception:

                st.error("File CSV tidak valid.")

                df_csv = None

            if df_csv is not None:

                kolom_kurang = [k for k in KOLOM_TEMPLATE if k not in df_csv.columns]

                if kolom_kurang:

                    st.error(f"Kolom berikut tidak ditemukan di file: {', '.join(kolom_kurang)}")

                else:

                    st.dataframe(
                            df_csv,
                            use_container_width=True
                        )

                    if st.button(
                        "Klasifikasikan Semua Data",
                        use_container_width=True
                    ):


                        berhasil = 0

                        gagal = []

                        hasil_prediksi = []

                        for _, baris in df_csv.iterrows():

                            try:

                                nilai_fitur = [
                                    float(baris["download_speed"]),
                                    float(baris["upload_speed"]),
                                    float(baris["latency"]),
                                    float(baris["packet_loss"]),
                                    float(baris["skor_keluhan"])
                                ]

                            except (ValueError, TypeError):

                                gagal.append(str(baris.get("id_pelanggan", "-")))

                                continue

                            kelas, prob = predict(
                                model,
                                nilai_fitur
                            )

                            hasil_prediksi.append({
                                "id_pelanggan": baris["id_pelanggan"],
                                "download_speed": nilai_fitur[0],
                                "upload_speed": nilai_fitur[1],
                                "latency": nilai_fitur[2],
                                "packet_loss": nilai_fitur[3],
                                "skor_keluhan": nilai_fitur[4],
                                "label_kelas": baris["label_kelas"],
                                "Hasil Klasifikasi": kelas
                            })

                            berhasil += 1

                        # Simpan hasil ke session_state supaya tidak hilang
                        # ketika tombol download di bawah ini diklik (yang
                        # memicu rerun halaman).
                        st.session_state["hasil_import_csv"] = {
                            "file": file_csv.name,
                            "berhasil": berhasil,
                            "gagal": gagal,
                            "hasil_prediksi": hasil_prediksi,
                            "tersimpan_db": False
                        }


                    # ==========================================
                    # TAMPILKAN HASIL (persisten via session_state)
                    # ==========================================

                    hasil_tersimpan = st.session_state.get("hasil_import_csv")

                    if hasil_tersimpan and hasil_tersimpan["file"] == file_csv.name:

                        st.success(
                            f"{hasil_tersimpan['berhasil']} berhasil diklasifikasi. "
                            "Silakan periksa hasilnya di bawah, lalu klik **Simpan Data** jika ingin "
                            "datanya tercatat di Data User dan Riwayat."
                        )

                        st.markdown("## Hasil Klasifikasi")

                        df_hasil = pd.DataFrame(hasil_tersimpan["hasil_prediksi"])

                        if len(df_hasil) > 0:

                            styled_df = (
                                df_hasil.style
                                .format({
                                    "download_speed": "{:.2f}",
                                    "upload_speed": "{:.2f}",
                                    "latency": "{:.0f}",
                                    "packet_loss": "{:.2f}",
                                    "skor_keluhan": "{:.2f}"
                                })
                                .map(
                                    warna_hasil,
                                    subset=["Hasil Klasifikasi"]
                                )
                            )

                            st.dataframe(styled_df, use_container_width=True)

                            st.download_button(
                                "Download Hasil Klasifikasi (CSV)",
                                df_hasil.to_csv(index=False).encode(),
                                f"hasil_klasifikasi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                "text/csv",
                                use_container_width=True
                            )

                            if hasil_tersimpan.get("tersimpan_db"):

                                st.info(
                                    "Data hasil import ini sudah tersimpan di Data User dan Riwayat."
                                )

                            else:

                                if st.button(
                                    "Simpan Data",
                                    use_container_width=True,
                                    type="primary"
                                ):

                                    jumlah_simpan = 0

                                    for baris in hasil_tersimpan["hasil_prediksi"]:

                                        user_id = get_or_create_user_by_nama(
                                            baris["id_pelanggan"]
                                        )

                                        insert_hasil(
                                            user_id,
                                            baris["download_speed"],
                                            baris["upload_speed"],
                                            baris["latency"],
                                            baris["packet_loss"],
                                            baris["skor_keluhan"],
                                            baris["Hasil Klasifikasi"],
                                            datetime.now().strftime("%Y-%m-%d %H:%M"),
                                            baris.get("label_kelas")
                                        )

                                        jumlah_simpan += 1

                                    hasil_tersimpan["tersimpan_db"] = True

                                    st.session_state["hasil_import_csv"] = hasil_tersimpan

                                    st.success(
                                        f"{jumlah_simpan} data berhasil disimpan ke Data User dan Riwayat."
                                    )

                                    st.rerun()

                        if hasil_tersimpan["gagal"]:
                            st.warning(
                                "Baris berikut dilewati karena data numerik tidak valid (id_pelanggan): "
                                + ", ".join(hasil_tersimpan["gagal"])
                            )
