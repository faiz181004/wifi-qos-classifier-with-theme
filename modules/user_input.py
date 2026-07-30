import math

import streamlit as st
import streamlit.components.v1 as components

from database import get_connection
from datetime import datetime
from modules import style


# ==========================================================
# SPEED TEST (real network measurement — CLIENT-SIDE via JavaScript)
#
# CATATAN PENTING (riwayat perbaikan):
#   v1: memakai library Python "speedtest-cli" -> berjalan di SERVER,
#       bukan di device pengguna. SALAH, sudah diganti.
#   v2: memakai library pihak ketiga "streamlit-javascript" untuk
#       mengirim hasil JS balik ke Python -> TERNYATA tidak
#       kompatibel dengan versi Streamlit terbaru (protokol
#       komponennya berubah) -> hasil tidak pernah sampai ke Python.
#   v3: mencoba mengirim hasil lewat navigasi URL (window.top.location)
#       -> TERNYATA browser MEMBLOKIR TOTAL iframe menavigasi frame
#       utama, karena Streamlit tidak mengaktifkan izin
#       "allow-top-navigation(-by-user-activation)" di sandbox
#       komponennya. Ini berlaku bahkan untuk klik asli pengguna,
#       dan tidak bisa diakali dari sisi kode JS sama sekali.
#   v4: JS hanya menampilkan hasil sebagai teks, pengguna menyalin
#       manual ke kolom input. Selalu berhasil, tapi butuh 1 langkah
#       manual yang diminta dihilangkan.
#   v5 (SEKARANG): mencoba mengisi otomatis kolom number_input yang
#       SUNGGUHAN di halaman utama, langsung dari JS di dalam iframe,
#       memakai akses DOM window.top (diizinkan karena sandbox iframe
#       ini punya "allow-same-origin") -- mencari elemen <input> lewat
#       teks labelnya, lalu mengisi nilainya + memicu event input/
#       change/blur seolah diketik pengguna, supaya React (yang
#       dipakai Streamlit) mendeteksi perubahan dan mengirimkannya ke
#       Python secara normal lewat mekanisme bawaan number_input.
#       CATATAN JUJUR: ini bergantung pada struktur HTML internal
#       Streamlit (atribut data-testid dsb) yang TIDAK dijamin stabil
#       antar versi. Kolom input tetap ditampilkan sebagai cadangan
#       manual kalau trik ini gagal di environment Anda.
# ==========================================================


def _bangun_html_speedtest():
    """HTML+JS yang dijalankan di browser pengguna untuk mengukur
    kecepatan internet asli mereka. Menampilkan gauge animasi selagi
    mengukur, lalu mencoba mengisi otomatis kolom number_input di
    halaman utama (lihat catatan v5 di atas). Kolom hasil tetap
    ditampilkan sebagai cadangan kalau auto-isi gagal."""

    return """
    <div id="gaugeBox" style="display:flex;flex-direction:column;align-items:center;">
        <svg width="220" height="140" viewBox="0 0 300 200">
            <path d="M 32,150 A 118,118 0 0 1 268,150"
                  fill="none" stroke="#2a2e3f" stroke-width="14" stroke-linecap="round" />
            <g>
                <animateTransform attributeName="transform" type="rotate"
                    values="-75 150 150; 75 150 150; -75 150 150"
                    keyTimes="0;0.5;1" dur="1.6s" repeatCount="indefinite" />
                <line x1="150" y1="150" x2="150" y2="40"
                      stroke="#6d7dfc" stroke-width="4" stroke-linecap="round" />
                <circle cx="150" cy="150" r="7" fill="#6d7dfc" />
            </g>
        </svg>
    </div>

    <div id="status" style="
        font-family: -apple-system, sans-serif;
        color: #b5b8c5;
        font-size: 0.9rem;
        text-align: center;
        padding: 0.3rem;
    ">Mengukur kecepatan internet Anda...</div>

    <div id="hasilBox" style="
        font-family: -apple-system, sans-serif;
        text-align: center;
    "></div>

    <script>
    (async function () {
        const statusEl = document.getElementById("status");
        const hasilBox = document.getElementById("hasilBox");
        const gaugeBox = document.getElementById("gaugeBox");

        function denganTimeout(promise, ms, pesan) {
            return Promise.race([
                promise,
                new Promise((_, reject) => setTimeout(() => reject(new Error(pesan)), ms))
            ]);
        }

        function kartu(label, nilai, satuan) {
            return `
                <div style="display:inline-block;margin:0.4rem 0.6rem;padding:0.5rem 1rem;
                            background:#1a1d29;border:1px solid #2a2e3f;border-radius:10px;min-width:110px;">
                    <div style="color:#8a8fa3;font-size:0.72rem;text-transform:uppercase;">${label}</div>
                    <div style="color:#e8eaf0;font-size:1.3rem;font-weight:700;">${nilai}
                        <span style="font-size:0.7rem;color:#8a8fa3;font-weight:400;">${satuan}</span>
                    </div>
                </div>
            `;
        }

        // --- Trik auto-isi: cari input asli Streamlit lewat teks
        // labelnya, lalu isi nilainya + picu event seolah diketik
        // pengguna, supaya React/Streamlit mendeteksi perubahannya. ---
        function setNilaiInputReact(inputEl, nilai) {
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            setter.call(inputEl, nilai);
            inputEl.dispatchEvent(new Event("input", { bubbles: true }));
            inputEl.dispatchEvent(new Event("change", { bubbles: true }));
            inputEl.blur();
        }

        function cariInputLabel(doc, teksLabel) {
            const kandidat = doc.querySelectorAll("label, p, span");
            for (const el of kandidat) {
                const teks = (el.textContent || "").trim();
                if (teks === teksLabel || teks.startsWith(teksLabel)) {
                    const kontainer = el.closest('[data-testid="stNumberInput"]') || el.closest("div");
                    if (kontainer) {
                        const input = kontainer.querySelector('input[type="number"]');
                        if (input) return input;
                    }
                }
            }
            return null;
        }

        function cobaIsiOtomatis(hasil) {
            try {
                const topDoc = window.top.document;
                const peta = {
                    "Download Speed (Mbps)": hasil.download,
                    "Upload Speed (Mbps)": hasil.upload,
                    "Latency / Ping (ms)": hasil.ping,
                };
                let jumlahBerhasil = 0;
                for (const [label, nilai] of Object.entries(peta)) {
                    const input = cariInputLabel(topDoc, label);
                    if (input) {
                        setNilaiInputReact(input, nilai);
                        jumlahBerhasil++;
                    }
                }
                return jumlahBerhasil;
            } catch (e) {
                return 0;
            }
        }

        function tampilkanHasil(d, otomatisBerhasil) {
            gaugeBox.style.display = "none";
            hasilBox.innerHTML =
                kartu("Download", d.download, "Mbps") +
                kartu("Upload", d.upload, "Mbps") +
                kartu("Ping", d.ping, "ms") +
                kartu("Jitter", d.jitter, "ms") +
                (otomatisBerhasil >= 3
                    ? `<div style="margin-top:0.6rem;color:#22c55e;font-size:0.82rem;font-weight:600;">
                          &#10003; Kolom di bawah sudah otomatis terisi
                       </div>`
                    : `<div style="margin-top:0.6rem;color:#8a8fa3;font-size:0.78rem;">
                          Auto-isi tidak berhasil di browser ini -- silakan salin angka di atas ke kolom di bawah manual.
                       </div>`);
        }

        try {
            // --- PING & JITTER ---
            const pingSamples = [];
            for (let i = 0; i < 5; i++) {
                const t0 = performance.now();
                await fetch("https://speed.cloudflare.com/__down?bytes=0", { cache: "no-store" });
                pingSamples.push(performance.now() - t0);
            }
            const avgPing = pingSamples.reduce((a, b) => a + b, 0) / pingSamples.length;
            const variance = pingSamples.reduce((a, b) => a + Math.pow(b - avgPing, 2), 0) / pingSamples.length;
            const jitter = Math.sqrt(variance);

            // --- DOWNLOAD ---
            statusEl.textContent = "Mengukur kecepatan unduh...";
            const downloadBytes = 20000000;
            const dt0 = performance.now();
            const downRes = await denganTimeout(
                fetch("https://speed.cloudflare.com/__down?bytes=" + downloadBytes, { cache: "no-store" }),
                20000, "timeout download"
            );
            await downRes.arrayBuffer();
            const downloadMbps = (downloadBytes * 8 / 1e6) / ((performance.now() - dt0) / 1000);

            // --- UPLOAD ---
            statusEl.textContent = "Mengukur kecepatan unggah...";
            const uploadBytes = 8000000;
            const uploadData = new Uint8Array(uploadBytes);
            const ut0 = performance.now();
            await denganTimeout(
                fetch("https://speed.cloudflare.com/__up", { method: "POST", body: uploadData, cache: "no-store" }),
                20000, "timeout upload"
            );
            const uploadMbps = (uploadBytes * 8 / 1e6) / ((performance.now() - ut0) / 1000);

            statusEl.textContent = "Pengukuran selesai!";

            const hasil = {
                download: Math.round(downloadMbps * 100) / 100,
                upload: Math.round(uploadMbps * 100) / 100,
                ping: Math.round(avgPing * 100) / 100,
                jitter: Math.round(jitter * 100) / 100
            };

            const jumlahBerhasil = cobaIsiOtomatis(hasil);
            tampilkanHasil(hasil, jumlahBerhasil);

        } catch (err) {
            const pesan = err && err.message ? err.message : String(err);
            gaugeBox.style.display = "none";
            statusEl.textContent = "Speed Test gagal: " + pesan;
            hasilBox.innerHTML = `<div style="color:#ef4444;font-size:0.85rem;">
                Coba lagi, atau isi manual di kolom bawah berdasarkan aplikasi speed test lain.
            </div>`;
        }
    })();
    </script>
    """


# ==========================================================
# GAUGE (SVG speedometer, mirip tampilan Speedtest by Ookla)
# ==========================================================

def _titik_gauge(cx, cy, r, theta_deg):

    theta_rad = math.radians(theta_deg)

    x = cx + r * math.sin(theta_rad)
    y = cy - r * math.cos(theta_rad)

    return x, y


def render_gauge_loading():
    """
    Versi gauge dengan jarum yang benar-benar bergerak (mengayun bolak-balik)
    selama Speed Test sedang berjalan. Memakai animasi SVG native
    (animateTransform) supaya gerakannya presisi di koordinat viewBox,
    tidak terpengaruh skala CSS.
    """

    cx, cy = 150, 150

    html = f"""
    <div style="background:{style.CARD_BG};border:1px solid {style.BORDER};
    border-radius:14px;padding:1.6rem;display:flex;flex-direction:column;
    align-items:center;justify-content:center;gap:0.8rem;">
    <svg width="260" height="180" viewBox="0 0 300 200">
    <path d="M 32,150 A 118,118 0 0 1 268,150"
    fill="none" stroke="{style.BORDER}" stroke-width="14" stroke-linecap="round" />
    <g>
    <animateTransform attributeName="transform" type="rotate"
    values="-75 {cx} {cy}; 75 {cx} {cy}; -75 {cx} {cy}"
    keyTimes="0;0.5;1" dur="1.6s" repeatCount="indefinite" />
    <line x1="{cx}" y1="{cy}" x2="{cx}" y2="40"
    stroke="{style.PRIMARY}" stroke-width="4" stroke-linecap="round" />
    <circle cx="{cx}" cy="{cy}" r="7" fill="{style.PRIMARY}" />
    </g>
    </svg>
    <div style="color:{style.TEXT_MUTED};font-size:0.9rem;font-weight:600;">
    Mengukur kecepatan internet Anda...
    </div>
    </div>
    """

    dokumen_html = f"""
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: "Segoe UI", "Inter", sans-serif;
        }}
    </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """

    components.html(dokumen_html, height=300, scrolling=False)


def render_gauge(download, upload, ping, jitter, isp, ip, server_sponsor, server_lokasi, placeholder=False):

    cx, cy, r = 150, 150, 118

    skala_max = 1000  # Mbps, mengikuti skala log seperti Speedtest.net

    nilai_needle = 0 if placeholder else max(download or 0, 0)

    fraksi = math.log10(max(nilai_needle, 1)) / math.log10(skala_max)
    fraksi = min(max(fraksi, 0), 1)

    theta_needle = -90 + 180 * fraksi

    x1, y1 = _titik_gauge(cx, cy, r, -90)
    x2, y2 = _titik_gauge(cx, cy, r, 90)

    x_needle, y_needle = _titik_gauge(cx, cy, r - 14, theta_needle)

    # Arc terisi (dari kiri sampai posisi jarum)
    x_isi, y_isi = _titik_gauge(cx, cy, r, theta_needle)

    tanda = [0, 10, 50, 100, 200, 300, 500, 750, 1000]

    tick_svg = ""

    for v in tanda:

        f = min(max(math.log10(max(v, 1)) / math.log10(skala_max), 0), 1)
        th = -90 + 180 * f

        x_luar, y_luar = _titik_gauge(cx, cy, r + 22, th)

        label = "1g" if v == 1000 else str(v)

        tick_svg += (
            f'<text x="{x_luar:.1f}" y="{y_luar:.1f}" '
            f'text-anchor="middle" dominant-baseline="middle" '
            f'font-size="12" fill="{style.TEXT_MUTED}">{label}</text>'
        )

    nilai_download_teks = "—&nbsp;—" if placeholder or download is None else f"{download:.2f}"
    nilai_upload_teks = "—&nbsp;—" if placeholder or upload is None else f"{upload:.2f}"
    nilai_ping_teks = "—&nbsp;—" if placeholder or ping is None else f"{ping:.0f}"
    nilai_jitter_teks = "—&nbsp;—" if placeholder or not jitter else f"{jitter:.0f}"

    info_bawah = ""

    if not placeholder and (isp or server_sponsor):

        info_bawah = f"""
        <div style="display:flex;justify-content:space-between;align-items:flex-start;
                    margin-top:14px;padding-top:14px;border-top:1px solid {style.BORDER};">
            <div>
                <div style="font-weight:700;font-size:0.95rem;">{isp or '-'}</div>
                <div style="color:{style.TEXT_MUTED};font-size:0.8rem;">{ip or ''}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-weight:700;font-size:0.95rem;">{server_sponsor or '-'}</div>
                <div style="color:{style.TEXT_MUTED};font-size:0.8rem;">{server_lokasi or ''}</div>
            </div>
        </div>
        """

    html = f"""
    <div style="background:{style.CARD_BG};border:1px solid {style.BORDER};
                border-radius:14px;padding:1.4rem 1.6rem;">

        <div style="display:flex;justify-content:flex-end;align-items:center;gap:6px;
                    color:{style.TEXT_MUTED};font-size:0.85rem;font-weight:700;
                    letter-spacing:0.5px;margin-bottom:6px;">
            ⏱ SPEED TEST
        </div>

        <div style="display:flex;align-items:center;gap:1.6rem;flex-wrap:wrap;">

            <div style="flex:0 0 auto;">
                <svg width="300" height="230" viewBox="0 0 300 200">

                    <path d="M {x1:.1f},{y1:.1f} A {r},{r} 0 0 1 {x2:.1f},{y2:.1f}"
                          fill="none" stroke="{style.BORDER}" stroke-width="14"
                          stroke-linecap="round" />

                    <path d="M {x1:.1f},{y1:.1f} A {r},{r} 0 0 1 {x_isi:.1f},{y_isi:.1f}"
                          fill="none" stroke="{style.PRIMARY}" stroke-width="14"
                          stroke-linecap="round" opacity="{0.15 if placeholder else 0.9}" />

                    {tick_svg}

                    <line x1="{cx}" y1="{cy}" x2="{x_needle:.1f}" y2="{y_needle:.1f}"
                          stroke="{style.TEXT}" stroke-width="4" stroke-linecap="round" />
                    <circle cx="{cx}" cy="{cy}" r="7" fill="{style.TEXT}" />

                    <text x="{cx}" y="{cy + 40}" text-anchor="middle"
                          font-size="26" font-weight="700" fill="{style.TEXT}">
                        {"—&nbsp;—" if placeholder else f"{nilai_needle:.1f}"}
                    </text>
                    <text x="{cx}" y="{cy + 62}" text-anchor="middle"
                          font-size="12" fill="{style.TEXT_MUTED}">Mbps</text>

                </svg>
            </div>

            <div style="flex:0 0 auto;display:flex;flex-direction:column;gap:1.1rem;">
                <div>
                    <div style="color:{style.TEXT_MUTED};font-size:0.8rem;">PING</div>
                    <div style="font-size:1.6rem;font-weight:700;">{nilai_ping_teks}
                        <span style="font-size:0.8rem;color:{style.TEXT_MUTED};font-weight:400;"> ms</span>
                    </div>
                </div>
                <div>
                    <div style="color:{style.TEXT_MUTED};font-size:0.8rem;">〰️ JITTER</div>
                    <div style="font-size:1.6rem;font-weight:700;">{nilai_jitter_teks}
                        <span style="font-size:0.8rem;color:{style.TEXT_MUTED};font-weight:400;"> ms</span>
                    </div>
                </div>
            </div>

            <div style="flex:1 1 180px;display:flex;flex-direction:column;gap:0.7rem;min-width:170px;">
                <div style="background:{style.BG};border:1px solid {style.PRIMARY};border-radius:10px;
                            padding:0.7rem 0.9rem;">
                    <div style="color:{style.TEXT_MUTED};font-size:0.8rem;">⬇ UNDUH</div>
                    <div style="font-size:1.5rem;font-weight:700;">{nilai_download_teks}
                        <span style="font-size:0.75rem;color:{style.TEXT_MUTED};font-weight:400;"> Mbps</span>
                    </div>
                </div>
                <div style="background:{style.BG};border:1px solid {style.BORDER};border-radius:10px;
                            padding:0.7rem 0.9rem;">
                    <div style="color:{style.TEXT_MUTED};font-size:0.8rem;">⬆ UNGGAH</div>
                    <div style="font-size:1.5rem;font-weight:700;">{nilai_upload_teks}
                        <span style="font-size:0.75rem;color:{style.TEXT_MUTED};font-weight:400;"> Mbps</span>
                    </div>
                </div>
            </div>

        </div>

        {info_bawah}

    </div>
    """

    tinggi = 380 if (not placeholder and (isp or server_sponsor)) else 320

    dokumen_html = f"""
    <html>
    <head>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: "Segoe UI", "Inter", sans-serif;
            color: {style.TEXT};
        }}
    </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """

    components.html(dokumen_html, height=tinggi, scrolling=False)


# ==========================================================
# HALAMAN INPUT DATA
# ==========================================================

def show(model, predict):

    style.page_header(
        "Input Data Kualitas WiFi",
        "Masukkan data jaringan dan jawab kuesioner keluhan Anda"
    )

    # JS di browser mengukur kecepatan ASLI milik pengguna, lalu
    # mencoba mengisi otomatis 3 kolom input di bawah. Lihat catatan
    # riwayat perbaikan panjang di atas fungsi _bangun_html_speedtest()
    # kalau ingin tahu kenapa mekanismenya seperti ini.
    if st.session_state.get("speedtest_running"):
        components.html(_bangun_html_speedtest(), height=280)
        st.button("Reload", on_click=lambda: st.session_state.update(speedtest_running=False))
    else:
        if st.button("Jalankan Speed Test", use_container_width=True):
            st.session_state["speedtest_running"] = True
            st.rerun()

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        download = st.number_input(
            "Download Speed (Mbps)",
            min_value=0.0, max_value=2000.0,
            value=st.session_state.get("speedtest_download", 8.0),
            step=0.1, key="speedtest_download"
        )
        upload = st.number_input(
            "Upload Speed (Mbps)",
            min_value=0.0, max_value=2000.0,
            value=st.session_state.get("speedtest_upload", 4.0),
            step=0.1, key="speedtest_upload"
        )

    with col2:
        latency = st.number_input(
            "Latency / Ping (ms)",
            min_value=0.0, max_value=1000.0,
            value=st.session_state.get("speedtest_latency", 20.0),
            step=1.0, key="speedtest_latency"
        )
        packet_loss = st.number_input(
            "Packet Loss (%)",
            min_value=0.0, max_value=100.0,
            value=0.0, step=0.1
        )

    st.markdown(
        "🔗 **Belum mengetahui nilai Packet Loss?** "
        "Lakukan pengujian di "
        "[Open Packet Loss Test](https://openpacketloss.com/)."
    )

    st.markdown("#### Penilaian Keluhan")

    st.info("""
**Petunjuk Pengisian**

Pilih jawaban sesuai pengalaman Anda.

1 = Sangat sering bermasalah

2 = Sering

3 = Kadang-kadang

4 = Jarang

5 = Tidak pernah bermasalah
""")

    opsi = {
        "1 - Sangat sering bermasalah": 1,
        "2 - Sering": 2,
        "3 - Kadang-kadang": 3,
        "4 - Jarang": 4,
        "5 - Tidak pernah bermasalah": 5
    }

    q1 = opsi[
        st.radio(
            "1. Seberapa sering Anda mengalami koneksi internet yang lambat?",
            list(opsi.keys())
        )
    ]

    q2 = opsi[
        st.radio(
            "2. Seberapa sering koneksi internet Anda terputus secara tiba-tiba?",
            list(opsi.keys())
        )
    ]

    q3 = opsi[
        st.radio(
            "3. Seberapa sering Anda mengalami keterlambatan (lag) saat mengakses internet?",
            list(opsi.keys())
        )
    ]

    q4 = opsi[
        st.radio(
            "4. Seberapa sering sinyal WiFi di lokasi Anda tidak stabil?",
            list(opsi.keys())
        )
    ]

    q5 = opsi[
        st.radio(
            "5. Seberapa sering Anda perlu menghubungi teknisi karena gangguan?",
            list(opsi.keys())
        )
    ]

    skor_keluhan = round(
        (q1 + q2 + q3 + q4 + q5) / 5,
        2
    )

    st.success(
        f"Skor Keluhan : {skor_keluhan}"
    )

    st.markdown("#### Penilaian Keseluruhan")

    st.info(
        "**Petunjuk:** Pilih satu kategori yang paling menggambarkan penilaian "
        "Anda secara keseluruhan terhadap layanan WiFi Media Elektronik Kerinci."
    )

    label_kelas = st.radio(
        "Penilaian Anda",
        [
            "Sangat Baik",
            "Baik",
            "Sedang",
            "Buruk"
        ],
        horizontal=True
    )

    if st.button(
        "Jalankan Klasifikasi",
        use_container_width=True
    ):

        if download is None or upload is None or latency is None:
            st.warning("Silakan jalankan Speed Test terlebih dahulu sebelum melakukan klasifikasi.")
            st.stop()

        kelas, prob = predict(
            model,
            [
                download,
                upload,
                latency,
                packet_loss,
                skor_keluhan
            ]
        )

        # Simpan ke session
        st.session_state["hasil_prediksi"] = {
            "download": download,
            "upload": upload,
            "latency": latency,
            "packet_loss": packet_loss,
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "q4": q4,
            "q5": q5,
            "skor_keluhan": skor_keluhan,
            "kelas": kelas,
            "prob": prob,
            "label_kelas": label_kelas
        }

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
                st.session_state["user_id"],
                download,
                upload,
                latency,
                packet_loss,
                skor_keluhan,
                kelas,
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                label_kelas
            )
        )

        conn.commit()
        conn.close()

        st.success(                     
        "Silakan periksa hasilnya di halaman hasil saya"
         )

        st.session_state["menu"] = "Hasil"