import streamlit as st

from database import (
    get_all_users,
    delete_user
)
from modules import style


def show():

    style.page_header(
        "Data User",
        "Kelola akun pengguna terdaftar"
    )

    df = get_all_users()

    if len(df) == 0:

        st.info("Belum ada user.")

        return

    cari = st.text_input("Cari nama atau email user")

    if cari:

        df = df[
            df["nama"].str.contains(cari, case=False)
            |
            df["email"].str.contains(cari, case=False)
        ]

    st.dataframe(
        df,
        use_container_width=True
    )

    st.divider()

    st.subheader("Hapus User")

    user = st.selectbox(
        "Pilih ID",
        df["id"]
    )

    if st.button("Hapus User"):

        delete_user(user)

        st.success("User berhasil dihapus")

        st.rerun()