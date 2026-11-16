import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from io import BytesIO

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Scraper Berita PDRB", layout="wide")
st.title("📰 Scraper Berita PDRB Sumatera Barat")
st.markdown("Aplikasi ini mencari berita spesifik berdasarkan Wilayah, Komponen PDRB, dan Rentang Waktu.")

# ==========================================
# KAMUS WILAYAH & KEYWORD SPESIFIK
# ==========================================
wilayah_dict = {
    "Provinsi Sumatera Barat": '("Sumatera Barat" OR "Sumbar" OR "Pemprov Sumbar")',
    "Kota Padang": '("Kota Padang" OR "Pemko Padang" OR "Wako Padang" OR "Pemkot Padang")',
    "Kota Bukittinggi": '("Kota Bukittinggi" OR "Pemko Bukittinggi" OR "Wako Bukittinggi")',
    "Kota Payakumbuh": '("Kota Payakumbuh" OR "Pemko Payakumbuh" OR "Wako Payakumbuh")',
    "Kota Solok": '("Kota Solok" OR "Pemko Solok" OR "Wako Solok")',
    "Kota Sawahlunto": '("Kota Sawahlunto" OR "Pemko Sawahlunto" OR "Wako Sawahlunto")',
    "Kota Padang Panjang": '("Kota Padang Panjang" OR "Pemko Padang Panjang")',
    "Kota Pariaman": '("Kota Pariaman" OR "Pemko Pariaman" OR "Wako Pariaman")',
    "Kab. Agam": '("Kabupaten Agam" OR "Pemkab Agam" OR "Bupati Agam")',
    "Kab. Pasaman": '("Kabupaten Pasaman" OR "Pemkab Pasaman" OR "Bupati Pasaman")',
    "Kab. Pasaman Barat": '("Kabupaten Pasaman Barat" OR "Pemkab Pasaman Barat" OR "Pasbar")',
    "Kab. Lima Puluh Kota": '("Kabupaten Lima Puluh Kota" OR "Pemkab Lima Puluh Kota" OR "Lima Puluh Kota")',
    "Kab. Tanah Datar": '("Kabupaten Tanah Datar" OR "Pemkab Tanah Datar" OR "Tanah Datar")',
    "Kab. Solok": '("Kabupaten Solok" OR "Pemkab Solok" OR "Bupati Solok")',
    "Kab. Solok Selatan": '("Kabupaten Solok Selatan" OR "Pemkab Solok Selatan" OR "Solsel")',
    "Kab. Sijunjung": '("Kabupaten Sijunjung" OR "Pemkab Sijunjung" OR "Bupati Sijunjung")',
    "Kab. Dharmasraya": '("Kabupaten Dharmasraya" OR "Pemkab Dharmasraya" OR "Bupati Dharmasraya")',
    "Kab. Pesisir Selatan": '("Kabupaten Pesisir Selatan" OR "Pemkab Pesisir Selatan" OR "Pessel")',
    "Kab. Padang Pariaman": '("Kabupaten Padang Pariaman" OR "Pemkab Padang Pariaman" OR "Padang Pariaman")',
    "Kab. Kepulauan Mentawai": '("Kabupaten Kepulauan Mentawai" OR "Pemkab Mentawai" OR "Mentawai")'
}

# ==========================================
# DAFTAR KOMPONEN PDRB PENGELUARAN (35 KOMPONEN)
# ==========================================
komponen_pdrb = [
    # 1. PKRT
    {"kode": "1", "nama": "Pengeluaran Konsumsi Rumah Tangga", "keyword": '("hari raya" OR "libur sekolah" OR "diskon" OR "upah minimum" OR "inflasi")'},
    {"kode": "1.a.", "nama": "Makanan dan Minuman Non Beralkohol", "keyword": '("gagal panen" OR "serangan hama" OR "operasi pasar" OR "harga pangan naik" OR "bencana alam")'},
    {"kode": "1.b.", "nama": "Minuman Beralkohol dan Rokok", "keyword": '("rokok ilegal" OR "cukai rokok" OR "razia rokok" OR "pemusnahan rokok")'},
    {"kode": "1.c.", "nama": "Pakaian", "keyword": '("bazar murah" OR "diskon pakaian" OR "seragam gratis" OR "pakaian bekas impor")'},
    {"kode": "1.d.", "nama": "Perumahan, Air, Listrik, Gas", "keyword": '("listrik padam" OR "PDAM mati" OR "tarif listrik" OR "banjir" OR "bencana")'},
    {"kode": "1.e.", "nama": "Perabot dan Peralatan RT", "keyword": '("pameran furnitur" OR "renovasi rumah" OR "bantuan perabot" OR "kebakaran rumah")'},
    {"kode": "1.f.", "nama": "Kesehatan", "keyword": '("kabut asap" OR "karhutla" OR "wabah penyakit" OR "ISPA" OR "BPJS gratis")'},
    {"kode": "1.g.", "nama": "Transportasi/Angkutan", "keyword": '("harga tiket" OR "arus mudik" OR "libur panjang" OR "gangguan penerbangan" OR "tarif angkutan")'},
    {"kode": "1.h.", "nama": "Komunikasi", "keyword": '("gangguan jaringan" OR "internet gratis" OR "pemulihan jaringan" OR "kuota")'},
    {"kode": "1.i.", "nama": "Rekreasi dan Budaya", "keyword": '("event budaya" OR "festival" OR "kunjungan wisatawan" OR "libur panjang" OR "objek wisata")'},
    {"kode": "1.j.", "nama": "Pendidikan", "keyword": '("tahun ajaran baru" OR "PPDB" OR "pungutan liar" OR "beasiswa" OR "sekolah gratis")'},
    {"kode": "1.k.", "nama": "Penginapan dan Hotel", "keyword": '("okupansi hotel" OR "kunjungan wisatawan" OR "event pariwisata" OR "libur panjang")'},
    {"kode": "1.l.", "nama": "Barang Pribadi dan Jasa Perorangan", "keyword": '("harga emas" OR "jual emas" OR "gadai emas" OR "investasi emas")'},
    
    # 2. LNPRT
    {"kode": "2", "nama": "Pengeluaran Konsumsi LNPRT", "keyword": '("bantuan bencana" OR "kegiatan sosial" OR "ormas" OR "aksi kemanusiaan")'},
    
    # 3. Pemerintah
    {"kode": "3", "nama": "Pengeluaran Konsumsi Pemerintah", "keyword": '("perubahan APBD" OR "penyaluran bansos" OR "belanja pemerintah" OR "bantuan bencana")'},
    {"kode": "3.a.", "nama": "Konsumsi Kolektif", "keyword": '("pembangunan fasilitas publik" OR "gedung pemerintah" OR "belanja pegawai")'},
    {"kode": "3.b.", "nama": "Konsumsi Individu", "keyword": '("bansos" OR "bantuan sosial" OR "bantuan korban bencana" OR "bantuan pangan")'},
    
    # 4. PMTB
    {"kode": "4", "nama": "Pembentukan Modal Tetap Bruto", "keyword": '("proyek infrastruktur" OR "pembangunan jalan" OR "investasi" OR "peresmian proyek")'},
    {"kode": "4.a.", "nama": "Bangunan", "keyword": '("pembangunan gedung" OR "proyek konstruksi" OR "pembangunan jembatan" OR "revitalisasi pasar")'},
    {"kode": "4.b.", "nama": "Non-Bangunan", "keyword": '("impor mesin" OR "pengadaan alat berat" OR "modernisasi peralatan")'},
    
    # 5. Inventori
    {"kode": "5", "nama": "Perubahan Inventori", "keyword": '("stok pangan" OR "gudang bulog" OR "penimbunan" OR "kelangkaan barang")'},
    
    # 6. Ekspor Luar Negeri
    {"kode": "6", "nama": "Ekspor Luar Negeri", "keyword": '("pelepasan ekspor" OR "ekspor perdana" OR "pengiriman barang" OR "pelabuhan")'},
    {"kode": "6.a.", "nama": "Ekspor Barang", "keyword": '("ekspor CPO" OR "ekspor karet" OR "ekspor gambir" OR "harga komoditas global")'},
    {"kode": "6.b.", "nama": "Ekspor Jasa", "keyword": '("kunjungan wisman" OR "pariwisata mancanegara" OR "ekspor jasa")'},
    
    # 7. Impor Luar Negeri
    {"kode": "7", "nama": "Impor Luar Negeri", "keyword": '("impor barang" OR "kedatangan barang" OR "pasokan impor")'},
    {"kode": "7.a.", "nama": "Impor Barang", "keyword": '("impor BBM" OR "impor bahan baku" OR "impor pangan")'},
    {"kode": "7.b.", "nama": "Impor Jasa", "keyword": '("impor jasa" OR "tenaga kerja asing" OR "jasa luar negeri")'},
    
    # 8. Net Ekspor Antar Daerah
    {"kode": "8", "nama": "Net Ekspor Antar Daerah", "keyword": '("perdagangan antar daerah" OR "distribusi barang" OR "pasokan antar provinsi")'},
    {"kode": "8.a.", "nama": "Ekspor Antar Daerah", "keyword": '("pengiriman barang keluar daerah" OR "ekspor antar pulau")'},
    {"kode": "8.b.", "nama": "Impor Antar Daerah", "keyword": '("pasokan dari luar daerah" OR "impor antar pulau")'},
    
    # Total PDRB
    {"kode": "PDRB", "nama": "P D R B", "keyword": '("pertumbuhan ekonomi" OR "rilis BPS" OR "ekonomi daerah")'}
]

# ==========================================
# SIDEBAR: PENGATURAN INPUT
# ==========================================
st.sidebar.header("⚙️ Pengaturan Scraping")

# 1. Pilih Wilayah (Dropdown)
wilayah_terpilih = st.sidebar.selectbox("Pilih Wilayah:", list(wilayah_dict.keys()))

# 2. Pilih Rentang Waktu
st.sidebar.subheader("Rentang Waktu")
col1, col2 = st.sidebar.columns(2)
with col1:
    tahun_awal = st.number_input("Tahun Awal", min_value=2020, max_value=2030, value=2025)
    tw_awal = st.selectbox("Triwulan Awal", ["Q1", "Q2", "Q3", "Q4"], index=0)
with col2:
    tahun_akhir = st.number_input("Tahun Akhir", min_value=2020, max_value=2030, value=2026)
    tw_akhir = st.selectbox("Triwulan Akhir", ["Q1", "Q2", "Q3", "Q4"], index=2)

# 3. Pilih Komponen
komponen_terpilih = st.sidebar.multiselect(
    "Pilih Komponen PDRB:", 
    options=[k['nama'] for k in komponen_pdrb],
    default=[k['nama'] for k in komponen_pdrb] # Default pilih semua
)

# ==========================================
# FUNGSI PENDUKUNG
# ==========================================
def get_triwulan_range(tahun_awal, tw_awal, tahun_akhir, tw_akhir):
    tw_map = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
    start_num = tahun_awal * 10 + tw_map[tw_awal]
    end_num = tahun_akhir * 10 + tw_map[tw_akhir]
    
    if start_num > end_num:
        return []
    
    periods = []
    current = start_num
    while current <= end_num:
        tahun = current // 10
        tw_num = current % 10
        tw_str = f"Q{tw_num}"
        periods.append((tahun, tw_str))
        current += 1
        if current % 10 == 5:
            current = (current // 10 + 1) * 10 + 1
    return periods

def hitung_tanggal(tahun, triwulan):
    if triwulan == "Q1": return f"{tahun}-01-01", f"{tahun}-03-31"
    elif triwulan == "Q2": return f"{tahun}-04-01", f"{tahun}-06-30"
    elif triwulan == "Q3": return f"{tahun}-07-01", f"{tahun}-09-30"
    elif triwulan == "Q4": return f"{tahun}-10-01", f"{tahun}-12-31"

def ambil_berita(keyword, wilayah_query, start_date, end_date, max_berita=4):
    # Gabungkan keyword komponen dengan query wilayah spesifik
    query = f'{keyword} {wilayah_query}'
    url = f"https://news.google.com/rss/search?q={query}+after:{start_date}+before:{end_date}&hl=id&gl=ID&ceid=ID:id"
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        teks_gabungan = []
        judul_unik = set()
        
        for item in items:
            judul = item.title.text.split(' - ')[0]
            if judul not in judul_unik:
                teks_gabungan.append(f"- {judul}")
                judul_unik.add(judul)
            
            if len(teks_gabungan) >= max_berita:
                break
                
        return "\n".join(teks_gabungan) if teks_gabungan else "Tidak ada berita."
    except Exception as e:
        return f"Error: {e}"

# ==========================================
# EKSEKUSI UTAMA
# ==========================================
if st.sidebar.button("🚀 Mulai Scraping"):
    if not komponen_terpilih:
        st.warning("Silakan pilih minimal satu komponen!")
    else:
        daftar_periode = get_triwulan_range(tahun_awal, tw_awal, tahun_akhir, tw_akhir)
        
        if not daftar_periode:
            st.error("Rentang waktu tidak valid! Pastikan Tahun/Triwulan Akhir lebih besar dari Awal.")
        else:
            query_wilayah = wilayah_dict[wilayah_terpilih]
            
            st.info(f"Wilayah: **{wilayah_terpilih}** | Periode: {', '.join([f'{tw}-{thn}' for thn, tw in daftar_periode])}")
            
            hasil_data = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, nama_komp in enumerate(komponen_terpilih):
                status_text.text(f"Scraping: {nama_komp} ({i+1}/{len(komponen_terpilih)})...")
                
                keyword = next((k['keyword'] for k in komponen_pdrb if k['nama'] == nama_komp), "")
                
                row_data = {
                    "Kode": next((k['kode'] for k in komponen_pdrb if k['nama'] == nama_komp), ""),
                    "Komponen": nama_komp
                }
                
                for (thn, tw) in daftar_periode:
                    start_date, end_date = hitung_tanggal(thn, tw)
                    berita = ambil_berita(keyword, query_wilayah, start_date, end_date)
                    col_name = f"{tw}_{thn}"
                    row_data[col_name] = berita
                    time.sleep(1.5) # Jeda antar pencarian
                
                hasil_data.append(row_data)
                progress_bar.progress((i + 1) / len(komponen_terpilih))
                
            status_text.text("Scraping Selesai!")
            
            # Tampilkan Hasil
            st.subheader("📋 Hasil Scraping")
            df_hasil = pd.DataFrame(hasil_data)
            st.dataframe(df_hasil, use_container_width=True)
            
            # Download Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_hasil.to_excel(writer, index=False, sheet_name='Hasil_Scraping')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Download Hasil (Excel)",
                data=excel_data,
                file_name=f"Scraping_{wilayah_terpilih.replace(' ', '_')}_{tw_awal}{tahun_awal}_sd_{tw_akhir}{tahun_akhir}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )