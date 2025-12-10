import streamlit as st
import re
import pandas as pd
import json
from docx import Document
import io
import itertools
# File ini sepenuhnya menggunakan logika deterministik (tanpa AI/LLM API).

# ==============================================================================
# 1. DATABASE PEMETAAN KOMPETENSI DASAR
# ==============================================================================
# Database dasar yang akan di-augmentasi (diperkaya) oleh data DOCX pengguna.

# Perhatian: Gunakan huruf kecil untuk semua keyword di database!
BASE_SKILL_MAPPINGS = {
    # -- KATEGORI: ANALISIS & PEMODELAN --
    'analisa': {'title': 'Analisis Data Bisnis dan Pelaporan', 'category': 'Analisis'},
    'statistik': {'title': 'Penggunaan Metode Statistik', 'category': 'Analisis'},
    'pemodelan': {'title': 'Pemodelan Keuangan dan Bisnis', 'category': 'Pemodelan'},
    'analisa pasar': {'title': 'Analisis Pasar dan Trend Industri', 'category': 'Analisis'},
    'ecommerce': {'title': 'Strategi dan Analisis E-commerce', 'category': 'Analisis'}, 
    'business development': {'title': 'Strategi dan Implementasi Business Development', 'category': 'Analisis'}, 
    
    # -- KATEGORI: PENGEMBANGAN & DESAIN --
    'product development': {'title': 'Pengembangan Produk dan Inovasi', 'category': 'Pengembangan'},
    'pengembangan produk': {'title': 'Pengembangan Produk dan Siklus Hidup Produk', 'category': 'Pengembangan'},
    'desain grafis': {'title': 'Desain Komunikasi Visual dan Grafis', 'category': 'Desain'},
    'autocad': {'title': 'Penggunaan Perangkat Lunak Desain Berbantuan Komputer (AutoCAD)', 'category': 'Desain'},
    'copywriting': {'title': 'Penulisan Pemasaran Langsung (Copywriting)', 'category': 'Pemasaran'},
    
    # -- KATEGORI: MANAJEMEN & PENGANGGARAN --
    'project management': {'title': 'Manajemen Proyek dan Metodologi (PMP/Scrum)', 'category': 'Manajemen'},
    'proyek': {'title': 'Manajemen Proyek dan Metodologi (PMP/Scrum)', 'category': 'Manajemen'},
    'excel': {'title': 'Penguasaan Lanjutan Microsoft Excel', 'category': 'Pengoperasian'},
    'strategi': {'title': 'Analisis dan Perumusan Strategi', 'category': 'Analisis'}, 
    'digital marketing': {'title': 'Strategi dan Pelaksanaan Pemasaran Digital', 'category': 'Pemasaran'},
    'kpi' :{'title': 'Penyusunan dan Pemantauan Key Performance Indicators (KPI)', 'category': 'Penyusunan'}, 
}
# ==============================================================================
# 2. FUNGSI UTILITAS
# ==============================================================================

def capitalize_smartly(text):
    """Fungsi kapitalisasi cerdas."""
    words_standardized = []
    for word in text.split():
        if word.isupper() and len(word) > 1:
            words_standardized.append(word)
        else:
            words_standardized.append(word.capitalize())
    return ' '.join(words_standardized)

def extract_text_from_docx(uploaded_file):
    """Membaca teks dari file DOCX yang diunggah."""
    try:
        doc = Document(io.BytesIO(uploaded_file.getvalue()))
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        st.error(f"Gagal membaca file DOCX. Error: {e}")
        return ""

def generate_keywords(text):
    """Menghasilkan keyword untuk database dari sebuah judul."""
    text_lower = text.lower()
    stopwords = set(["dan", "atau", "dengan", "di", "dari", "untuk", "serta", "dalam", "yang", "pada", "melalui"])
    text_cleaned = re.sub(r'\s*\([^)]*\)\s*', '', text_lower)
    words = re.findall(r'\b\w+\b', text_cleaned)
    
    keywords = sorted([w for w in words if w not in stopwords and len(w) > 2], key=len, reverse=True)[:3]
    acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
    
    return list(set([word.lower() for word in keywords] + [a.lower() for a in acronyms]))


def augment_mappings_from_docx(docx_content):
    """
    Memproses teks DOCX (Buku Career Path) untuk menghasilkan mappings baru.
    ASUMSI: Setiap 3 baris di DOCX mewakili 1 set data:
        Baris 1: Raw Skill A (yang akan menjadi keyword)
        Baris 2: Standard Title B
        Baris 3: Category C (Opsional)
    """
    new_mappings = {}
    lines = [line.strip() for line in docx_content.split('\n') if line.strip()]
    
    if len(lines) < 3:
        st.warning("Data DOCX terlalu singkat. Minimal butuh 3 baris (Raw Skill, Standard Title, Category).")
        return {}

    # Mengelompokkan baris menjadi blok 3 (Raw Skill, Title, Category)
    for i in range(0, len(lines), 3):
        if i + 2 < len(lines):
            raw_skill = lines[i]
            standard_title = lines[i+1]
            category = lines[i+2]
            
            keywords = generate_keywords(raw_skill)

            for keyword in keywords:
                # Pastikan keyword bukan string kosong dan diubah ke huruf kecil
                if keyword and keyword not in new_mappings and keyword not in BASE_SKILL_MAPPINGS:
                    new_mappings[keyword] = {
                        'title': standard_title.strip(),
                        'category': capitalize_smartly(category.strip()),
                        'source': 'Augmented/User Data'
                    }
        else:
            break
            
    return new_mappings

def convert_dict_to_df(data_dict):
    """Konversi dictionary mappings ke DataFrame untuk diedit."""
    data_list = []
    for keyword, data in data_dict.items():
        data_list.append({
            'Keyword': keyword,
            'Judul Standar': data['title'],
            'Kategori': data['category'],
            'Sumber': data.get('source', 'Base/Default')
        })
    return pd.DataFrame(data_list)

def convert_df_to_dict(data_df):
    """Konversi DataFrame yang diedit kembali ke dictionary mappings."""
    new_dict = {}
    # Iterasi baris DataFrame
    for index, row in data_df.iterrows():
        keyword = str(row['Keyword']).lower().strip() # Selalu pastikan keyword adalah huruf kecil
        if keyword:
            new_dict[keyword] = {
                'title': row['Judul Standar'],
                'category': row['Kategori'],
                'source': row['Sumber'] # Pertahankan sumber
            }
    return new_dict

def process_single_skill_deterministic(skill, sorted_mappings):
    """
    Memproses satu keterampilan menggunakan logika database dan fallback sederhana.
    """
    cleaned_skill = re.sub(r'[\u2022\u2013\-\•]+', ' ', skill).strip()
    skill_lower = cleaned_skill.lower()
    match_info = None
    category = 'Umum' 
    final_title = cleaned_skill 

    # 1. Mencari kecocokan terbaik di kamus (Deterministic Matching)
    for keyword, data in sorted_mappings:
        if keyword in skill_lower:
            match_info = data
            break 
    
    if match_info:
        standard_title = match_info['title']
        category = match_info['category']
        final_title = standard_title
        
        # LOGIKA DETAIL KURUNG: Capture and preserve the entire original parenthesis block.
        parentheses_match = re.search(r'(\s*\([^)]*\))', cleaned_skill)

        if parentheses_match:
            original_parentheses_block = parentheses_match.group(1).strip()
            final_title = f"{standard_title} {original_parentheses_block}"
        
        source = "Database" if match_info.get('source') != 'Augmented/User Data' else match_info.get('source')
    
    else:
        # FALLBACK SEDERHANA
        skill_no_parentheses = re.sub(r'\((.*?)\)', '', cleaned_skill).strip()
        standardized = capitalize_smartly(skill_no_parentheses)
        
        # Tambahkan prefix 'Penguasaan' jika perlu
        if not standardized.lower().startswith(('penguasaan', 'manajemen', 'analisis', 'strategi', 'implementasi', 
            'perumusan', 'pengembangan', 'riset', 'copywriting', 'perencanaan',
            'pengelolaan', 'pengoperasian', 'pemeliharaan', 'penyusunan', 'analisa',
            'desain', 'pemasaran', 'pengujian', 'kepatuhan', 'pelaksanaan', 'pemahaman', 'perawatan', 'penggunaan', 'management', 'penanganan', 'pengadaan', 'it'
        )):
            final_title = f"Penguasaan {standardized}"
        else:
            final_title = standardized
        
        # Tambahkan kembali kurung yang mungkin ada di skill mentah
        raw_parentheses_match = re.search(r'(\s*\([^)]*\))', cleaned_skill)
        if raw_parentheses_match:
            final_title = f"{final_title} {raw_parentheses_match.group(1).strip()}"

        category = 'Umum' 
        source = "Fallback Sederhana"

    return {
        'Kompetensi': final_title,
        'Kategori': category,
        'Sumber Mentah': cleaned_skill, 
        'Sumber Standardisasi': source
    }

def clean_skill_titles(raw_skills, current_mappings):
    """Fungsi pembersihan utama menggunakan logika database deterministik yang telah diaugmentasi."""
    input_list = [s.strip() for s in raw_skills.split('\n') if s.strip()]
    cleaned_data = []
    
    sorted_mappings = sorted(current_mappings.items(), key=lambda item: len(item[0]), reverse=True)
    
    for skill in input_list:
        result = process_single_skill_deterministic(skill, sorted_mappings)
        cleaned_data.append(result)

    seen = set()
    unique_data = []
    for item in cleaned_data:
        if item['Kompetensi'] not in seen:
            seen.add(item['Kompetensi'])
            unique_data.append(item)
            
    return unique_data

# ==============================================================================
# 4. APLIKASI STREAMLIT
# ==============================================================================

def main():
    st.set_page_config(
        page_title="Standardisasi Kompetensi VVVV Group",
        layout="wide",
    )
    
    st.title("🛠️ Standardisasi Matriks Kompetensi VVVV Group (Deterministic Learning & Editing)")
    
    # --- Inisialisasi Session State ---
    if 'cleaned_data' not in st.session_state:
        st.session_state.cleaned_data = []
    if 'augmented_mappings' not in st.session_state:
        st.session_state.augmented_mappings = BASE_SKILL_MAPPINGS
    if 'data_editor_key' not in st.session_state:
        st.session_state.data_editor_key = 0
    if 'mapping_editor_key' not in st.session_state:
        st.session_state.mapping_editor_key = 0


    # --- Sidebar/Augmentation Control ---
    with st.sidebar:
        st.header("⚙️ Pembelajaran dari Data Anda")
        st.markdown("""
        Unggah file **.docx** yang berisi data kompetensi yang sudah **benar** dari proyek sebelumnya (3 baris per set data).
        """)
        
        docx_file = st.file_uploader("Upload Buku Career Path (.docx)", type=['docx'])
        
        if docx_file is not None:
            if st.button("Proses DOCX & Perkaya Database", type="secondary"):
                with st.spinner("Mengekstrak dan belajar dari data DOCX..."):
                    docx_content = extract_text_from_docx(docx_file)
                    new_mappings = augment_mappings_from_docx(docx_content)
                    
                    # Merge data baru, data augmentasi menimpa data dasar jika keyword sama
                    current_mappings = BASE_SKILL_MAPPINGS.copy()
                    current_mappings.update(new_mappings)
                    st.session_state.augmented_mappings = current_mappings
                    st.session_state.mapping_editor_key += 1
                    
                    st.success(f"Database diperkaya! Ditambahkan {len(new_mappings)} keyword baru.")
        
        st.markdown("---")
        st.metric(
            label="Total Keyword Database Aktif",
            value=f"{len(st.session_state.augmented_mappings):,} keywords"
        )
        st.caption("Mode: Deterministic (Database Lookup & In-Situ Editing)")

    # --- Database Editing Section (New Feature) ---
    st.header("1. Editor Database Keyword Aktif (Untuk Koreksi In-Situ)")
    st.info("""
    Anda dapat mengedit, menambah, atau menghapus baris di tabel ini.
    Perubahan akan langsung digunakan untuk memproses data mentah di langkah berikutnya.
    **Penting: Kolom 'Keyword' harus HANYA terdiri dari huruf kecil (lowercase).**
    """)
    
    # Konversi dictionary ke DataFrame untuk diedit
    current_df = convert_dict_to_df(st.session_state.augmented_mappings)
    
    edited_df = st.data_editor(
        current_df,
        key=f"mapping_editor_{st.session_state.mapping_editor_key}",
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Keyword": st.column_config.TextColumn("Keyword (Harus lowercase)", required=True),
            "Judul Standar": st.column_config.TextColumn("Judul Standar", required=True),
            "Kategori": st.column_config.TextColumn("Kategori", required=True),
            "Sumber": st.column_config.Column(disabled=True, help="Base/Default atau Augmented/User Data")
        }
    )
    
    # Tombol untuk Menerapkan Perubahan dari Editor Database
    if st.button("💾 Simpan Perubahan Database (Wajib Klik!)", help="Terapkan semua perubahan di tabel di atas ke database aktif."):
        new_mappings_dict = convert_df_to_dict(edited_df)
        st.session_state.augmented_mappings = new_mappings_dict
        st.success(f"Database berhasil diperbarui dengan {len(new_mappings_dict)} keyword.")
        # Memicu rerun untuk memastikan database terupdate
        st.rerun()

    st.markdown("---")

    # --- Input Area ---
    st.header("2. Masukkan Daftar Keterampilan Mentah (Untuk PT Berikutnya)")
    
    sample_input = (
        "Kreasi Konten Visual (Desain Grafis & Video Editing)\n" 
        "Penguasaan • Copywriting & Content Writing\n" 
        "Riset Digital\n" 
        "Penyusunan KPI\n" 
        "Analisis Data Operasional (dengan Python)\n" 
        "Penguasaan Strategi Business Development\n"
        "IT Security Auditing dan Penetration Testing (Black Box Testing)\n"
        "Pencatatan Akuntansi Forensik" 
    )
    
    raw_skills = st.text_area(
        "Masukkan satu keterampilan per baris (dari sisa 5 PT):",
        value=sample_input,
        height=300,
        key="raw_input"
    )

    # --- Processing Button ---
    if st.button("⚡ Standardisasi & Kategorisasi Judul (INSTAN)", type="primary"):
        if raw_skills:
            final_data = clean_skill_titles(raw_skills, st.session_state.augmented_mappings)
            
            st.session_state.cleaned_data = final_data
            st.session_state.data_editor_key += 1
            st.toast(f"Ditemukan {len(final_data)} Judul Kompetensi Unik yang Distandardisasi.", icon='📝')
        else:
            st.warning("Mohon masukkan daftar keterampilan di area input terlebih dahulu.")

    # --- Output Area ---
    if st.session_state.cleaned_data:
        st.header("3. Hasil Kategorisasi dan Standardisasi")
        
        df = pd.DataFrame(st.session_state.cleaned_data)
        
        display_df = df.drop(columns=['Sumber Mentah'])
        
        st.success(f"Menampilkan {len(display_df)} Judul Kompetensi.")

        edited_df = st.data_editor(
            display_df,
            key=st.session_state.data_editor_key,
            use_container_width=True,
            column_config={"Sumber Standardisasi": st.column_config.Column(disabled=True)},
            hide_index=False
        )
        
        selected_indices = st.session_state[st.session_state.data_editor_key].get('selected_rows', [])
        
        st.markdown("---")
        
        # Tombol Reprocess
        if selected_indices:
            if st.button(f"🔄 Reprocess {len(selected_indices)} Baris Terpilih", help="Proses ulang baris yang dipilih menggunakan database yang telah diperkaya."):
                reprocess_selected_skills(selected_indices, st.session_state.augmented_mappings)
                st.rerun() 
        else:
             st.info("💡 Klik pada baris di tabel (kolom indeks) untuk memilihnya, lalu tekan tombol Reprocess.")


if __name__ == "__main__":
    main()
