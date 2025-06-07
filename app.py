import streamlit as st
import json
import pandas as pd
import time
import os
import csv

st.set_page_config(page_title="Kuis Python Dasar")

# ====== Gaya CSS Global ======
st.markdown("""
    <style>
        body {
            color-scheme: light;
        }
            
        /* Background Global */
        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif !important;
            background: linear-gradient(135deg, #667eea, #e1dfeb);
            color: #333;
        }

        /* Container Utama */
        .block-container {
            padding: 2rem 3rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 12px 30px rgb(103 80 164 / 0.3);
            animation: fadeInPage 0.7s ease forwards;
            transition: filter 0.3s ease;
        }

        /* Soal Card */
        .soal-card {
            background-color: #dbd8ed;
            border-radius: 25px;
            padding: 12px;
            margin-bottom: 20px;
            box-shadow: 0 8px 16px rgb(0 0 0 / 0.1);
            transition: box-shadow 0.3s ease, transform 0.3s ease;
            color: black;
            animation: slideIn 0.7s ease forwards;
        }
        .soal-card:hover {
            box-shadow: 0 12px 24px rgb(225 223 235 / 0.5);
            transform: translateY(-4px);
        }

        /* Tombol */
        div.stButton > button {
            background: #e1dfeb;
            color: black;
            font-weight: 600;
            border-radius: 10px;
            padding: 0.7rem 1.5rem;
            transition: background 0.3s ease, transform 0.2s ease;
            box-shadow: 0 4px 15px rgb(225 223 235 / 0.6);
        }
        div.stButton > button:hover {
            background: #d6d0f0;
            color: black;
            transform: scale(1.05);
            box-shadow: 0 8px 25px rgb(214 208 240 / 0.8);
        }

        /* Radio Option */
        .stRadio > div {
            transition: background 0.3s ease, transform 0.2s ease;
            border-radius: 8px;
            padding: 8px;
            color: black;
        }
        .stRadio > div:hover {
            background: #e7e5f7;
            transform: scale(1.02);
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: #e1dfeb;
            color: black;
        }
        [data-testid="stSidebar"] .css-1d391kg {
            font-weight: 700;
            font-size: 1.3rem;
            margin-bottom: 1rem;
        }
        [data-testid="stSidebar"] label {
            color: black;
        }

        /* Leaderboard Table Custom */
        table {
            border-collapse: collapse;
            width: 100%;
            font-weight: 500;
            font-size: 10rem;
            color: black;
        }
        th, td {
            padding: 0.9rem 1.2rem;
            text-align: left;
        }
        th {
            background: #e1dfeb;
            color: black;
            border-bottom: 2px solid #d6d0f0;
        }
        tr:nth-child(even) {
            background-color: #f3f3f3;
            color: black;
        }
        tr:hover {
            background-color: #d6d0f0;
            cursor: pointer;
            transition: background-color 0.3s ease;
            color: black;
        }

        /* Progress Bar */
        .stProgress > div > div {
            background: linear-gradient(90deg, #667eea, #e1dfeb);
            border-radius: 10px;
        }

        /* Animations */
        @keyframes fadeInPage {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        @keyframes slideIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
    </style>
""", unsafe_allow_html=True)

# ====== Load Soal dengan Cache ======
@st.cache_data
def load_soal():
    with open("soal.json") as f:
        return json.load(f)

soal_list = load_soal()

# ====== Inisialisasi State ======
def reset_kuis():
    for key in ['mulai_quiz', 'start_time', 'jawaban', 'submit', 'sudah_simpan']:
        st.session_state[key] = False if isinstance(st.session_state.get(key), bool) else None
    st.session_state.page = "Home"

if 'nama' not in st.session_state:
    st.session_state.nama = ""
if 'mulai_quiz' not in st.session_state:
    st.session_state.mulai_quiz = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'jawaban' not in st.session_state:
    st.session_state.jawaban = {}
if 'submit' not in st.session_state:
    st.session_state.submit = False
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'sudah_simpan' not in st.session_state:
    st.session_state.sudah_simpan = False

TOTAL_WAKTU = 60 # detik

# ====== Fungsi Mulai Kuis ======
def mulai_kuis():
    nama_input = st.session_state.input_nama.strip()
    if nama_input == "":
        st.warning("⚠ Nama tidak boleh kosong!")
        return False
    else:
        st.session_state.nama = nama_input
        st.session_state.mulai_quiz = True
        st.session_state.start_time = time.time()
        st.session_state.submit = False
        st.session_state.page = "Kuis"
        st.session_state.jawaban = {}
        st.session_state.sudah_simpan = False
        return True

# ====== Fungsi Simpan Leaderboard ======
def simpan_ke_leaderboard(nama, benar, total_soal, persen):
    skor_data = {
        "nama": nama,
        "skor": benar,
        "total_soal": total_soal,
        "persentase": f"{persen:.2f}%"
    }

    file_path = "leaderboard.csv"
    file_exists = os.path.isfile(file_path)

    with open(file_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["nama", "skor", "total_soal", "persentase"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(skor_data)

# ====== Sidebar ======
with st.sidebar:
    st.title("📚 Menu Navigasi")
    if st.session_state.nama:
        st.markdown(f"### 👤 Nama: {st.session_state.nama}")
    else:
        st.markdown("### 👤 Nama: -")

    if st.session_state.mulai_quiz and st.session_state.start_time:
        waktu_terlewati = int(time.time() - st.session_state.start_time)
        sisa_waktu = max(0, TOTAL_WAKTU - waktu_terlewati)
        menit = sisa_waktu // 60
        detik = sisa_waktu % 60
        st.markdown(f"⏳ **Waktu tersisa:** {menit:02d}:{detik:02d}")
    else:
        st.markdown("⏳ Waktu tersisa: -")

    pages = ["Home", "Kuis", "Pembahasan", "Leaderboard"]
    default_index = pages.index(st.session_state.page) if st.session_state.page in pages else 0
    selected_page = st.radio("Pilih Halaman:", pages, index=default_index)
    if selected_page != st.session_state.page:
        st.session_state.page = selected_page

# ====== Fungsi Tiap Halaman ======
def tampilkan_home():
    st.title("Kuis Python Dasar ⚡")
    st.markdown("###### Projek Program Komputer")
    st.markdown("Oleh Kevin & Farrel")
    st.image("https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3OWcxMXAzdWpkdXJzMXhxbnpocGM4MGF2M3RqMzk3enNrcTVnODJoaCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/y93slPbDMdeXJQONHa/giphy.gif", width=300)
    st.text_input("Masukkan nama kamu:", key="input_nama", value=st.session_state.nama)
    if st.button("🎯 Mulai Kuis"):
        if mulai_kuis():
            st.session_state.page = "Kuis"

def tampilkan_kuis():
    if not st.session_state.mulai_quiz:
        st.warning("⚠ Silakan mulai kuis dari halaman Home terlebih dahulu.")
    else:
        waktu_terlewati = int(time.time() - st.session_state.start_time)
        sisa_waktu = TOTAL_WAKTU - waktu_terlewati

        if sisa_waktu <= 0:
            st.warning("⏰ Waktu habis! Jawaban disubmit otomatis.")
            st.session_state.submit = True
            st.session_state.mulai_quiz = False
            st.session_state.page = "Pembahasan"

            # Tombol menuju leaderboard setelah waktu habis
            if st.button("Yah, waktu habis"):
                st.session_state.page = "Leaderboard"
            return  # keluar agar tidak render bagian soal lagi

        else:
            st.title("📝 Selamat Mengerjakan!")
            menit = sisa_waktu // 60
            detik = sisa_waktu % 60
            st.markdown(f"### ⏳ Waktu tersisa: {menit:02d}:{detik:02d}")

            for i, soal in enumerate(soal_list):
                with st.container():
                    st.markdown(f"""
                    <div class=\"soal-card\">
                        <h4>📘 Soal {i+1}</h4>
                        <p>{soal["pertanyaan"]}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    pilihan = soal["opsi"]
                    jawaban_sebelumnya = st.session_state.jawaban.get(i, None)

                    opsi_radio = ["(Belum memilih)"] + pilihan
                    idx_default = 0
                    if jawaban_sebelumnya in pilihan:
                        idx_default = pilihan.index(jawaban_sebelumnya) + 1

                    jawaban = st.radio(
                        f"Jawaban kamu untuk Soal {i+1}:",
                        opsi_radio,
                        index=idx_default,
                        key=f"soal_{i}"
                    )
                    if jawaban == "(Belum memilih)":
                        st.session_state.jawaban.pop(i, None)
                    else:
                        st.session_state.jawaban[i] = jawaban

            if st.button("✅ Submit Jawaban"):
                if len(st.session_state.jawaban) < len(soal_list):
                    belum = [str(i+1) for i in range(len(soal_list)) if i not in st.session_state.jawaban]
                    st.warning(f"Harap menjawab semua soal terlebih dahulu! Soal belum dijawab: {', '.join(belum)}")
                else:
                    st.session_state.submit = True
                    st.session_state.mulai_quiz = False
                    st.session_state.page = "Pembahasan" 

def tampilkan_pembahasan():
    if not st.session_state.submit:
        st.info("⚠ Selesaikan kuis terlebih dahulu.")

    else:
        st.title("📖 Pembahasan Kuis")
        benar = 0
        for i, soal in enumerate(soal_list):
            st.subheader(f"Soal {i+1}")
            st.write("**Pertanyaan:**", soal["pertanyaan"])
            jawaban_user = st.session_state.jawaban.get(i, "Belum menjawab")
            st.write("**Jawaban Kamu:**", jawaban_user)
            st.write("**Jawaban Benar:**", soal["jawaban_benar"])
            if jawaban_user == soal["jawaban_benar"]:
                benar += 1
                st.success("Jawaban kamu benar!")
            else:
                st.error("Jawaban kamu salah.")
            st.write("**Pembahasan:**", soal["pembahasan"])
            st.markdown("---")

        total_soal = len(soal_list)
        persen = benar / total_soal * 100
        st.markdown(f"""
        ### 🎯 Hasil Kuis:
        - ✅ Jawaban Benar: **{benar}**
        - ❌ Jawaban Salah: **{total_soal - benar}**
        - 📊 Skor: **{persen:.2f}%**
        """)

        if not st.session_state.sudah_simpan:
            simpan_ke_leaderboard(st.session_state.nama, benar, total_soal, persen)
            st.session_state.sudah_simpan = True

        col1, = st.columns(1)
        with col1:
            if st.button("Lihat Leaderboard"):
                st.session_state.page = "Leaderboard"

def tampilkan_leaderboard():
    if not st.session_state.submit:
        st.warning("⚠ Leaderboard hanya bisa diakses setelah menyelesaikan kuis dan melihat pembahasan.")
        if st.button("Kembali ke Home"):
            st.session_state.page = "Home"
        return  # keluar dari fungsi jika belum menyelesaikan kuis

    st.title("🏆 Leaderboard")
    file_path = "leaderboard.csv"

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if "skor" in df.columns:
            df = df.sort_values(by="skor", ascending=False).reset_index(drop=True)
            df.index = df.index + 1
            st.markdown("### 📈 Ranking Berdasarkan Skor:")
            st.table(df[["nama", "skor", "persentase"]].rename(columns={
                "nama": "👤 Nama",
                "skor": "🏆 Skor",
                "persentase": "📊 Persentase"
            }))
            st.image("https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3eDZmYWs0djFxbjZscWY4bTNxNmJkOG10aTFnand6aXp4emZla3I3cCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/4Z0hDZQdWQYtG/giphy.gif", width=300)
        else:
            st.error("File leaderboard.csv tidak memiliki kolom 'skor'.")
    else:
        st.info("Belum ada data leaderboard.")

    if st.button("Kembali ke Home"):
        st.session_state.page = "Home"

# ====== Routing Halaman ======
if st.session_state.page == "Home":
    tampilkan_home()
elif st.session_state.page == "Kuis":
    tampilkan_kuis()
elif st.session_state.page == "Pembahasan":
    tampilkan_pembahasan()
elif st.session_state.page == "Leaderboard":
    tampilkan_leaderboard()
