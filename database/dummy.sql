-- SiMonPro — Dummy Data (Produksi Tekstil/Pakaian)
-- PostgreSQL 15

-- =============================================
-- Users
-- =============================================
INSERT INTO users (username, password, role) VALUES
    ('owner', 'owner123', 'owner'),
    ('admin', 'admin123', 'admin');

-- =============================================
-- Kategori Produk
-- =============================================
INSERT INTO kategori_produk (nama_kategori) VALUES
    ('Atasan'),
    ('Bawahan'),
    ('Pakaian Dalam');

-- =============================================
-- Produk (produk_id di-generate otomatis: 1-8)
-- =============================================
INSERT INTO produk (nama_produk, deskripsi_produk, satuan, gambar, status_aktif, nama_kategori) VALUES
    ('Kaos Polos Pria',      'Kaos oblong katun combed 30s lengan pendek',  'pcs', NULL, TRUE, 'Atasan'),
    ('Kemeja Formal Pria',   'Kemeja formal bahan poplin lengan panjang',    'pcs', NULL, TRUE, 'Atasan'),
    ('Kaos Polo Wanita',     'Kaos polo bahan lacoste lengan pendek',        'pcs', NULL, TRUE, 'Atasan'),
    ('Celana Chino Pria',    'Celana chino slim fit bahan kanvas',           'pcs', NULL, TRUE, 'Bawahan'),
    ('Celana Jeans Wanita',  'Celana jeans skinny bahan denim stretch',      'pcs', NULL, TRUE, 'Bawahan'),
    ('Rok Midi Wanita',      'Rok midi bahan katun motif polos',             'pcs', NULL, TRUE, 'Bawahan'),
    ('Kaos Dalam Pria',      'Kaos dalam bahan katun ribbed lengan pendek',  'pcs', NULL, TRUE, 'Pakaian Dalam'),
    ('Celana Dalam Wanita',  'Celana dalam bahan katun elastis',             'pcs', NULL, TRUE, 'Pakaian Dalam');

-- =============================================
-- Target Produksi (periode bulanan Jan-Apr 2025)
-- produk_id: 1=Kaos Polos Pria, 2=Kemeja Formal Pria, 3=Kaos Polo Wanita,
--            4=Celana Chino Pria, 5=Celana Jeans Wanita, 6=Rok Midi Wanita,
--            7=Kaos Dalam Pria, 8=Celana Dalam Wanita
-- =============================================
INSERT INTO target_produksi (produk_id, periode, tanggal_mulai, tanggal_selesai, jumlah_target) VALUES
    -- Januari
    (1, 'bulanan', '2025-01-01', '2025-01-31', 3000),
    (2, 'bulanan', '2025-01-01', '2025-01-31', 2000),
    (3, 'bulanan', '2025-01-01', '2025-01-31', 2500),
    (4, 'bulanan', '2025-01-01', '2025-01-31', 1800),
    (5, 'bulanan', '2025-01-01', '2025-01-31', 2000),
    (6, 'bulanan', '2025-01-01', '2025-01-31', 1500),
    (7, 'bulanan', '2025-01-01', '2025-01-31', 4000),
    (8, 'bulanan', '2025-01-01', '2025-01-31', 3500),
    -- Februari
    (1, 'bulanan', '2025-02-01', '2025-02-28', 3200),
    (2, 'bulanan', '2025-02-01', '2025-02-28', 2200),
    (3, 'bulanan', '2025-02-01', '2025-02-28', 2700),
    (4, 'bulanan', '2025-02-01', '2025-02-28', 2000),
    (5, 'bulanan', '2025-02-01', '2025-02-28', 2200),
    (6, 'bulanan', '2025-02-01', '2025-02-28', 1700),
    (7, 'bulanan', '2025-02-01', '2025-02-28', 4200),
    (8, 'bulanan', '2025-02-01', '2025-02-28', 3700),
    -- Maret
    (1, 'bulanan', '2025-03-01', '2025-03-31', 3500),
    (2, 'bulanan', '2025-03-01', '2025-03-31', 2500),
    (3, 'bulanan', '2025-03-01', '2025-03-31', 3000),
    (4, 'bulanan', '2025-03-01', '2025-03-31', 2200),
    (5, 'bulanan', '2025-03-01', '2025-03-31', 2500),
    (6, 'bulanan', '2025-03-01', '2025-03-31', 2000),
    (7, 'bulanan', '2025-03-01', '2025-03-31', 4500),
    (8, 'bulanan', '2025-03-01', '2025-03-31', 4000),
    -- April
    (1, 'bulanan', '2025-04-01', '2025-04-30', 3800),
    (2, 'bulanan', '2025-04-01', '2025-04-30', 2800),
    (3, 'bulanan', '2025-04-01', '2025-04-30', 3200),
    (4, 'bulanan', '2025-04-01', '2025-04-30', 2400),
    (5, 'bulanan', '2025-04-01', '2025-04-30', 2700),
    (6, 'bulanan', '2025-04-01', '2025-04-30', 2200),
    (7, 'bulanan', '2025-04-01', '2025-04-30', 5000),
    (8, 'bulanan', '2025-04-01', '2025-04-30', 4500);

-- =============================================
-- Produksi Harian (Januari 2025)
-- =============================================
INSERT INTO produksi_harian (tanggal, produk_id, jumlah_aktual, jumlah_defect, penanggung_jawab, kendala_produksi) VALUES
    ('2025-01-02', 1, 120, 3,  'Budi Santoso',   NULL),
    ('2025-01-02', 2, 80,  2,  'Siti Rahayu',    NULL),
    ('2025-01-02', 7, 160, 4,  'Dewi Kurniawan', NULL),
    ('2025-01-03', 1, 115, 4,  'Budi Santoso',   'Mesin jahit no.3 rusak'),
    ('2025-01-03', 3, 100, 3,  'Siti Rahayu',    NULL),
    ('2025-01-03', 8, 140, 3,  'Dewi Kurniawan', NULL),
    ('2025-01-06', 1, 125, 2,  'Budi Santoso',   NULL),
    ('2025-01-06', 4, 72,  2,  'Siti Rahayu',    NULL),
    ('2025-01-06', 7, 165, 5,  'Dewi Kurniawan', 'Benang putus berkali-kali'),
    ('2025-01-07', 2, 82,  3,  'Siti Rahayu',    NULL),
    ('2025-01-07', 5, 80,  2,  'Budi Santoso',   NULL),
    ('2025-01-07', 8, 142, 4,  'Dewi Kurniawan', NULL),
    ('2025-01-08', 1, 130, 2,  'Budi Santoso',   NULL),
    ('2025-01-08', 3, 105, 3,  'Siti Rahayu',    NULL),
    ('2025-01-08', 6, 60,  2,  'Dewi Kurniawan', NULL),
    ('2025-01-09', 2, 78,  4,  'Siti Rahayu',    'Bahan baku kain terlambat'),
    ('2025-01-09', 4, 75,  2,  'Budi Santoso',   NULL),
    ('2025-01-10', 1, 118, 3,  'Budi Santoso',   NULL),
    ('2025-01-10', 7, 168, 4,  'Dewi Kurniawan', NULL),
    ('2025-01-10', 8, 145, 3,  'Dewi Kurniawan', NULL),
    ('2025-01-13', 1, 122, 2,  'Budi Santoso',   NULL),
    ('2025-01-13', 5, 82,  2,  'Budi Santoso',   NULL),
    ('2025-01-14', 2, 85,  3,  'Siti Rahayu',    NULL),
    ('2025-01-14', 3, 108, 2,  'Siti Rahayu',    NULL),
    ('2025-01-15', 1, 128, 2,  'Budi Santoso',   NULL),
    ('2025-01-15', 6, 62,  1,  'Dewi Kurniawan', NULL),
    ('2025-01-15', 7, 162, 3,  'Dewi Kurniawan', NULL);

-- =============================================
-- Produksi Harian (Februari 2025)
-- =============================================
INSERT INTO produksi_harian (tanggal, produk_id, jumlah_aktual, jumlah_defect, penanggung_jawab, kendala_produksi) VALUES
    ('2025-02-03', 1, 132, 3,  'Budi Santoso',   NULL),
    ('2025-02-03', 2, 88,  2,  'Siti Rahayu',    NULL),
    ('2025-02-03', 7, 170, 4,  'Dewi Kurniawan', NULL),
    ('2025-02-04', 3, 110, 3,  'Siti Rahayu',    NULL),
    ('2025-02-04', 8, 148, 3,  'Dewi Kurniawan', NULL),
    ('2025-02-05', 1, 128, 5,  'Budi Santoso',   'Mesin obras mogok'),
    ('2025-02-05', 4, 80,  2,  'Budi Santoso',   NULL),
    ('2025-02-06', 2, 90,  3,  'Siti Rahayu',    NULL),
    ('2025-02-06', 5, 88,  2,  'Budi Santoso',   NULL),
    ('2025-02-07', 1, 135, 2,  'Budi Santoso',   NULL),
    ('2025-02-07', 6, 68,  2,  'Dewi Kurniawan', NULL),
    ('2025-02-07', 7, 172, 5,  'Dewi Kurniawan', 'Listrik padam 2 jam'),
    ('2025-02-10', 1, 130, 3,  'Budi Santoso',   NULL),
    ('2025-02-10', 3, 112, 3,  'Siti Rahayu',    NULL),
    ('2025-02-11', 2, 92,  2,  'Siti Rahayu',    NULL),
    ('2025-02-11', 4, 82,  2,  'Budi Santoso',   NULL),
    ('2025-02-12', 1, 138, 3,  'Budi Santoso',   NULL),
    ('2025-02-12', 8, 150, 4,  'Dewi Kurniawan', NULL),
    ('2025-02-13', 5, 90,  2,  'Budi Santoso',   NULL),
    ('2025-02-13', 7, 175, 4,  'Dewi Kurniawan', NULL);

-- =============================================
-- Produksi Harian (Maret 2025)
-- =============================================
INSERT INTO produksi_harian (tanggal, produk_id, jumlah_aktual, jumlah_defect, penanggung_jawab, kendala_produksi) VALUES
    ('2025-03-03', 1, 145, 5,  'Budi Santoso',   NULL),
    ('2025-03-03', 2, 95,  3,  'Siti Rahayu',    NULL),
    ('2025-03-03', 7, 182, 6,  'Dewi Kurniawan', 'Kualitas benang menurun'),
    ('2025-03-04', 3, 118, 4,  'Siti Rahayu',    NULL),
    ('2025-03-04', 8, 158, 5,  'Dewi Kurniawan', NULL),
    ('2025-03-05', 1, 140, 6,  'Budi Santoso',   'Kain bahan baku cacat'),
    ('2025-03-05', 4, 88,  3,  'Budi Santoso',   NULL),
    ('2025-03-06', 2, 98,  4,  'Siti Rahayu',    NULL),
    ('2025-03-06', 5, 98,  3,  'Budi Santoso',   NULL),
    ('2025-03-07', 1, 148, 4,  'Budi Santoso',   NULL),
    ('2025-03-07', 6, 78,  3,  'Dewi Kurniawan', NULL),
    ('2025-03-07', 7, 185, 7,  'Dewi Kurniawan', 'Mesin jahit perlu servis'),
    ('2025-03-10', 1, 150, 4,  'Budi Santoso',   NULL),
    ('2025-03-10', 3, 122, 4,  'Siti Rahayu',    NULL),
    ('2025-03-11', 2, 100, 3,  'Siti Rahayu',    NULL),
    ('2025-03-11', 4, 90,  3,  'Budi Santoso',   NULL),
    ('2025-03-12', 1, 152, 3,  'Budi Santoso',   NULL),
    ('2025-03-12', 8, 160, 5,  'Dewi Kurniawan', NULL),
    ('2025-03-13', 5, 100, 3,  'Budi Santoso',   NULL),
    ('2025-03-13', 7, 188, 6,  'Dewi Kurniawan', NULL);

-- =============================================
-- Produksi Harian (April 2025)
-- =============================================
INSERT INTO produksi_harian (tanggal, produk_id, jumlah_aktual, jumlah_defect, penanggung_jawab, kendala_produksi) VALUES
    ('2025-04-01', 1, 155, 3,  'Budi Santoso',   NULL),
    ('2025-04-01', 2, 105, 2,  'Siti Rahayu',    NULL),
    ('2025-04-01', 7, 195, 5,  'Dewi Kurniawan', NULL),
    ('2025-04-02', 3, 125, 3,  'Siti Rahayu',    NULL),
    ('2025-04-02', 8, 168, 4,  'Dewi Kurniawan', NULL),
    ('2025-04-03', 1, 152, 4,  'Budi Santoso',   NULL),
    ('2025-04-03', 4, 95,  2,  'Budi Santoso',   NULL),
    ('2025-04-04', 2, 108, 3,  'Siti Rahayu',    NULL),
    ('2025-04-04', 5, 105, 2,  'Budi Santoso',   NULL),
    ('2025-04-07', 1, 158, 2,  'Budi Santoso',   NULL),
    ('2025-04-07', 6, 85,  2,  'Dewi Kurniawan', NULL),
    ('2025-04-07', 7, 198, 4,  'Dewi Kurniawan', NULL),
    ('2025-04-08', 1, 160, 3,  'Budi Santoso',   NULL),
    ('2025-04-08', 3, 128, 3,  'Siti Rahayu',    NULL),
    ('2025-04-09', 2, 110, 2,  'Siti Rahayu',    NULL),
    ('2025-04-09', 4, 98,  2,  'Budi Santoso',   NULL),
    ('2025-04-10', 1, 162, 2,  'Budi Santoso',   NULL),
    ('2025-04-10', 8, 170, 3,  'Dewi Kurniawan', NULL),
    ('2025-04-11', 5, 108, 2,  'Budi Santoso',   NULL),
    ('2025-04-11', 7, 200, 4,  'Dewi Kurniawan', NULL);

-- =============================================
-- Detail Defect
-- defect_id: 1=Kecacatan Fisik, 2=Kesalahan Proses, 3=Kerusakan Material
-- =============================================
INSERT INTO detail_defect (produksi_id, defect_id, jumlah_defect) VALUES
    -- Januari (produksi_id 1-27)
    (1,  1, 2), (1,  2, 1),
    (2,  1, 1), (2,  3, 1),
    (3,  2, 2), (3,  3, 2),
    (4,  1, 2), (4,  2, 1), (4,  3, 1),
    (5,  1, 2), (5,  2, 1),
    (6,  2, 2), (6,  3, 1),
    (7,  1, 1), (7,  2, 1),
    (8,  1, 1), (8,  3, 1),
    (9,  1, 3), (9,  2, 2),
    (10, 1, 2), (10, 2, 1),
    (11, 1, 1), (11, 2, 1),
    (12, 2, 2), (12, 3, 2),
    (13, 1, 1), (13, 2, 1),
    (14, 1, 2), (14, 2, 1),
    (15, 1, 1), (15, 3, 1),
    (16, 1, 2), (16, 2, 2),
    (17, 1, 1), (17, 2, 1),
    (18, 1, 2), (18, 2, 1),
    (19, 1, 2), (19, 3, 1),
    (20, 2, 2), (20, 3, 1),
    (21, 1, 1), (21, 2, 1),
    (22, 1, 1), (22, 2, 1),
    (23, 1, 2), (23, 2, 1),
    (24, 1, 1), (24, 2, 1),
    (25, 1, 1), (25, 2, 1),
    (26, 1, 1),
    (27, 2, 2), (27, 3, 1),
    -- Februari (produksi_id 28-47)
    (28, 1, 2), (28, 2, 1),
    (29, 1, 1), (29, 2, 1),
    (30, 2, 2), (30, 3, 2),
    (31, 1, 2), (31, 2, 1),
    (32, 2, 2), (32, 3, 1),
    (33, 1, 3), (33, 2, 2),
    (34, 1, 1), (34, 2, 1),
    (35, 1, 2), (35, 2, 1),
    (36, 1, 1), (36, 2, 1),
    (37, 1, 1), (37, 2, 1),
    (38, 1, 1), (38, 3, 1),
    (39, 1, 3), (39, 2, 2),
    (40, 1, 2), (40, 2, 1),
    (41, 1, 2), (41, 2, 1),
    (42, 1, 1), (42, 2, 1),
    (43, 1, 2), (43, 2, 1),
    (44, 2, 2), (44, 3, 2),
    (45, 1, 1), (45, 2, 1),
    (46, 1, 1), (46, 2, 1),
    (47, 2, 2), (47, 3, 2),
    -- Maret (produksi_id 48-67)
    (48, 1, 3), (48, 2, 2),
    (49, 1, 2), (49, 2, 1),
    (50, 1, 3), (50, 2, 2), (50, 3, 1),
    (51, 1, 2), (51, 2, 2),
    (52, 2, 3), (52, 3, 2),
    (53, 1, 3), (53, 2, 2), (53, 3, 1),
    (54, 1, 2), (54, 2, 1),
    (55, 1, 2), (55, 2, 2),
    (56, 1, 2), (56, 2, 2),
    (57, 1, 2), (57, 2, 2),
    (58, 1, 2), (58, 3, 1),
    (59, 1, 4), (59, 2, 3),
    (60, 1, 2), (60, 2, 2),
    (61, 1, 2), (61, 2, 1),
    (62, 1, 2), (62, 2, 1),
    (63, 1, 2), (63, 2, 1),
    (64, 1, 2), (64, 2, 1),
    (65, 2, 3), (65, 3, 2),
    (66, 1, 2), (66, 2, 1),
    (67, 1, 4), (67, 2, 2),
    -- April (produksi_id 68-87)
    (68, 1, 2), (68, 2, 1),
    (69, 1, 1), (69, 2, 1),
    (70, 1, 3), (70, 2, 2),
    (71, 1, 2), (71, 2, 1),
    (72, 2, 2), (72, 3, 2),
    (73, 1, 2), (73, 2, 2),
    (74, 1, 1), (74, 2, 1),
    (75, 1, 2), (75, 2, 1),
    (76, 1, 1), (76, 2, 1),
    (77, 1, 1), (77, 2, 1),
    (78, 1, 1), (78, 3, 1),
    (79, 1, 2), (79, 2, 2),
    (80, 1, 2), (80, 2, 1),
    (81, 1, 2), (81, 2, 1),
    (82, 1, 1), (82, 2, 1),
    (83, 1, 2), (83, 2, 1),
    (84, 2, 2), (84, 3, 1),
    (85, 1, 1), (85, 2, 1),
    (86, 1, 2), (86, 2, 2),
    (87, 2, 2), (87, 3, 2);
