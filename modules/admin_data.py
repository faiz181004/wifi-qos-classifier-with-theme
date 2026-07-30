import streamlit as st
import pandas as pd

from database import (
    get_connection,
    delete_hasil
)
from modules import style


warna_hasil = style.warna_hasil_style


def show():

    style.page_header(
        "Data Klasifikasi",
        "Kelola seluruh hasil klasifikasi pengguna"
    )

    conn = get_connection()

    query = """
    SELECT

    hasil.id,

    users.nama,

    users.email,

    hasil.download_speed,

    hasil.upload_speed,

    hasil.latency,

    hasil.packet_loss,

    hasil.skor_keluhan,

    hasil.label_kelas,

    hasil.hasil,

    hasil.tanggal

    FROM hasil

    JOIN users

    ON hasil.user_id=users.id

    ORDER BY hasil.id DESC

    """

    df = pd.read_sql(query, conn)

    conn.close()

    if len(df)==0:

        st.info("Belum ada data.")

        return

    cari = st.text_input("Cari berdasarkan nama atau email")

    if cari:

        df=df[
            df["nama"].str.contains(cari,case=False)
            |
            df["email"].str.contains(cari,case=False)
        ]

    styled_df = (
    df.style
    .format({
        "download_speed": "{:.2f}",
        "upload_speed": "{:.2f}",
        "latency": "{:.2f}",
        "packet_loss": "{:.2f}",
        "skor_keluhan": "{:.2f}",
    })
    .map(warna_hasil, subset=["hasil"])
    .map(warna_hasil, subset=["label_kelas"])
)

    st.dataframe(
        styled_df,
        use_container_width=True
    )

    st.divider()

    pilih = st.selectbox(

        "Pilih ID Data",

        df["id"]

    )

    if st.button("Hapus Data"):

        delete_hasil(pilih)

        st.success("Data berhasil dihapus")

        st.rerun()

    csv=df.to_csv(index=False).encode()

    st.download_button(

        "Download CSV",

        csv,

        "hasil.csv",

        "text/csv"

    )