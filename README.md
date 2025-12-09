# Standardisasi & Kategorisasi Matriks Kompetensi

Aplikasi Streamlit untuk mengkonversi daftar keterampilan mentah ke **Judul Kompetensi Teknis Profesional** secara instan menggunakan logika database lookup yang deterministic (100% tanpa AI/LLM).

## Fitur
- ✅ Input daftar keterampilan mentah
- ✅ Kategorisasi otomatis berdasarkan database kompetensi terstruktur
- ✅ Standardisasi judul kompetensi
- ✅ Export hasil ke CSV
- ✅ Sistem 100% deterministic (no AI/API dependency)

## Setup & Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Streamlit
```bash
streamlit run techn.py
```

### 3. Akses Aplikasi
- **Local**: http://localhost:8501
- **Network**: http://[IP-Address]:8501

## Requirements
- Python 3.8+
- streamlit>=1.28.0
- pandas>=2.0.0

## Struktur Database
Aplikasi menggunakan mapping kompetensi terstruktur dengan kategori:
- Analisis
- Pemodelan
- Pengembangan
- Desain
- Manajemen
- Penganggaran
- Pengadaan
- Kepatuhan
- Dan lainnya...

## Cara Penggunaan
1. Copy-paste daftar keterampilan ke text area
2. Klik tombol **Proses**
3. Lihat hasil kategorisasi & standardisasi
4. Download CSV jika diperlukan

Link -> https://generate-techcomps.streamlit.app/
