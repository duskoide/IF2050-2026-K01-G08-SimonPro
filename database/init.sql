-- SiMonPro (Sistem Monitoring Produksi) — Database Schema
-- PostgreSQL 15

CREATE TYPE user_role AS ENUM ('owner', 'admin');
CREATE TYPE periode_type AS ENUM ('harian', 'mingguan', 'bulanan', 'tahunan');

CREATE TABLE users (
    user_id    SERIAL PRIMARY KEY,
    username   VARCHAR(100) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    role       user_role    NOT NULL
);

CREATE TABLE kategori_produk (
    kategori_id   SERIAL PRIMARY KEY,
    nama_kategori VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE produk (
    kode_produk     VARCHAR(50)  PRIMARY KEY,
    nama_produk     VARCHAR(255) NOT NULL,
    deskripsi_produk TEXT,
    satuan          VARCHAR(50),
    gambar          TEXT,
    status_aktif    BOOLEAN      NOT NULL DEFAULT TRUE,
    nama_kategori   VARCHAR(100) NOT NULL REFERENCES kategori_produk(nama_kategori)
);

CREATE TABLE target_produksi (
    target_id       SERIAL PRIMARY KEY,
    kode_produk     VARCHAR(50)   NOT NULL REFERENCES produk(kode_produk),
    periode         periode_type  NOT NULL,
    tanggal_mulai   DATE          NOT NULL,
    tanggal_selesai DATE          NOT NULL,
    jumlah_target   INT           NOT NULL CHECK (jumlah_target >= 0),
    CONSTRAINT chk_date_range CHECK (tanggal_selesai >= tanggal_mulai)
);

CREATE TABLE produksi_harian (
    produksi_id      SERIAL PRIMARY KEY,
    tanggal          DATE         NOT NULL,
    kode_produk      VARCHAR(50)  NOT NULL REFERENCES produk(kode_produk),
    jumlah_aktual    INT          NOT NULL CHECK (jumlah_aktual >= 0),
    jumlah_defect    INT          NOT NULL CHECK (jumlah_defect >= 0),
    penanggung_jawab VARCHAR(255) NOT NULL,
    kendala_produksi  TEXT,
    CONSTRAINT chk_defect_not_exceed_aktual CHECK (jumlah_defect <= jumlah_aktual)
);

CREATE TABLE sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id    INT       NOT NULL REFERENCES users(user_id),
    login_time TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active  BOOLEAN   NOT NULL DEFAULT TRUE
);