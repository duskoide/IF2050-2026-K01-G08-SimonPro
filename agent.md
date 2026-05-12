# SiMonPro — Agent Reference Document

> Auto-generated inventory of the project's current state, architecture, and roadmap.

---

## 1. Project Overview

**SiMonPro** (Sistem Monitoring Produksi) is a PyQt6 desktop application for monitoring and managing textile/garment production. It targets two roles:

| Role | Access Level |
|------|-------------|
| **Owner** | Read-only: view dashboard, products, targets, achievement, defect reports |
| **Admin** | Full CRUD: manage products, categories, targets, daily production, defects |

**Tech Stack**: Python 3.10+, PyQt6, PostgreSQL 15 (via Docker), `psycopg2`, `qtawesome`, `matplotlib`, `reportlab`, `fpdf2`, `python-dateutil`, `python-dotenv`.

---

## 2. Use Cases

Derived from the README module list and database schema.

| UC # | Use Case | Actor | Status |
|------|----------|-------|--------|
| UC01 | Login / Logout | Owner, Admin | ✅ Done |
| UC02 | Kelola Data Produk (CRUD) | Admin (CRUD), Owner (Read) | ⚠️ Service/Controller done; View uses hardcoded data |
| UC03 | Kelola Kategori Produk (CRUD) | Admin (CRUD), Owner (Read) | ✅ Done |
| UC04 | Lihat Dashboard Produksi | Owner, Admin | ✅ Done (summary cards + charts) |
| UC05 | Kelola Target Produksi | Admin (CRUD), Owner (Read) | ❌ Not implemented |
| UC06 | Input Produksi Harian | Admin | ❌ Not implemented |
| UC07 | Kelola Defect | Admin (CRUD), Owner (Read) | ❌ Not implemented |
| UC08 | Lihat Pencapaian Target | Owner, Admin | ❌ Not implemented (only summary cards on dashboard) |
| UC09 | Generate Laporan | Owner, Admin | ❌ Not implemented |

### Use-Case Details

#### UC01 — Login / Logout
- User enters username & password on the login page.
- `AuthService.validate_credentials()` checks credentials against DB (plaintext comparison).
- On success, a `Session` (UUID) is created and stored in the `sessions` table.
- On logout, the session is invalidated (`is_active = FALSE` in DB).

#### UC02 — Kelola Data Produk
- **Admin** can add, edit, deactivate products; **Owner** can only view.
- Validation: nama_produk required & unique, satuan required, kategori must exist.
- Soft-delete via `status_aktif = FALSE`.

#### UC03 — Kelola Kategori Produk
- **Admin** can add, edit, delete categories; **Owner** is denied access.
- Duplicate name check (case-insensitive).

#### UC04 — Lihat Dashboard
- Displays 4 stat cards: Total Produksi, Pencapaian Target %, Tingkat Defect %, Jumlah Produk Aktif.
- Bar chart: target vs aktual per month (fallback to latest data months if current is empty).
- Line chart: defect count per month.

#### UC05 — Kelola Target Produksi (NOT YET)
- Set production targets per product per period (harian/mingguan/bulanan/tahunan).
- DB table `target_produksi` already exists with columns: `target_id`, `produk_id`, `periode`, `tanggal_mulai`, `tanggal_selesai`, `jumlah_target`.

#### UC06 — Input Produksi Harian (NOT YET)
- Record daily production: `tanggal`, `produk_id`, `jumlah_aktual`, `jumlah_defect`, `penanggung_jawab`, `kendala_produksi`.
- DB table `produksi_harian` already exists.
- Should also link to `detail_defect` for defect breakdown.

#### UC07 — Kelola Defect (NOT YET)
- Classify defects by `tipe_defect` (3 pre-seeded: Kecacatan Fisik, Kesalahan Proses, Kerusakan Material).
- Record `detail_defect` per production entry.
- DB tables `tipe_defect` and `detail_defect` already exist.

#### UC08 — Lihat Pencapaian Target (NOT YET)
- Compare `target_produksi.jumlah_target` vs actual `produksi_harian.jumlah_aktual`.
- Detailed breakdown by product, period, percentage achieved.

#### UC09 — Generate Laporan (NOT YET)
- Generate PDF/document reports from production data.
- Dependencies `reportlab` and `fpdf2` are installed but unused.

---

## 3. Classes (Current Implementation)

### 3.1 Database Layer

| Class | File | Responsibility |
|-------|------|----------------|
| `Database` | `src/database/db_connection.py` | Singleton wrapping `psycopg2`; provides `execute_query`, `execute_update`, `execute_many`, context manager |
| `get_db()` | `src/database/db_connection.py` | Module-level helper to get the singleton instance |
| `test_connection()` | `src/database/db_connection.py` | Quick DB connectivity check |

### 3.2 Models

| Class | File | Key Methods |
|-------|------|-------------|
| `User` | `src/models/User.py` | Simple data class: `user_id`, `username`, `password`, `role` |
| `Session` | `src/models/Session.py` | `create_session(user)`, `invalidate()`, `get_user_role()` |
| `KategoriProduk` | `src/models/KategoriProduk.py` | `getAll(db)`, `from_row(row)`, `tambah(db, nama)`, `simpanPerubahan(db, id, nama)`, `hapus(db, id)`, `cekDuplikasi(db, nama, exclude_id)`, `getProdukByKategori(db)` |
| `Produk` | `src/models/Produk.py` | `getAll(db)`, `getById(db, id)`, `getByKategori(db, kat)`, `getByNama(db, nama)`, `getAllIncludingInactive(db)`, `getAllWithKategori(db)`, `tambah(db, ...)`, `simpanPerubahan(db, ...)`, `nonaktifkan(db, id)`, `cekNamaExist(db, nama, exclude_id)` |

### 3.3 Services

| Class | File | Key Methods |
|-------|------|-------------|
| `AuthService` | `src/services/AuthService.py` | `validate_credentials(username, password)`, `logout(session_id)`, `is_authenticated()`, `get_current_user()`, `get_current_session()`, `_save_session()`, `_end_session()` |
| `UserDataLocal` | `src/services/UserDataLocal.py` | `find_by_username(username)` |
| `DashboardService` | `src/services/DashboardService.py` | `get_summary_data()`, `get_chart_data(months)` |
| `KategoriService` | `src/services/KategoriService.py` | `tambahKategori(nama)`, `updateKategori(id, nama)`, `hapusKategori(id)`, `getDaftarKategori()`, `getProdukTerbaru()`, `_validasiKategori(nama)` |
| `ProdukService` | `src/services/ProdukService.py` | `get_daftar_produk()`, `get_daftar_produk_termasuk_nonaktif()`, `get_produk_by_id()`, `get_produk_by_kategori()`, `cari_produk()`, `get_daftar_kategori()`, `tambah_produk()`, `simpan_perubahan()`, `nonaktifkan_produk()`, `cek_nama_tersedia()` |

### 3.4 Controllers

| Class | File | Key Methods |
|-------|------|-------------|
| `LoginController` | `src/controllers/LoginController.py` | `login(username, password)` |
| `KategoriController` | `src/controllers/KategoriController.py` | `request_edit_kategori()`, `submit_tambah_kategori()`, `submit_update_kategori()`, `submit_hapus_kategori()`, `get_all_kategori()` |
| `ProdukController` | `src/controllers/ProdukController.py` | `get_daftar_produk(role)`, `get_produk_detail(role, id)`, `cari_produk(role, query)`, `submit_tambah_produk(role, ...)`, `submit_update_produk(role, ...)`, `submit_nonaktifkan_produk(role, id)` |

### 3.5 Views (PyQt6 Widgets)

| Class | File | Key Details |
|-------|------|-------------|
| `GradientBackground` | `src/views/loginpage.py`, `dashboardview.py`, `produklistview.py` | Radial/linear gradient painted background |
| `RoundedInputField` | `src/views/loginpage.py` | Custom styled input with icon and password toggle |
| `LoginWindow` | `src/views/loginpage.py` | Full login UI with drag-to-move, Enter key support, error display, `clear_fields()` |
| `Card`, `StatCard` | `src/views/dashboardview.py` | Styled stat cards |
| `BarChart` | `src/views/dashboardview.py` | Custom QPainter bar chart (target vs actual per month) |
| `LineChart` | `src/views/dashboardview.py` | Custom QPainter line chart (defect trend per month) |
| `Sidebar` | `src/views/dashboardview.py`, `produklistview.py` | Navigation sidebar with 7 menu items + logout |
| `Topbar` | `src/views/dashboardview.py`, `produklistview.py` | Title bar with user info, drag-to-move |
| `DashboardWindow` | `src/views/dashboardview.py` | Main dashboard page, `QStackedWidget` for navigation |
| `ProductCard`, `ProductGrid`, `SearchBar`, `Toolbar`, `FilterBar` | `src/views/produklistview.py` | Product listing UI components |
| `ProdukWindow` | `src/views/produklistview.py` | Product listing page (embedded or standalone) |
| `EditKategoriDialog` | `src/views/KategoriView.py` | Category edit dialog with combo box, new name input, save/delete |
| `MainWindow` | `src/views/main_window.py` | Simple DB connection check window (**unused** in app flow) |

---

## 4. File Structure

### 4.1 Existing Files

```
IF2050-2026-K01-G08-SimonPro/
├── main.py                              # App entry point
├── pyproject.toml                        # Project metadata & dependencies
├── requirements.txt                      # Pinned dependencies (autogenerated by uv)
├── docker-compose.yml                    # PostgreSQL 15 on port 5433
├── database/
│   ├── init.sql                          # Schema: 8 tables + 2 enums
│   └── dummy.sql                         # Seed data: users, categories, products, targets, production, defects
├── img/
│   ├── Logo Simonpro Biru.png
│   └── Logo Simonpro Putih.png
├── font/
│   └── Inter_18pt/24pt/28pt-*.ttf        # Full Inter typeface family
├── src/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py                   # Exports: Database, get_db, test_connection
│   │   └── db_connection.py              # Database singleton
│   ├── models/
│   │   ├── __init__.py
│   │   ├── User.py
│   │   ├── Session.py
│   │   ├── KategoriProduk.py
│   │   └── Produk.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── AuthService.py
│   │   ├── UserDataLocal.py
│   │   ├── DashboardService.py
│   │   ├── KategoriService.py
│   │   └── ProdukService.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── LoginController.py
│   │   ├── KategoriController.py
│   │   └── ProdukController.py
│   ├── views/
│   │   ├── __init__.py                   # Exports: MainWindow (unused)
│   │   ├── loginpage.py                 # LoginWindow, RoundedInputField
│   │   ├── dashboardview.py              # DashboardWindow, BarChart, LineChart, Sidebar, Topbar
│   │   ├── produklistview.py             # ProdukWindow, ProductCard, ProductGrid, etc.
│   │   ├── KategoriView.py              # EditKategoriDialog
│   │   └── main_window.py               # MainWindow (DB health check — unused)
│   └── utils/
│       └── __init__.py                   # Empty — utility package placeholder
├── tests/
│   ├── __init__.py
│   ├── test_db_connection.py             # 8 integration tests
│   ├── test_dummy.py                     # 2 basic tests
│   └── test_produk.py                    # 29 ProdukService/Controller tests
└── localdocs/
    ├── K01_G08_Draft_CD (1).pdf
    ├── K01_G08_Final_DPPL2.pdf
    └── [STI] Implementasi.pdf
```

### 4.2 Files That Need To Be Created

```
src/
├── models/
│   ├── TargetProduksi.py                 # Model for target_produksi table
│   ├── ProduksiHarian.py                 # Model for produksi_harian table
│   ├── TipeDefect.py                     # Model for tipe_defect table
│   └── DetailDefect.py                   # Model for detail_defect table
├── services/
│   ├── TargetProduksiService.py          # Business logic for UC05
│   ├── ProduksiHarianService.py          # Business logic for UC06
│   ├── DefectService.py                  # Business logic for UC07
│   ├── PencapaianService.py             # Business logic for UC08
│   └── LaporanService.py                 # Business logic for UC09
├── controllers/
│   ├── TargetProduksiController.py       # Controller for UC05
│   ├── ProduksiHarianController.py       # Controller for UC06
│   ├── DefectController.py              # Controller for UC07
│   ├── PencapaianController.py          # Controller for UC08
│   └── LaporanController.py             # Controller for UC09
├── views/
│   ├── targetproduksiview.py            # View for Target Produksi (UC05)
│   ├── produksiharianview.py           # View for Input Produksi (UC06)
│   ├── defectview.py                    # View for Defect management (UC07)
│   ├── pencapaianview.py                # View for Pencapaian (UC08)
│   ├── laporanview.py                   # View for Laporan (UC09)
│   ├── dialog_tambah_produk.py          # Dialog form for adding/editing products
│   └── dialog_tambah_target.py           # Dialog form for adding/editing targets
└── tests/
    ├── test_kategori.py                 # Tests for KategoriService/Controller
    ├── test_target_produksi.py           # Tests for TargetProduksi
    ├── test_produksi_harian.py           # Tests for ProduksiHarian
    ├── test_defect.py                    # Tests for Defect
    ├── test_pencapaian.py                # Tests for Pencapaian
    └── test_laporan.py                   # Tests for Laporan
```

---

## 5. Database Schema (Existing)

All tables are already created in `database/init.sql`:

| Table | Columns | Relationships |
|-------|---------|-------------|
| `users` | `user_id` (PK), `username` (UNIQUE), `password`, `role` (ENUM: owner, admin) | — |
| `sessions` | `session_id` (PK), `user_id` (FK→users), `login_time`, `is_active` | — |
| `kategori_produk` | `kategori_id` (PK), `nama_kategori` (UNIQUE) | Referenced by `produk.nama_kategori` |
| `produk` | `produk_id` (PK), `nama_produk`, `deskripsi_produk`, `satuan`, `gambar`, `status_aktif`, `nama_kategori` (FK→kategori_produk) | Referenced by `target_produksi`, `produksi_harian` |
| `target_produksi` | `target_id` (PK), `produk_id` (FK→produk), `periode` (ENUM: harian/mingguan/bulanan/tahunan), `tanggal_mulai`, `tanggal_selesai`, `jumlah_target` (≥0) | — |
| `produksi_harian` | `produksi_id` (PK), `tanggal`, `produk_id` (FK→produk), `jumlah_aktual` (≥0), `jumlah_defect` (≥0, ≤jumlah_aktual), `penanggung_jawab`, `kendala_produksi` | Referenced by `detail_defect` |
| `tipe_defect` | `defect_id` (PK), `nama_defect` (UNIQUE) | Referenced by `detail_defect` |
| `detail_defect` | `detail_id` (PK), `produksi_id` (FK→produksi_harian ON DELETE CASCADE), `defect_id` (FK→tipe_defect), `jumlah_defect` (≥0) | — |

---

## 6. Implementation Plan

### Phase 1: Fix Existing Gaps

| Priority | Task | Details |
|----------|------|---------|
| P0 | Wire ProdukWindow to DB | Replace hardcoded `PRODUCTS` list with data from `ProdukService.get_daftar_produk()`. Connect search, filter, and sort. |
| P0 | Add "Tambah/Edit Produk" dialog | Create `dialog_tambah_produk.py` with form fields (nama, deskripsi, satuan, gambar, kategori dropdown, status). Wire to `ProdukController`. |
| P1 | Fix Produk "Edit" button on cards | Currently a no-op; should open edit dialog with product data pre-filled. |
| P1 | Connect `FilterBar` buttons | Sort and group-by buttons in `ProdukWindow` are currently non-functional. |
| P2 | Remove or repurpose `MainWindow` | `main_window.py` is a simple DB health-check not used in the app flow. Either remove it or integrate. |

### Phase 2: Target Produksi (UC05)

| Step | Deliverable |
|------|-------------|
| 1 | Create `src/models/TargetProduksi.py` — dataclass with `from_row()`, `getAll(db)`, `getById(db, id)`, `getByProduk(db, produk_id)`, `getByPeriode(db, periode)`, `tambah(db, ...)`, `simpanPerubahan(db, ...)`, `hapus(db, id)` |
| 2 | Create `src/services/TargetProduksiService.py` — validation (tanggal_mulai < tanggal_selesai, jumlah_target ≥ 0, produk must exist), CRUD delegation |
| 3 | Create `src/controllers/TargetProduksiController.py` — role-gating (admin = CRUD, owner = read), callbacks |
| 4 | Create `src/views/targetproduksiview.py` — `TargetProduksiWindow` with table/grid showing targets per product per period, add/edit dialog, delete confirmation |
| 5 | Wire `TargetProduksiWindow` into `DashboardWindow.navigate_to()` — add to `QStackedWidget` |

### Phase 3: Input Produksi Harian (UC06)

| Step | Deliverable |
|------|-------------|
| 1 | Create `src/models/ProduksiHarian.py` — dataclass with `from_row()`, CRUD static methods, date range queries |
| 2 | Create `src/services/ProduksiHarianService.py` — validation (jumlah_defect ≤ jumlah_aktual, tanggal not future, produk must be active), CRUD |
| 3 | Create `src/controllers/ProduksiHarianController.py` — role-gating (admin only for input), callbacks |
| 4 | Create `src/views/produksiharianview.py` — form with product dropdown, date picker, actual/defect quantities, responsible person, constraints text area |
| 5 | Wire into dashboard navigation |

### Phase 4: Defect Management (UC07)

| Step | Deliverable |
|------|-------------|
| 1 | Create `src/models/TipeDefect.py` — CRUD for defect types |
| 2 | Create `src/models/DetailDefect.py` — CRUD for defect detail records per production entry |
| 3 | Create `src/services/DefectService.py` — manage defect types and detail records, link to `produksi_harian` |
| 4 | Create `src/controllers/DefectController.py` — role-gating (admin = CRUD, owner = read) |
| 5 | Create `src/views/defectview.py` — defect type management, defect recording per production day |
| 6 | Wire into dashboard navigation |

### Phase 5: Pencapaian / Achievement (UC08)

| Step | Deliverable |
|------|-------------|
| 1 | Create `src/services/PencapaianService.py` — query targets vs actuals per product/period, calculate achievement percentages |
| 2 | Create `src/controllers/PencapaianController.py` — role-gating (both can view) |
| 3 | Create `src/views/pencapaianview.py` — achievement table with color-coded status, filter by period/product |
| 4 | Wire into dashboard navigation |

### Phase 6: Laporan / Report Generation (UC09)

| Step | Deliverable |
|------|-------------|
| 1 | Create `src/services/LaporanService.py` — gather production data, target data, defect data for report generation |
| 2 | Create `src/controllers/LaporanController.py` — report generation and export |
| 3 | Create `src/views/laporanview.py` — report type selection, date range picker, preview, PDF export using `reportlab` or `fpdf2` |
| 4 | Wire into dashboard navigation |

### Phase 7: Polish & Hardening

| Priority | Task |
|----------|------|
| P1 | Hash passwords (replace plaintext comparison in `AuthService._verify_password` with `bcrypt` or `hashlib`) |
| P1 | Add comprehensive tests for each new module (following the pattern in `test_produk.py`) |
| P2 | Refactor duplicated `Sidebar`/`Topbar`/`GradientBackground` classes into shared utilities under `src/views/common/` |
| P2 | Add input validation/sanitization on all forms |
| P2 | Handle DB connection errors gracefully in views (show user-friendly error dialogs) |
| P3 | Add user management (add/edit/deactivate users) — currently only 2 hardcoded users |
| P3 | Internationalization / localization support |

---

## 7. Key Observations

1. **Architecture**: MVC pattern is consistently applied. Models are thin (data + static SQL methods), Services handle validation + business logic, Controllers handle role-gating, Views are PyQt6 widgets.

2. **Database is complete**: All 8 tables with constraints, enums, and seed data are implemented. No schema changes needed.

3. **Role-based access**: `owner` = read-only, `admin` = full CRUD. This pattern is established in `ProdukController` and `KategoriController` and should be followed for all new modules.

4. **Sidebar defines navigation**: Both `dashboardview.py` and `produklistview.py` have a `Sidebar` with 7 menu items. Currently only Dashboard and Produk are wired up. New views need to be added to the `QStackedWidget` in `DashboardWindow`.

5. **ProdukWindow is partially static**: The product grid uses hardcoded `PRODUCTS` data instead of pulling from the database. This needs to be wired to `ProdukService`.

6. **No product add/edit form**: The "Tambah Produk" and "Edit" buttons on product cards don't open any dialog yet.

7. **Password security**: Credentials are compared in plaintext. This should be addressed before production.

8. **Unused `MainWindow`**: `src/views/main_window.py` is a standalone DB connection checker that's not part of the app flow.

9. **Empty `src/utils/`**: Placeholder directory exists but has no utility modules yet.

10. **Dependencies already include report libs**: Both `reportlab` and `fpdf2` are in `pyproject.toml`, ready for the Laporan module.