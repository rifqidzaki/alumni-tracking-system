# Alumni Tracking System

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-green?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-blue?logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap&logoColor=white)

## Project Description

**Alumni Tracking System (ATS)** adalah sistem web yang digunakan oleh admin kampus untuk melakukan **pelacakan alumni secara otomatis** melalui berbagai sumber publik seperti LinkedIn, Google Scholar, ORCID, ResearchGate, GitHub, Kaggle, website perusahaan, dan berita online.

Sistem ini menggunakan **simulasi hasil pencarian** untuk menampilkan kandidat alumni, kemudian menghitung **confidence score** menggunakan algoritma disambiguation untuk membedakan orang bernama sama. Hasil pelacakan disimpan sebagai **tracking evidence** yang dapat diverifikasi oleh admin.

Dikembangkan untuk memenuhi tugas kuliah **Rekayasa Kebutuhan** di **Universitas Muhammadiyah Malang**.

---

## Features

- **Dashboard** – Statistik alumni: total, sudah dilacak, belum dilacak, perlu verifikasi, progress per program studi
- **Input Data Alumni** – Form untuk menambahkan data alumni (nama, prodi, tahun lulus, kota, email)
- **Generate Search Query** – Otomatis menghasilkan query pencarian berdasarkan data alumni
- **Pencarian Kandidat** – Simulasi hasil pencarian dari berbagai sumber publik
- **Disambiguation & Scoring** – Menghitung confidence score dengan formula:
  ```
  Score = 0.4 × Name Match + 0.3 × Affiliation Match + 0.2 × Timeline Match + 0.1 × Field Match
  ```
- **Klasifikasi Hasil** – Strong Match (≥ 0.75), Need Verification (0.50 – 0.74), Not Match (< 0.50)
- **Cross-Validation** – Meningkatkan score jika kandidat ditemukan di lebih dari satu sumber
- **Tracking Evidence** – Menyimpan jejak bukti pelacakan alumni
- **Search & Filter** – Pencarian dan filter data alumni
- **Pagination** – Navigasi halaman untuk tabel data
- **UI Modern Bootstrap** – Desain responsive dengan sidebar, glassmorphism, dan animasi

---

## Tech Stack

| Layer    | Technology            |
| -------- | --------------------- |
| Backend  | Python 3.10+, Flask   |
| Frontend | HTML, CSS, Bootstrap 5, JavaScript |
| Database | SQLite                |
| Icons    | Bootstrap Icons       |
| Fonts    | Google Fonts (Inter)  |

---

## Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/username/alumni-tracking-system.git
   cd alumni-tracking-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

---

## Usage

1. **Tambah Alumni** – Buka menu "Input Alumni" → Isi form → Klik "Tambah Alumni"
2. **Lihat Daftar** – Buka menu "Daftar Alumni" → Gunakan search/filter untuk mencari alumni
3. **Generate Query** – Klik ikon 🔍 pada alumni → Lihat query pencarian yang dihasilkan
4. **Jalankan Pencarian** – Klik ikon 🔭 pada alumni → Lihat kandidat dengan confidence score
5. **Simpan Evidence** – Klik tombol bookmark pada kandidat yang sesuai
6. **Lihat Evidence** – Buka menu "Tracking Evidence" untuk melihat semua bukti pelacakan

---

## Project Structure

```
alumni-tracking-system/
│
├── app.py                  # Main Flask application
├── database.py             # Database models & CRUD operations
├── scoring.py              # Scoring & disambiguation logic
├── search_simulator.py     # Simulated search results
├── database.db             # SQLite database (auto-generated)
├── requirements.txt        # Python dependencies
│
├── templates/
│   ├── base.html           # Base template with sidebar layout
│   ├── dashboard.html      # Dashboard page
│   ├── alumni_form.html    # Input & list alumni page
│   ├── query_result.html   # Search query generation page
│   ├── search_result.html  # Search results & disambiguation page
│   └── evidence.html       # Tracking evidence page
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       └── main.js         # Client-side JavaScript
│
└── README.md               # Project documentation
```

---

## Demo Link

> Deployment: Dapat dideploy di [Render](https://render.com), [Railway](https://railway.app), atau [Vercel](https://vercel.com) menggunakan konfigurasi berikut:
>
> **Start Command:** `python app.py`
> **Environment:** Python 3.10+

---

## Testing Table

| No | Feature           | Input              | Expected Result             | Status |
| -- | ----------------- | ------------------ | --------------------------- | ------ |
| 1  | Input Alumni      | Data alumni        | Data tersimpan di database  | ✅ Pass |
| 2  | Generate Query    | Nama alumni        | Query pencarian muncul      | ✅ Pass |
| 3  | Search Result     | Query              | Daftar kandidat muncul      | ✅ Pass |
| 4  | Disambiguation    | Data kandidat      | Score dihitung              | ✅ Pass |
| 5  | Tracking Evidence | Kandidat dipilih   | Data tersimpan              | ✅ Pass |
| 6  | Dashboard         | Data alumni ada    | Statistik ditampilkan       | ✅ Pass |
| 7  | Search Alumni     | Keyword pencarian  | Alumni terfilter            | ✅ Pass |
| 8  | Filter Alumni     | Prodi / Tahun      | Alumni terfilter            | ✅ Pass |
| 9  | Pagination        | Navigasi halaman   | Data berpindah halaman      | ✅ Pass |
| 10 | Cross-Validation  | Kandidat ganda     | Score meningkat             | ✅ Pass |

---

## License

This project is created for educational purposes at **Universitas Muhammadiyah Malang**.
