import sqlite3

DATABASE = "wifi.db"


def get_connection():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # ===========================
    # Tabel User
    # ===========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user'
    )
    """)

    # ===========================
    # Tabel Hasil Klasifikasi
    # ===========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hasil(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        download_speed REAL,
        upload_speed REAL,
        latency REAL,
        packet_loss REAL,
        skor_keluhan REAL,
        hasil TEXT,
        tanggal TEXT,
        label_kelas TEXT,

        FOREIGN KEY(user_id)
        REFERENCES users(id)
    )
    """)

    conn.commit()

    # ===========================
    # Migrasi: pastikan kolom label_kelas ada
    # (untuk database wifi.db lama yang dibuat sebelum kolom ini ditambahkan)
    # ===========================
    cursor.execute("PRAGMA table_info(hasil)")

    kolom_ada = [baris["name"] for baris in cursor.fetchall()]

    if "label_kelas" not in kolom_ada:

        cursor.execute("ALTER TABLE hasil ADD COLUMN label_kelas TEXT")

        conn.commit()

    # ===========================
    # Membuat akun admin otomatis
    # ===========================
    cursor.execute("SELECT * FROM users WHERE email=?", ("admin@gmail.com",))

    if cursor.fetchone() is None:

        import hashlib

        password = hashlib.sha256("admin123".encode()).hexdigest()

        cursor.execute("""
        INSERT INTO users
        (nama,email,password,role)
        VALUES
        (?,?,?,?)
        """, (
            "Administrator",
            "admin@gmail.com",
            password,
            "admin"
        ))

        conn.commit()

    conn.close()

import pandas as pd


def get_all_users():

    conn = get_connection()

    df = pd.read_sql("""
        SELECT
            id,
            nama,
            email,
            role
        FROM users
        ORDER BY id DESC
    """, conn)

    conn.close()

    return df


def delete_user(user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )

    conn.commit()

    conn.close()


def get_user_by_email(email):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    return user


def insert_hasil(user_id, download_speed, upload_speed, latency, packet_loss, skor_keluhan, hasil, tanggal, label_kelas=None):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO hasil(
            user_id,
            download_speed,
            upload_speed,
            latency,
            packet_loss,
            skor_keluhan,
            hasil,
            tanggal,
            label_kelas
        )
        VALUES(?,?,?,?,?,?,?,?,?)
        """,
        (
            user_id,
            download_speed,
            upload_speed,
            latency,
            packet_loss,
            skor_keluhan,
            hasil,
            tanggal,
            label_kelas
        )
    )

    conn.commit()

    conn.close()


def get_or_create_user_by_nama(nama, role="user"):
    """
    Mencari user berdasarkan nama (dipakai untuk import CSV, kolom
    id_pelanggan dipetakan ke nama user). Jika belum ada, user baru
    akan dibuatkan otomatis dengan password default "import123".
    Mengembalikan id user (int).
    """

    import hashlib

    nama = str(nama).strip()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE nama=?",
        (nama,)
    )

    row = cursor.fetchone()

    if row is not None:

        user_id = row["id"]

        conn.close()

        return user_id

    email_slug = (
        nama.lower()
        .replace(" ", "_")
        .replace("@", "_")
    )

    email = f"{email_slug}@import.local"

    # Hindari bentrok email jika slug sudah dipakai
    cursor.execute(
        "SELECT id FROM users WHERE email=?",
        (email,)
    )

    if cursor.fetchone() is not None:
        import time
        email = f"{email_slug}_{int(time.time()*1000)}@import.local"

    password = hashlib.sha256("import123".encode()).hexdigest()

    cursor.execute(
        """
        INSERT INTO users(nama,email,password,role)
        VALUES(?,?,?,?)
        """,
        (nama, email, password, role)
    )

    conn.commit()

    user_id = cursor.lastrowid

    conn.close()

    return user_id


def delete_hasil(id_hasil):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM hasil WHERE id=?",
        (id_hasil,)
    )

    conn.commit()

    conn.close()