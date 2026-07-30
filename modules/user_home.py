
import streamlit as st
from modules import style

def card(title, body):
    st.markdown(f"""
    <div style="background:{style.CARD_BG};border:1px solid {style.BORDER};border-radius:16px;padding:20px;height:230px">
    <h4 style="margin-top:0;color:white">{title}</h4>
    <div style="color:{style.TEXT_MUTED};line-height:1.8">{body}</div>
    </div>
    """, unsafe_allow_html=True)

def show(df_bersih, hasil_model, LABEL, URUTAN_KELAS, nama_user):
    style.page_header("Beranda","Media Elektronik Kerinci — Layanan Internet WiFi")

    st.markdown(f"""
    <h1 style="margin:0;color:white">👋 Halo, {nama_user}</h1>
    <p style="font-size:17px;color:{style.TEXT_MUTED};line-height:1.8">
    Selamat datang di aplikasi klasifikasi kualitas layanan WiFi.
    Semoga aktivitas Anda hari ini berjalan lancar.
    </p>
    """, unsafe_allow_html=True)

    st.write("")
    st.subheader("Tentang Aplikasi")
    c1,c2=st.columns(2)

    with c1:
        card("Parameter yang Digunakan",
        "• Download Speed<br>"
        "• Upload Speed<br>"
        "• Latency<br>"
        "• Packet Loss<br>"
        "• Keluhan Pengguna")

    with c2:
        card("Hasil Klasifikasi",
        "Sangat Baik<br>"
        "Baik<br>"
        "Sedang<br>"
        " Buruk")

    st.write("")
    st.subheader("Cara Menggunakan")

    st.markdown("""
    <div style="background:{style.CARD_BG};border:1px solid {style.BORDER};border-radius:16px;padding:20px">
    <ol style="color:{style.TEXT_MUTED};font-size:16px;line-height:2">
    <li>Pilih menu <b>Input Data</b>.</li>
    <li>Masukkan hasil Speedtest dan data keluhan.</li>
    <li>Klik <b>Jalankan Klasifikasi</b>.</li>
    <li>Lihat hasil pada menu <b>Hasil Saya</b>.</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
