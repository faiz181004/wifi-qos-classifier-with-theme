import streamlit as st


# ==========================================================
# PALET WARNA — Dark Navy / Indigo & Light (terinspirasi dashboard modern)
# ==========================================================

THEMES = {
    "dark": dict(
        PRIMARY        = "#4848D1",
        PRIMARY_HOVER  = "#3E3EC3",
        PRIMARY_SOFT   = "rgba(108, 107, 245, 0.16)",
        PRIMARY_SHADOW = "rgba(108, 107, 245, 0.28)",

        SUCCESS      = "#22C55E",
        SUCCESS_SOFT = "rgba(34, 197, 94, 0.16)",

        WARNING      = "#EAB308",
        WARNING_SOFT = "rgba(234, 179, 8, 0.16)",

        DANGER      = "#F04747",
        DANGER_SOFT = "rgba(240, 71, 71, 0.16)",

        BG          = "#111525",     # background utama, navy sangat gelap
        SIDEBAR_BG  = "#0E142E",
        CARD_BG     = "#131730",     # kartu, sedikit lebih terang dari BG
        CARD_BG_2   = "#171C3A",     # kartu level kedua / hover
        BORDER      = "#232946",
        TEXT        = "#E9EBF7",
        TEXT_MUTED  = "#8B92B0",
    ),
    "light": dict(
        PRIMARY        = "#3F31D4",
        PRIMARY_HOVER  = "#3E3EC3",
        PRIMARY_SOFT   = "rgba(72, 72, 209, 0.10)",
        PRIMARY_SHADOW = "rgba(72, 72, 209, 0.18)",

        SUCCESS      = "#16A34A",
        SUCCESS_SOFT = "rgba(22, 163, 74, 0.12)",

        WARNING      = "#CA8A04",
        WARNING_SOFT = "rgba(202, 138, 4, 0.12)",

        DANGER      = "#DC2626",
        DANGER_SOFT = "rgba(220, 38, 38, 0.12)",

        BG          = "#E3F2FD",     # background utama, terang
        SIDEBAR_BG  = "#BBD0E1",
        CARD_BG     = "#BBD0E1",     # kartu
        CARD_BG_2   = "#F1F2F9",     # kartu level kedua / hover
        BORDER      = "#E2E4F0",
        TEXT        = "#101011",
        TEXT_MUTED  = "#0E0E0E",
    ),
}

# Nilai default (akan ditimpa oleh init_theme() saat aplikasi berjalan)
PRIMARY        = THEMES["dark"]["PRIMARY"]
PRIMARY_HOVER  = THEMES["dark"]["PRIMARY_HOVER"]
PRIMARY_SOFT   = THEMES["dark"]["PRIMARY_SOFT"]
PRIMARY_SHADOW = THEMES["dark"]["PRIMARY_SHADOW"]

SUCCESS      = THEMES["dark"]["SUCCESS"]
SUCCESS_SOFT = THEMES["dark"]["SUCCESS_SOFT"]

WARNING      = THEMES["dark"]["WARNING"]
WARNING_SOFT = THEMES["dark"]["WARNING_SOFT"]

DANGER      = THEMES["dark"]["DANGER"]
DANGER_SOFT = THEMES["dark"]["DANGER_SOFT"]

BG          = THEMES["dark"]["BG"]
SIDEBAR_BG  = THEMES["dark"]["SIDEBAR_BG"]
CARD_BG     = THEMES["dark"]["CARD_BG"]
CARD_BG_2   = THEMES["dark"]["CARD_BG_2"]
BORDER      = THEMES["dark"]["BORDER"]
TEXT        = THEMES["dark"]["TEXT"]
TEXT_MUTED  = THEMES["dark"]["TEXT_MUTED"]


# ==========================================================
# MANAJEMEN TEMA (LIGHT / DARK)
# ==========================================================

def _apply_palette(nama_tema):
    """Menimpa variabel warna modul ini sesuai tema yang dipilih."""

    palette = THEMES.get(nama_tema, THEMES["dark"])
    globals().update(palette)


def init_theme():
    """Dipanggil sekali di awal render setiap halaman agar warna
    modul ini sesuai dengan tema yang tersimpan di session_state."""

    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"

    _apply_palette(st.session_state["theme"])


def toggle_theme():
    """Membalik tema aktif antara light <-> dark."""

    st.session_state["theme"] = (
        "light" if st.session_state.get("theme", "dark") == "dark" else "dark"
    )
    _apply_palette(st.session_state["theme"])


def is_dark():
    return st.session_state.get("theme", "dark") == "dark"


def theme_toggle_button(key="theme_toggle"):
    """Menampilkan tombol untuk mengubah tema light/dark dan
    langsung memuat ulang halaman saat ditekan."""

    label = "☀️ Light" if is_dark() else "🌙 Dark"

    if st.button(label, key=key, use_container_width=True, help="Ganti tema tampilan"):
        toggle_theme()
        st.rerun()


# ==========================================================
# CSS GLOBAL
# ==========================================================

def load_css():

    st.markdown(
        f"""
        <style>

        /* ---------- Base ---------- */
        .stApp {{
            background: {BG};
            color: {TEXT};
            transition: background 0.2s ease, color 0.2s ease;
        }}

        /* ---------- Tombol ganti tema (sidebar) ---------- */
        section[data-testid="stSidebar"] div[data-testid="stButton"] button {{
            transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
        }}

        html, body, [class*="css"] {{
            font-family: "Inter", "Segoe UI", sans-serif;
            color: {TEXT};
        }}

        #MainMenu, footer {{
            visibility: hidden;
        }}

        header[data-testid="stHeader"] {{
            background: transparent;
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {{
            background: {SIDEBAR_BG};
            border-right: 1px solid {BORDER};
        }}

        section[data-testid="stSidebar"] > div {{
            padding-top: 0.5rem;
        }}

        section[data-testid="stSidebar"] * {{
            color: {TEXT} !important;
        }}

        /* ---------- Sidebar: menu (radio) bergaya nav item ala dashboard ---------- */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {{
            display: none;   /* sembunyikan label "Menu" bawaan */
        }}

        section[data-testid="stSidebar"] div[role="radiogroup"] {{
            gap: 4px;
            display: flex;
            flex-direction: column;
        }}

        section[data-testid="stSidebar"] div[role="radiogroup"] label {{
            position: relative;
            border-radius: 10px;
            padding: 10px 14px 10px 16px;
            margin: 0;
            font-weight: 500;
            transition: background 0.15s ease, color 0.15s ease;
            cursor: pointer;
        }}

        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
            background: {CARD_BG};
        }}

        /* sembunyikan bulatan radio bawaan */
        section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {{
            display: none;
        }}

        /* item aktif: pill indigo + garis aksen kiri, meniru referensi desain */
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
            background: {PRIMARY_SOFT};
        }}

        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {{
            color: {PRIMARY} !important;
            font-weight: 700 !important;
        }}

        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked)::before {{
            content: "";
            position: absolute;
            left: -1px;
            top: 8px;
            bottom: 8px;
            width: 3px;
            border-radius: 3px;
            background: {PRIMARY};
        }}

        section[data-testid="stSidebar"] hr {{
            border-color: {BORDER};
        }}

        section[data-testid="stSidebar"] button {{
            background: transparent !important;
            border: 1px solid {BORDER} !important;
            color: {TEXT} !important;
            border-radius: 10px !important;
        }}

        section[data-testid="stSidebar"] button:hover {{
            border-color: {DANGER} !important;
            color: {DANGER} !important;
        }}

        /* ---------- Headings & text ---------- */
        h1, h2, h3, h4 {{
            color: {TEXT};
            font-weight: 700;
            letter-spacing: -0.01em;
        }}

        p, span, label, li {{
            color: {TEXT};
        }}

        /* ---------- Buttons (main area) ---------- */
        div[data-testid="stAppViewContainer"] .stButton button {{
            background: {PRIMARY};
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 0.55rem 1.1rem;
            font-weight: 600;
            box-shadow: 0 4px 14px {PRIMARY_SHADOW};
            transition: background 0.15s ease, transform 0.1s ease;
        }}

        div[data-testid="stAppViewContainer"] .stButton button:hover {{
            background: {PRIMARY_HOVER};
            transform: translateY(-1px);
        }}

        div[data-testid="stAppViewContainer"] .stDownloadButton button {{
            background: transparent;
            color: {TEXT};
            border: 1px solid {BORDER};
            border-radius: 10px;
            font-weight: 600;
        }}

        div[data-testid="stAppViewContainer"] .stDownloadButton button:hover {{
            border-color: {PRIMARY};
            color: {PRIMARY};
        }}

        /* ---------- Inputs ---------- */
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] > div,
        .stTextArea textarea {{
            background: {CARD_BG} !important;
            color: {TEXT} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 10px !important;
        }}

        /* ---------- Tabs ---------- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            border-bottom: 1px solid {BORDER};
        }}

        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            border-radius: 8px 8px 0 0;
            padding: 8px 16px;
            font-weight: 600;
            color: {TEXT_MUTED};
        }}

        .stTabs [aria-selected="true"] {{
            color: {PRIMARY} !important;
            border-bottom: 2px solid {PRIMARY};
        }}

        /* ---------- Metric cards ---------- */
        div[data-testid="stMetric"] {{
            background: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 1rem 1.1rem;
        }}

        div[data-testid="stMetricLabel"] {{
            color: {TEXT_MUTED} !important;
            font-weight: 600 !important;
        }}

        div[data-testid="stMetricValue"] {{
            font-weight: 700 !important;
        }}

        /* ---------- Dataframe / table ---------- */
        div[data-testid="stDataFrame"] {{
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid {BORDER};
        }}

        /* ---------- Alerts ---------- */
        div[data-testid="stAlert"] {{
            border-radius: 12px;
        }}

        /* ---------- Progress bar ---------- */
        div[data-testid="stProgressBarTrack"] {{
            background: {BORDER} !important;
        }}

        div[data-testid="stProgressBarTrack"] > div {{
            background: {PRIMARY} !important;
        }}

        /* ---------- File uploader ---------- */
        section[data-testid="stFileUploaderDropzone"] {{
            background: {CARD_BG};
            border: 1px dashed {BORDER};
            border-radius: 12px;
        }}

        /* ---------- Divider ---------- */
        hr {{
            border-color: {BORDER};
            margin: 1.1rem 0;
        }}

        /* ---------- Custom card ---------- */
        .app-card {{
            background: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
        }}

        .app-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# KOMPONEN BANTUAN
# ==========================================================

def page_header(title, subtitle=None):
    """Header halaman: judul + subjudul, tanpa ikon."""

    st.markdown(
        f"""
        <div style="font-size:1.6rem;font-weight:700;color:{TEXT};margin-bottom:0.2rem;letter-spacing:-0.01em;">{title}</div>
        {f'<div style="color:{TEXT_MUTED};font-size:0.92rem;margin-bottom:0.8rem;">{subtitle}</div>' if subtitle else ''}
        <div style="height:1px;background:{BORDER};margin:0.8rem 0 1.2rem 0;"></div>
        """,
        unsafe_allow_html=True
    )


def badge(text, color=SUCCESS):
    return f'<span class="app-badge" style="background:{color}29;color:{color};">{text}</span>'


def card_open():
    st.markdown('<div class="app-card">', unsafe_allow_html=True)


def card_close():
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================
# WARNA KELAS HASIL — dipakai bersama di tabel admin/ekspor
# ==========================================================

def warna_hasil_style(val):
    """Mengembalikan CSS pandas Styler untuk kolom kelas hasil,
    dengan tone yang konsisten dengan tema gelap aplikasi."""

    if val == "Buruk":
        return f"background-color:{DANGER_SOFT}; color:{DANGER}; font-weight:700;"

    elif val == "Sedang":
        return f"background-color:{WARNING_SOFT}; color:{WARNING}; font-weight:700;"

    elif val == "Baik":
        return f"background-color:{SUCCESS_SOFT}; color:{SUCCESS}; font-weight:700;"

    elif val == "Sangat Baik":
        return f"background-color:{SUCCESS}; color:#08130D; font-weight:700;"

    return ""
