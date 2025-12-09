import streamlit as st
import re
import pandas as pd

# ==============================================================================
# 1. DATABASE PEMETAAN KOMPETENSI (Structured Technical Skills)
#    Struktur: 'input_keyword': {'title': 'Standardized Title', 'category': 'Category Name'}
# ==============================================================================

STRUCTURED_SKILL_MAPPINGS = {
    # -- KATEGORI: ANALISIS & PEMODELAN --
    'analisa': {'title': 'Analisis Data Bisnis dan Pelaporan', 'category': 'Analisis'},
    'statistik': {'title': 'Penggunaan Metode Statistik', 'category': 'Analisis'},
    'pemodelan': {'title': 'Pemodelan Keuangan dan Bisnis', 'category': 'Pemodelan'},
    'analisa pasar': {'title': 'Analisis Pasar dan Trend Industri', 'category': 'Analisis'},
    'ecommerce': {'title': 'Strategi dan Analisis E-commerce', 'category': 'Analisis'}, # NEW MAPPING

    # -- KATEGORI: PENGEMBANGAN & DESAIN --
    'product development': {'title': 'Pengembangan Produk dan Inovasi', 'category': 'Pengembangan'},
    'pengembangan produk': {'title': 'Pengembangan Produk dan Siklus Hidup Produk', 'category': 'Pengembangan'},
    'desain grafis': {'title': 'Desain Komunikasi Visual dan Grafis', 'category': 'Desain'},
    'autocad': {'title': 'Penggunaan Perangkat Lunak Desain Berbantuan Komputer (AutoCAD)', 'category': 'Desain'},
    'copywriting': {'title': 'Copywriting dan Teknik Penulisan Pemasaran', 'category': 'Penulisan'}, 
    'content writing': {'title': 'Strategi Perencanaan dan Penulisan Konten', 'category': 'Penulisan'}, 
    
    # -- KATEGORI: MANAJEMEN & PENGANGGARAN & PENGADAAN --
    'project management': {'title': 'Manajemen Proyek dan Metodologi (PMP/Scrum)', 'category': 'Manajemen'},
    'proyek': {'title': 'Manajemen Proyek dan Metodologi (PMP/Scrum)', 'category': 'Manajemen'},
    'budget': {'title': 'Manajemen Penganggaran dan Kontrol Biaya', 'category': 'Penganggaran'},
    'cost control': {'title': 'Analisis dan Kontrol Biaya Operasional', 'category': 'Penganggaran'},
    'tender': {'title': 'Strategi dan Proses Pengadaan (Tendering & Procurement)', 'category': 'Pengadaan'},
    'media sosial': {'title': 'Manajemen Platform Media Sosial', 'category': 'Manajemen'}, # Dihapus "Korporat"
    'budgeting' :{'title': 'Perencanaan dan Pengelolaan Anggaran (Budgeting)', 'category': 'Penganggaran'}, # NEW MAPPING

    # -- KATEGORI: PENGOPERASIAN & PENGELOLAAN --
    'erp': {'title': 'Pengoperasian Sistem ERP (Enterprise Resource Planning)', 'category': 'Pengoperasian'},
    'sap': {'title': 'Pengoperasian Sistem SAP', 'category': 'Pengoperasian'},
    'ms office': {'title': 'Pengoperasian Aplikasi Kantor (Ms Office)', 'category': 'Pengoperasian'}, # Dihapus "/Google Workspace"
    'cloud computing': {'title': 'Pengelolaan Layanan Cloud Computing (AWS/Azure/GCP)', 'category': 'Pengelolaan'},
    'network': {'title': 'Manajemen Jaringan (Networking) dan Keamanan Data', 'category': 'Pengelolaan'},
    
    # -- KATEGORI: KEPATUHAN & AUDIT & RISIKO --
    'risiko': {'title': 'Manajemen Risiko Bisnis dan Operasional', 'category': 'Kepatuhan'},
    'hukum ketenagakerjaan': {'title': 'Kepatuhan Hukum Ketenagakerjaan', 'category': 'Kepatuhan'},
    'audit internal': {'title': 'Pelaksanaan Audit Internal', 'category': 'Kepatuhan'},
    'tax planning': {'title': 'Perencanaan dan Optimalisasi Pajak', 'category': 'Kepatuhan'}, # Dihapus "Korporat"
    
    # -- KATEGORI: OPERASIONAL & KUALITAS & PEMELIHARAAN --
    'k3': {'title': 'Implementasi Prosedur K3 (Keselamatan dan Kesehatan Kerja)', 'category': 'Pengoperasian'},
    'quality control': {'title': 'Pengawasan Mutu dan Kontrol Kualitas (QC)', 'category': 'Pengujian'},
    'produksi': {'title': 'Manajemen Efisiensi Operasional Produksi', 'category': 'Pengelolaan'},
    'maintenance': {'title': 'Pemeliharaan Preventif dan Korektif', 'category': 'Pemeliharaan'},
    'riset digital': {'title': 'Riset dan Analisis Trend Digital', 'category': 'Analisis'}, 

    # -- KATEGORI: PENYUSUNAN & PENULISAN & PEMASARAN --
    'kontrak': {'title': 'Penyusunan dan Review Kontrak Bisnis', 'category': 'Penyusunan'},
    'laporan keuangan': {'title': 'Penyusunan Laporan Keuangan', 'category': 'Penyusunan'},
    'digital marketing': {'title': 'Strategi dan Pelaksanaan Pemasaran Digital', 'category': 'Pemasaran'},
    'power point': {'title': 'Penulisan dan Pembuatan Presentasi Visual', 'category': 'Penulisan'},
    'komunikasi': {'title': 'Penulisan dan Komunikasi ', 'category': 'Penulisan'}, # Dihapus "Korporat"
    'kpi' :{'title': 'Penyusunan dan Pemantauan Key Performance Indicators (KPI)', 'category': 'Penyusunan'}, # NEW MAPPING
    'job description' :{'title': 'Penyusunan dan Analisis Job Description', 'category': 'Penyusunan'}, # NEW MAPPING

    # -- KATEGORI LAIN --
    'karyawan': {'title': 'Strategi dan Proses Rekrutmen & Seleksi Karyawan', 'category': 'Pengelolaan'},
    'excel': {'title': 'Penguasaan Lanjutan Microsoft Excel', 'category': 'Pengoperasian'},
    'strategi': {'title': 'Analisis dan Perumusan Strategi', 'category': 'Analisis'}, # Dihapus "Korporat"
    
    # Tambahkan lebih banyak mapping di sini seiring berjalannya proyek!
}

# ==============================================================================
# 2. FUNGSI PEMBERSINAN/STANDARDISASI
# ==============================================================================


def clean_skill_titles(raw_skills):
    # ... (pemrosesan awal)
    input_list = [s.strip() for s in raw_skills.split('\n') if s.strip()]
    cleaned_data = []
    sorted_mappings = sorted(STRUCTURED_SKILL_MAPPINGS.items(), key=lambda item: len(item[0]), reverse=True)
    
    for skill in input_list:
        # [--- PERBAIKAN 1: PEMBERSIHAN KARAKTER KHUSUS DAN SPASI (mis. bullet point •) ---]
        cleaned_skill = re.sub(r'[\u2022\u2013\-\•]+', ' ', skill).strip()
        skill_lower = cleaned_skill.lower()
        match_info = None
        
        # 1. Mencari kecocokan terbaik di kamus
        for keyword, data in sorted_mappings:
            if keyword in skill_lower:
                match_info = data
                break 
        
        if match_info:
            standard_title = match_info['title']
            category = match_info['category']
            
            # [--- PERBAIKAN 2: LOGIKA PENAMBAHAN DETAIL SPESIFIK DARI KURUNG () ---]
            parentheses_match = re.search(r'\((.*?)\)', cleaned_skill)
            final_title = standard_title

            if parentheses_match:
                raw_details = parentheses_match.group(1).strip()
                
                # Pisahkan detail menjadi sub-item (contoh: 'Desain Grafis & Video Editing')
                detail_items = [item.strip() for item in re.split(r'[,&/]', raw_details)]
                
                unique_details = []
                standard_title_lower = standard_title.lower()
                
                for detail in detail_items:
                    detail_lower = detail.lower()
                    # Hanya simpan detail yang TIDAK ditemukan sebagai substring utama di judul standar
                    if detail_lower and detail_lower not in standard_title_lower:
                        unique_details.append(detail)

                if unique_details:
                    # Gabungkan detail unik yang tersisa
                    extra_part = " & ".join(unique_details)
                    final_title = f"{standard_title} ({extra_part})"

            # 3. Tambahkan ke data
            cleaned_data.append({
                'Kompetensi': final_title,
                'Kategori': category
            })
            
        else:
            # 4. Mekanisme Cadangan (Fallback)
            # Menghapus kurung dan isinya sebelum kapitalisasi untuk fallback
            skill_no_parentheses = re.sub(r'\((.*?)\)', '', cleaned_skill).strip()
            standardized = ' '.join(word.capitalize() for word in skill_no_parentheses.split())
            
            # [--- PERBAIKAN 3: DAFTAR KATA KUNCI PROFESIONAL UNTUK MENCEGAH DOUBLE-PREFIX 'Penguasaan' ---]
            # KOMA TELAH DIPERBAIKI di antara 'analisa' dan 'desain'
            if not standardized.lower().startswith((
                'penguasaan', 'manajemen', 'analisis', 'strategi', 'implementasi', 
                'perumusan', 'pengembangan', 'riset', 'copywriting', 'perencanaan',
                'pengelolaan', 'pengoperasian', 'pemeliharaan', 'penyusunan', 'analisa', # <-- KOMA DITAMBAHKAN DI SINI
                'desain', 'pemasaran', 'pengujian', 'kepatuhan', 'pelaksanaan', 'pemahaman', 'perawatan', 'penggunaan', 'management', 'penanganan', 'pengadaan' 
            )):
                final_title = f"Penguasaan {standardized}"
            else:
                 final_title = standardized
            
            # Tetapkan kategori cadangan jika tidak ditemukan
            cleaned_data.append({
                'Kompetensi': final_title,
                'Kategori': 'Pengelolaan' # Kategori generik untuk Technical Skills yang belum dipetakan
            })
    # ... (penghapusan duplikat)
    seen = set()
    unique_data = []
    for item in cleaned_data:
        if item['Kompetensi'] not in seen:
            seen.add(item['Kompetensi'])
            unique_data.append(item)
            
    return unique_data

# ==============================================================================
# 3. APLIKASI STREAMLIT
# ==============================================================================

def main():
    st.set_page_config(
        page_title="Standardisasi Kompetensi VVVV Group",
        layout="wide", # Menggunakan layout wide agar tabel terlihat lebih luas
    )
    
    st.title("🛠️ Standardisasi & Kategorisasi Matriks Kompetensi VVVV Group")
    st.markdown(
        """
        Alat ini mengkonversi daftar keterampilan mentah ke **Judul Kompetensi Teknis Profesional** yang konsisten dan secara otomatis mengelompokkannya ke dalam Kategori Teknik Baku (misalnya: Analisis, Pengembangan, Penganggaran).
        """
    )
    
    # --- Input Area ---
    st.header("1. Masukkan Daftar Keterampilan Mentah")
    
    # Contoh input diperbarui untuk mencerminkan penambahan skill mappings dan kategori
    sample_input = (
        "Kreasi Konten Visual (Desain Grafis & Video Editing)\n" # Uji coba logika mempertahankan detail kurung
        "Penguasaan • Copywriting & Content Writing\n" 
        "Manajemen Platform Media Sosial\n" 
        "Riset Digital\n" 
        "Penyusunan KPI\n" # Uji coba mapping KPI
        "Perencanaan Budgeting (Tahunan)\n" # Uji coba mapping budgeting
        "Analisis Data Operasional (dengan Python)" # Uji coba detail unik di kurung
    )
    
    raw_skills = st.text_area(
        "Masukkan satu keterampilan per baris:",
        value=sample_input,
        height=300,
        key="raw_input"
    )

    # --- Processing Button ---
    if st.button("✨ Standardisasi & Kategorisasi Judul", type="primary"):
        if raw_skills:
            # --- Output Area ---
            st.header("2. Hasil Kategorisasi dan Standardisasi")
            
            # Memanggil fungsi pembersihan
            final_data = clean_skill_titles(raw_skills)
            
            if final_data:
                st.success(f"Ditemukan {len(final_data)} Judul Kompetensi Unik yang Distandardisasi.")
                
                # Menampilkan hasil dalam bentuk tabel Pandas Dataframe
                df = pd.DataFrame(final_data)
                
                # Menggunakan st.dataframe untuk tampilan yang lebih baik dan interaktif
                st.dataframe(df, use_container_width=True)
                
                st.markdown("---")
                st.info("💡 **Tips:** Detail spesifik dalam kurung (`()`) akan dipertahankan jika tidak redundan dengan judul standar.")
            
        else:
            st.warning("Mohon masukkan daftar keterampilan di area input terlebih dahulu.")

if __name__ == "__main__":
    main()