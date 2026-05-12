# SiMonPro - Sistem Monitoring Produksi

## Penjelasan Singkat Aplikasi

SiMonPro (Sistem Monitoring Produksi) adalah aplikasi desktop yang digunakan untuk memantau dan mengelola aktivitas produksi, khususnya pada bidang tekstil dan pakaian. Aplikasi ini membantu Owner dan Admin dalam melihat performa produksi, pencapaian target, serta tingkat defect melalui dashboard yang terintegrasi.

Fitur utama yang tersedia mencakup autentikasi pengguna, dashboard monitoring produksi, pengelolaan data produk dan kategori, pencatatan target serta produksi harian, pencatatan defect, dan pembuatan laporan.

---

## Prasyarat dan Instalasi

### Prasyarat

Pastikan perangkat telah memiliki:

- Python 3.10 atau lebih tinggi
- Docker dan Docker Compose
- PostgreSQL 15 (dijalankan melalui Docker Compose)
- pip atau uv

### Langkah Instalasi

1. **Klon repositori proyek**

   ```bash
   git clone https://github.com/duskoide/IF2050-2026-K01-G08-SimonPro.git
   cd IF2050-2026-K01-G08-SimonPro
   ```

2. **Buat dan jalankan container PostgreSQL**

   Aplikasi menggunakan Docker Compose untuk menyediakan basis data PostgreSQL. Jalankan perintah berikut:

   ```bash
   docker compose up -d
   ```

   Container ini akan secara otomatis menjalankan skema basis data (`database/init.sql`) dan data dummy (`database/dummy.sql`) pada pertama kali dijalankan.

3. **Instal dependensi Python**

   Jika menggunakan **pip**:

   ```bash
   pip install -r requirements.txt
   ```

   Atau jika menggunakan **uv**:

   ```bash
   uv sync
   ```

4. **Konfigurasi koneksi basis data (opsional)**

   Secara default, aplikasi terhubung ke basis data dengan konfigurasi berikut:

   - Host: `localhost`
   - Port: `5433`
   - Database: `simonpro`
   - Username: `postgres`
   - Password: `secret`

   Jika perlu mengubah konfigurasi, atur variabel lingkungan berikut sebelum menjalankan aplikasi:

   ```bash
   set DB_HOST=localhost
   set DB_PORT=5433
   set DB_NAME=simonpro
   set DB_USER=postgres
   set DB_PASSWORD=secret
   ```

---

## Cara Menjalankan Aplikasi

Setelah seluruh prasyarat terpenuhi dan instalasi selesai, ikuti langkah-langkah berikut untuk menjalankan aplikasi:

1. **Pastikan container PostgreSQL aktif**

   ```bash
   docker compose ps
   ```

   Jika container tidak berjalan, jalankan kembali dengan:

   ```bash
   docker compose up -d
   ```

2. **Jalankan aplikasi**

   ```bash
   python main.py
   ```

3. **Login ke aplikasi**

   Setelah aplikasi terbuka, gunakan salah satu akun dummy berikut untuk masuk:

   - Username: `owner` - Password: `owner123` (peran: Owner)
   - Username: `admin` - Password: `admin123` (peran: Admin)

4. **Menggunakan aplikasi**

   Setelah berhasil login, Anda akan diarahkan ke halaman Dashboard yang menampilkan ringkasan performa produksi. Gunakan menu navigasi di sisi kiri untuk berpindah antar fitur. Untuk keluar dari aplikasi, klik tombol **Keluar** pada menu navigasi.

---

## Daftar Modul yang Diimplementasikan

### Autentikasi dan Manajemen Sesi

| Nama Modul | Deskripsi |
|------------|-----------|
| Login | Halaman autentikasi pengguna dengan validasi username dan password, dilengkapi dengan manajemen sesi yang tersimpan di basis data. |

### Dashboard dan Monitoring

| Nama Modul | Deskripsi |
|------------|-----------|
| Dashboard | Halaman utama yang menampilkan ringkasan performa produksi, termasuk total produksi, persentase pencapaian target, tingkat defect, dan jumlah produk aktif. |

### Manajemen Data Master

| Nama Modul | Deskripsi |
|------------|-----------|
| Produk | Modul untuk mengelola data produk, termasuk nama produk, deskripsi, satuan, gambar, status aktif, dan kategori. |
| Kategori Produk | Modul klasifikasi produk ke dalam kategori tertentu, seperti Atasan, Bawahan, dan Pakaian Dalam. |

### Operasional Produksi

| Nama Modul | Deskripsi |
|------------|-----------|
| Target Produksi | Modul untuk menetapkan target jumlah produksi per produk dalam periode tertentu (harian, mingguan, bulanan, atau tahunan). |
| Input Produksi | Modul pencatatan hasil produksi harian, termasuk jumlah aktual, jumlah defect, penanggung jawab, dan kendala produksi. |
| Defect | Modul pencatatan dan klasifikasi kecacatan produk berdasarkan tipe defect yang telah ditentukan. |

### Pelaporan

| Nama Modul | Deskripsi |
|------------|-----------|
| Pencapaian | Modul evaluasi pencapaian target produksi dibandingkan dengan hasil aktual yang tercatat. |
| Laporan | Modul generasi laporan produksi dalam bentuk dokumen. |

---

## Daftar Tabel Basis Data

### 1. users

Tabel untuk menyimpan data pengguna aplikasi.

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| user_id | SERIAL | Primary Key |
| username | VARCHAR(100) | Nama pengguna (unik, wajib diisi) |
| password | VARCHAR(255) | Kata sandi pengguna (wajib diisi) |
| role | user_role | Peran pengguna: `owner` atau `admin` |

### 2. kategori_produk

Tabel untuk menyimpan kategori produk.

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| kategori_id | SERIAL | Primary Key |
| nama_kategori | VARCHAR(100) | Nama kategori produk (unik, wajib diisi) |

### 3. produk

Tabel untuk menyimpan data produk yang diproduksi.

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| produk_id | SERIAL | Primary Key |
| nama_produk | VARCHAR(255) | Nama produk (wajib diisi) |
| deskripsi_produk | TEXT | Deskripsi produk |
| satuan | VARCHAR(50) | Satuan produk |
| gambar | TEXT | Path atau URL gambar produk |
| status_aktif | BOOLEAN | Status aktif produk (default: TRUE) |
| nama_kategori | VARCHAR(100) | Foreign Key ke `kategori_produk(nama_kategori)` |

### 4. target_produksi

Tabel untuk menyimpan target produksi per periode.

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| target_id | SERIAL | Primary Key |
| produk_id | INT | Foreign Key ke `produk(produk_id)` |
| periode | periode_type | Jenis periode: `harian`, `mingguan`, `bulanan`, atau `tahunan` |
| tanggal_mulai | DATE | Tanggal mulai periode target (wajib diisi) |
| tanggal_selesai | DATE | Tanggal akhir periode target (wajib diisi) |
| jumlah_target | INT | Jumlah target produksi (wajib diisi, minimal 0) |

### 5. produksi_harian

Tabel untuk mencatat hasil produksi harian.

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| produksi_id | SERIAL | Primary Key |
| tanggal | DATE | Tanggal produksi (wajib diisi) |
| produk_id | INT | Foreign Key ke `produk(produk_id)` |
| jumlah_aktual | INT | Jumlah produksi aktual (wajib diisi, minimal 0) |
| jumlah_defect | INT | Jumlah produk cacat (wajib diisi, minimal 0) |
| penanggung_jawab | VARCHAR(255) | Nama penanggung jawab produksi (wajib diisi) |
| kendala_produksi | TEXT | Catatan kendala yang dihadapi saat produksi |

### 6. tipe_defect

Tabel untuk menyimpan klasifikasi jenis kecacatan produk.

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| defect_id | SERIAL | Primary Key |
| nama_defect | VARCHAR(100) | Nama jenis defect (unik, wajib diisi) |

### 7. detail_defect

Tabel untuk menyimpan rincian kecacatan pada setiap catatan produksi harian.

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| detail_id | SERIAL | Primary Key |
| produksi_id | INT | Foreign Key ke `produksi_harian(produksi_id)` dengan `ON DELETE CASCADE` |
| defect_id | INT | Foreign Key ke `tipe_defect(defect_id)` |
| jumlah_defect | INT | Jumlah produk dengan jenis defect tertentu (wajib diisi, minimal 0) |

### 8. sessions

Tabel untuk menyimpan data sesi login pengguna.

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| session_id | VARCHAR(255) | Primary Key |
| user_id | INT | Foreign Key ke `users(user_id)` |
| login_time | TIMESTAMP | Waktu login (default: waktu saat ini) |
| is_active | BOOLEAN | Status sesi aktif (default: TRUE) |

---

## Catatan Pengembangan

- Aplikasi ini menggunakan arsitektur berbasis Model-View-Controller (MVC) untuk memisahkan logika bisnis, antarmuka pengguna, dan pengontrol alur kerja.
- Semua koneksi ke basis data dikelola melalui kelas singleton `Database` yang terdapat pada modul `src/database/db_connection.py` untuk memastikan efisiensi koneksi.
- Data dummy yang disediakan mencakup periode Januari hingga April 2025 untuk keperluan pengujian dan demonstrasi fitur dashboard.
