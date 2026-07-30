import streamlit as st
from modules import style


def kualitas_jaringan(download, upload, latency, packet_loss):

    skor = 0

    # Download
    if download >= 8.5:
        skor += 3
    elif download >= 6:
        skor += 2
    elif download >= 3:
        skor += 1

    # Upload
    if upload >= 4:
        skor += 3
    elif upload >= 2:
        skor += 2
    elif upload >= 1:
        skor += 1

    # Latency
    if latency <= 30:
        skor += 3
    elif latency <= 70:
        skor += 2
    elif latency <= 150:
        skor += 1

    # Packet Loss
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


# Peta warna berdasarkan label kelas, dipakai di beberapa komponen
WARNA_KELAS = {
    "Sangat Baik": style.SUCCESS,
    "Baik": style.SUCCESS,
    "Sedang": style.WARNING,
    "Buruk": style.DANGER
}


def _warna(label):
    return WARNA_KELAS.get(label, style.PRIMARY)


def _kartu_metrik(icon, label, value):
    """Kartu metrik kecil bergaya, pengganti st.metric bawaan agar lebih rapi."""

    st.markdown(
        f"""
        <div style="
            background:{style.CARD_BG};
            border:1px solid {style.BORDER};
            border-radius:12px;
            padding:0.9rem 1rem;
            text-align:center;
        ">
            <div style="font-size:1.5rem;line-height:1;margin-bottom:0.3rem;">{icon}</div>
            <div style="color:{style.TEXT_MUTED};font-size:0.78rem;font-weight:600;letter-spacing:0.3px;text-transform:uppercase;">{label}</div>
            <div style="font-size:1.25rem;font-weight:700;color:{style.TEXT};margin-top:0.15rem;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def _kartu_analisis(judul, label_hasil):
    """Kartu badge untuk hasil analisis (jaringan / keluhan)."""

    warna = _warna(label_hasil)

    st.markdown(
        f"""
        <div style="
            background:{style.CARD_BG};
            border:1px solid {style.BORDER};
            border-radius:12px;
            padding:1rem 1.1rem;
            height:100%;
        ">
            <div style="color:{style.TEXT_MUTED};font-size:0.82rem;font-weight:600;margin-bottom:0.6rem;">{judul}</div>
            <span style="
                display:inline-block;
                background:{warna}22;
                color:{warna};
                border:1px solid {warna}55;
                padding:4px 14px;
                border-radius:999px;
                font-weight:700;
                font-size:0.95rem;
            ">{label_hasil}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def _bar_probabilitas(kelas, nilai):
    """Bar probabilitas custom (HTML/CSS) — tidak bergantung pada
    struktur DOM internal st.progress, sehingga tampil konsisten dan
    diwarnai sesuai kelasnya masing-masing."""

    warna = _warna(kelas)
    persen = max(0.0, min(100.0, float(nilai) * 100))

    st.markdown(
        f"""
        <div style="margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="font-weight:700;color:{style.TEXT};">{kelas}</span>
                <span style="color:{style.TEXT_MUTED};font-weight:600;">{persen:.2f}%</span>
            </div>
            <div style="background:{style.BORDER};border-radius:8px;height:12px;overflow:hidden;">
                <div style="
                    width:{persen}%;
                    height:100%;
                    background:{warna};
                    border-radius:8px;
                    transition:width 0.4s ease;
                "></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def show():

    style.page_header(
        "Hasil Klasifikasi",
        "Ringkasan hasil analisis kualitas WiFi Anda"
    )

    if "hasil_prediksi" not in st.session_state:

        st.warning("Belum ada hasil klasifikasi.")

        return

    data = st.session_state["hasil_prediksi"]

    # ==========================================================
    # HERO: HASIL AKHIR (ditampilkan paling atas)
    # ==========================================================

    warna_final = _warna(data["kelas"])

    st.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg,{warna_final}22,{warna_final}08);
            border:2px solid {warna_final};
            border-radius:18px;
            padding:1.6rem;
            text-align:center;
            margin-bottom:1.5rem;
        ">
            <div style="color:{style.TEXT_MUTED};font-size:0.85rem;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:0.4rem;">
                Hasil Akhir · Gaussian Naïve Bayes
            </div>
            <div style="color:{warna_final};font-size:2.1rem;font-weight:800;">
                {data["kelas"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==========================================================
    # INFORMASI JARINGAN
    # ==========================================================

    st.subheader("Informasi Jaringan")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        _kartu_metrik("", "Download", f'{data["download"]:.2f} Mbps')

    with c2:
        _kartu_metrik("", "Upload", f'{data["upload"]:.2f} Mbps')

    with c3:
        _kartu_metrik("", "Latency", f'{data["latency"]:.2f} ms')

    with c4:
        _kartu_metrik("", "Packet Loss", f'{data["packet_loss"]:.2f}%')

    st.write("")

    hasil_jaringan = kualitas_jaringan(
        data["download"],
        data["upload"],
        data["latency"],
        data["packet_loss"]
    )

    hasil_keluhan = kualitas_keluhan(
        data["skor_keluhan"]
    )

    a1, a2 = st.columns(2)

    with a1:
        _kartu_analisis("Analisis Informasi Jaringan", hasil_jaringan)

    with a2:
        _kartu_analisis("Analisis Keluhan Pengguna", hasil_keluhan)

    st.divider()

    # ==========================================================
    # HASIL KUESIONER
    # ==========================================================

    st.subheader("Hasil Kuesioner")

    pertanyaan = [
        ("Internet Lambat", data["q1"]),
        ("Internet Terputus", data["q2"]),
        ("Lag", data["q3"]),
        ("WiFi Tidak Stabil", data["q4"]),
        ("Hubungi Teknisi", data["q5"]),
    ]

    kolom_q = st.columns(5)

    for kolom, (label, nilai) in zip(kolom_q, pertanyaan):
        with kolom:
            st.markdown(
                f"""
                <div style="
                    background:{style.CARD_BG};
                    border:1px solid {style.BORDER};
                    border-radius:10px;
                    padding:0.7rem 0.4rem;
                    text-align:center;
                ">
                    <div style="font-size:1.3rem;font-weight:800;color:{style.PRIMARY};">{nilai}</div>
                    <div style="color:{style.TEXT_MUTED};font-size:0.72rem;margin-top:0.2rem;">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    _kartu_metrik("", "Skor Keluhan", data["skor_keluhan"])

    st.divider()

    # ==========================================================
    # PROBABILITAS
    # ==========================================================

    st.subheader("Probabilitas")

    prob = data["prob"]

    for kelas, nilai in sorted(prob.items(), key=lambda x: x[1], reverse=True):

        _bar_probabilitas(kelas, nilai)
