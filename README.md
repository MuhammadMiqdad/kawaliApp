# kawaliApp
# 🏛️ Portal Pencarian Prasasti Kawali

Portal pencarian semantik untuk eksplorasi prasasti kuno Sunda menggunakan Apache Jena Fuseki SPARQL Endpoint.

## 📋 Daftar Isi
- [Panduan Installasi Aplikasi](#-panduan-installasi-aplikasi)
- [Panduan Menggunakan Aplikasi](#-Panduan-Menggunakan-Aplikasi)
- [Dokumentasi Interface](#-dokumentasi-interface)

---

## 🚀 Panduan Installasi Aplikasi

### A Persyaratan Sistem

**Software yang dibutuhkan:**
- **Python 3.7** atau lebih baru
- **Java 17** atau lebih baru (untuk Apache Jena Fuseki 5.4.0)
  
> ⚠️ **Penting**: Fuseki 5.4.0 membutuhkan minimal Java versi 17
> - Cek versi Java: `java -version`
> - Download Java 17+: [Oracle Java Downloads](https://www.oracle.com/java/technologies/downloads/)

### B Download Apache Jena Fuseki

1. Kunjungi website resmi Apache Jena: [https://jena.apache.org/download/](https://jena.apache.org/download/)
2. Pilih **Apache Jena Fuseki** dari daftar download
3. Download file ZIP/TAR sesuai sistem operasi Anda

### C Ekstrak dan Setup

1. **Ekstrak file** yang telah didownload ke direktori yang diinginkan
   ```
   Contoh: C:\Users\Asus\Downloads\
   ```
2. **Tambahkan Apache Jena ke PATH** (opsional, untuk memudahkan akses)

### D Menjalankan Fuseki Server

1. **Buka Command Prompt (CMD)**
2. **Navigasi ke folder Jena Fuseki:**
   ```cmd
   cd C:\Users\Asus\Downloads\apache-jena-fuseki-5.4.0\apache-jena-fuseki-5.4.0
   ```
   *(Sesuaikan dengan lokasi dan versi yang didownload)*

3. **Jalankan Fuseki server:**
   ```cmd
   fuseki-server
   ```
   > 📝 **Note**: Pastikan Java versi yang terinstall kompatibel dengan Fuseki 5.4.0 (minimal Java 17)

4. **Buka browser dan akses:**
   ```
   http://localhost:3030
   ```

### E Membuat Dataset

1. Di halaman Apache Jena Fuseki, klik **"New Dataset"**
2. **Isi konfigurasi dataset:**
   - **Dataset name**: `kawali` (atau nama bebas sesuai keinginan)
   - **Dataset type**: Pilih **"Persistent (TDB2)"**
3. Klik **"Create Dataset"**
4. Dataset berhasil dibuat - Anda akan melihat endpoint dataset yang baru dibuat

### F Upload Data TTL

1. **Klik nama dataset** yang telah dibuat (misalnya "kawali")
2. Pilih **"Add Data"**
3. Klik **"Select Files"**
4. **Masukkan file TTL** yang ingin diuji coba untuk query SPARQL
5. **Upload file** - Data sekarang siap untuk diquery melalui SPARQL endpoint

### G Library Python yang Digunakan

```python
streamlit     # Framework untuk membuat web application
pandas        # Untuk manipulasi data dan export ke CSV/Excel
requests      # Untuk komunikasi HTTP dengan SPARQL endpoint
json          # Untuk parsing response JSON dari Fuseki
csv           # Untuk export data ke format CSV
typing        # Untuk type hints dalam kode
urllib.parse  # Untuk encoding URL dan query parameters
```

**Install dependencies:**
```bash
pip install streamlit pandas requests
```

---

## 🎯 Panduan Menggunakan Aplikasi

### A Persiapan

1. **Pastikan Fuseki server berjalan:**
   ```cmd
   # Buka Command Prompt
   cd C:\Users\Asus\Downloads\apache-jena-fuseki-5.4.0\apache-jena-fuseki-5.4.0
   fuseki-server
   ```
   Fuseki akan berjalan di: `http://localhost:3030`

2. **Menjalankan Streamlit:**
   ```bash
   python -m streamlit run kawaliApp.py
   ```

3. **Akses Aplikasi:**
   Buka browser dan akses: `http://localhost:8501`

### B Interface Utama

#### Header dan Status Koneksi
- **Status Koneksi**: Indikator hijau (✅) menunjukkan koneksi ke Fuseki berhasil
- **Endpoint Info**: Menampilkan URL SPARQL endpoint yang digunakan

#### Sidebar Statistik
- **Total Prasasti**: Jumlah manuskrip yang tersedia
- **Total Baris**: Jumlah baris naskah dalam database
- **Detail Prasasti**: Breakdown jumlah baris per prasasti

### C Fitur Pencarian

#### Jenis Pencarian

1. **Semua (All)**
   - Mencari di semua field: transliterasi, terjemahan, dan aksara
   - Gunakan untuk pencarian umum

2. **Transliterasi**
   - Mencari hanya di teks Latin (romanisasi)
   - Contoh query: `"kawali"`, `"raja"`, `"desa"`

3. **Terjemahan**
   - Mencari hanya di terjemahan Bahasa Indonesia
   - Contoh query: `"raja"`, `"tempat"`, `"desa"`

4. **Aksara Sunda**
   - Mencari dalam aksara Sunda asli
   - Input menggunakan karakter aksara Sunda

### D Tips Pencarian Efektif

- ✅ Gunakan kata kunci yang spesifik
- ✅ Pencarian tidak case-sensitive
- ✅ Coba variasi kata jika tidak menemukan hasil
- ✅ Gunakan jenis pencarian yang sesuai dengan tipe data yang dicari

---

## 📱 Dokumentasi Interface

### A Menu Utama
- <img width="475" alt="image" src="https://github.com/user-attachments/assets/8ae0d9ec-5eab-4440-96cf-d389be037c1a" />


### B Fitur Pencarian

#### Pencarian "Semua"
- Mencari di semua field (transliterasi, terjemahan, aksara)
- Hasil menampilkan semua data yang mengandung kata kunci
  <img width="732" alt="image" src="https://github.com/user-attachments/assets/ad0048f1-bae7-41ad-9648-b2a9e4a98e10" />
  <img width="752" alt="image" src="https://github.com/user-attachments/assets/e580c8fe-1003-47d0-a5c3-9e83f7d67e99" />
  <img width="823" alt="image" src="https://github.com/user-attachments/assets/867f0d9a-a185-4502-8b20-de77095b5bab" />

#### Pencarian "Transliterasi"
- Fokus pada teks Latin
- Berguna untuk pencarian berdasarkan bunyi kata
  <img width="701" alt="image" src="https://github.com/user-attachments/assets/6642fdf0-f8a6-4567-af45-f0a849642c4e" />
- Jika yg dimasukkan data aksara/terjemahannya
<img width="590" alt="image" src="https://github.com/user-attachments/assets/31ea2eb2-6b58-49a2-8359-b48c415199ee" />


#### Pencarian "Terjemahan"
- Fokus pada terjemahan Bahasa Indonesia
- Berguna untuk pencarian berdasarkan makna
  <img width="606" alt="image" src="https://github.com/user-attachments/assets/632a6be4-5886-47e0-8803-883e926d43bd" />
- Jika yg dimasukkan data aksara/latinnya
  <img width="605" alt="image" src="https://github.com/user-attachments/assets/4c387bc3-53e2-47b7-8b26-763167cc261d" />



#### Pencarian "Aksara Sunda"
- Fokus pada aksara Sunda asli
- Memerlukan input karakter aksara Sunda
  <img width="598" alt="image" src="https://github.com/user-attachments/assets/7098968c-85a2-4c67-95de-02c4e599d63c" />
- Jika yg dimasukkan data latin/terjemahannya
<img width="611" alt="image" src="https://github.com/user-attachments/assets/ee072873-cc1f-43b1-9eb1-f1168af4ccda" />



### C Tampilan Hasil

Setiap hasil pencarian menampilkan:
- **Aksara Sunda**: Teks dalam script asli
- **Transliterasi Latin**: Romanisasi teks
- **Terjemahan Indonesia**: Makna dalam Bahasa Indonesia
- **Metadata**: Informasi ID prasasti, baris, dan sumber

### D Fitur Export

Hasil pencarian dapat didownload dalam format:
- **CSV (Excel Compatible)**: Format UTF-8 BOM untuk Excel
- **CSV (UTF-8)**: Format UTF-8 standar
- **JSON**: Format JSON dengan integritas Unicode

---

## 🔗 Link Repository

**Material RDF/TTL**: [https://github.com/evanaff/rdf-turtle-semantic-web](https://github.com/evanaff/rdf-turtle-semantic-web)

---

## 👥 Tim Pengembang

- Muhammad Miqdad Alfattah Josi (140810220005)
- Muhammad Zhafran Shidiq (140810220007)  
- Evan Ahnaf Satyatama (140810220017)

**Universitas Padjadjaran**  
**Fakultas MIPA - Program Studi Teknik Informatika**  
**2025**

---

*Dikembangkan untuk penelitian dan pelestarian warisan budaya Sunda*



