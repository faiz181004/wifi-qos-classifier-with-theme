import streamlit as st
import pandas as pd
import plotly.express as px

from database import get_connection
from modules import style


def show(hasil_model):

    style.page_header(
        "Dashboard Admin",
        f"Selamat datang kembali, {st.session_state['nama']}"
    )

    conn = get_connection()

    total_user = pd.read_sql(
        "SELECT COUNT(*) total FROM users WHERE role='user'",
        conn
    ).iloc[0]["total"]

    total_data = pd.read_sql(
        "SELECT COUNT(*) total FROM hasil",
        conn
    ).iloc[0]["total"]

    distribusi = pd.read_sql("""
    SELECT
        hasil,
        COUNT(*) AS jumlah
    FROM hasil
    GROUP BY hasil
    """, conn)

    conn.close()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Jumlah User",
        total_user
    )

    c2.metric(
        "Total Klasifikasi",
        total_data
    )

    c3.metric(
        "Akurasi Model",
        f"{hasil_model['akurasi']*100:.2f}%"
    )

    st.divider()

    st.write("""
    Aplikasi ini digunakan untuk mengklasifikasikan kualitas layanan WiFi
    ke dalam empat kategori berdasarkan data yang telah tersimpan.
    """)

    st.subheader("Distribusi Data per Kelas")

    urutan = [
    "Buruk",
    "Sedang",
    "Baik",
    "Sangat Baik"
    ]

    distribusi = (
        distribusi
        .set_index("hasil")
        .reindex(urutan, fill_value=0)
        .reset_index()
    )

    fig = px.bar(
    distribusi,
    x="hasil",
    y="jumlah",
    text="jumlah",
    color_discrete_sequence=[style.PRIMARY]
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        title="Distribusi Data per Kelas",
        xaxis_title="Kategori",
        yaxis_title="Jumlah Data",
        showlegend=False,
        height=450,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    