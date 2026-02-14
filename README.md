# MongoDB to MySQL Migration Tool

Tool untuk migrasi data dari MongoDB ke MySQL untuk project Snaplove.

## Struktur Folder

```
migration/
├── backup_data/        # Data JSON dari MongoDB (IGNORED by git)
│   ├── test.users.json
│   ├── test.frames.json
│   └── ...
├── config.example.py   # Template konfigurasi (copy ke config.py)
├── config.py           # Konfigurasi database dan path (IGNORED by git)
├── converter.py        # Script utama untuk konversi
├── schema.sql          # Schema MySQL database
├── requirements.txt    # Dependencies Python
├── test_connection.py  # Script test koneksi
├── run_migration.bat   # Script otomatis (Windows)
├── run_migration.sh    # Script otomatis (Linux/Mac)
├── .gitignore          # Git ignore file
└── README.md           # Dokumentasi ini
```

## Prerequisites

1. **Python 3.7+** terinstall
2. **MySQL Server** sudah berjalan
3. **Data JSON** dari MongoDB sudah di-export ke folder `migration/backup_data/`

## Instalasi

### 1. Install Python Dependencies

```bash
cd migration
pip install -r requirements.txt
```

### 2. Konfigurasi Database

Copy file template dan edit dengan setting MySQL Anda:

```bash
# Copy template ke config.py
cp config.example.py config.py

# Edit config.py (Windows)
notepad config.py

# Edit config.py (Linux/Mac)
nano config.py
```

Sesuaikan konfigurasi MySQL:

```python
MYSQL_CONFIG = {
    'host': 'localhost',      # Host MySQL server
    'port': 3306,             # Port MySQL
    'user': 'root',           # Username MySQL
    'password': 'your_mysql_password',  # Password MySQL (GANTI INI!)
    'database': 'snaplove_db',  # Nama database (akan dibuat)
}
```

**⚠️ PENTING:** File `config.py` sudah ada di `.gitignore` sehingga password Anda tidak akan ter-commit ke git.

## Cara Menggunakan

### Langkah 1: Export Data dari MongoDB

Export semua collection dari MongoDB ke format JSON:

```bash
# Buat folder backup_data di dalam migration
cd migration
mkdir backup_data

# Export semua collection ke folder backup_data
mongoexport --db=test --collection=users --out=backup_data/test.users.json --jsonArray
mongoexport --db=test --collection=frames --out=backup_data/test.frames.json --jsonArray
mongoexport --db=test --collection=photos --out=backup_data/test.photos.json --jsonArray
# ... dan seterusnya untuk collection lainnya
```

Atau jika sudah ada, pastikan file-file berikut ada di folder `migration/backup_data/`:
- `test.users.json`
- `test.maintenances.json`
- `test.follows.json`
- `test.frames.json`
- `test.tickets.json`
- `test.reports.json`
- `test.photos.json`
- `test.photocollabs.json`
- `test.aiphotoboothusages.json`
- `test.broadcasts.json`
- `test.notifications.json`

### Langkah 2: Buat Database MySQL

```sql
CREATE DATABASE snaplove_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Langkah 3: Jalankan Migration

```bash
cd migration
python converter.py
```

## Output

Script akan menampilkan progress untuk setiap tahap:

```
============================================================
MongoDB to MySQL Migration Tool
============================================================

✓ Connected to MySQL database: snaplove_db

[Step 1] Creating database schema...
✓ Database schema created successfully (XX statements)

[Step 2] Migrating data...

--- Migrating users ---
✓ Loaded XX records from test.users.json
✓ Users: XX successful, 0 failed

--- Migrating frames ---
✓ Loaded XX records from test.frames.json
✓ Frames: XX successful, 0 failed

...

============================================================
✓ Migration completed successfully!
============================================================
```

## Struktur Database

### Tabel Utama:
- `users` - Data pengguna
- `frames` - Frame template
- `photos` - Foto yang di-upload
- `follows` - Relasi follow antar user
- `tickets` - Tiket support
- `reports` - Report frame
- `photo_collabs` - Kolaborasi foto
- `notifications` - Notifikasi
- `broadcasts` - Broadcast message
- `maintenances` - Settings maintenance
- `aiphotobooth_usages` - Usage AI photobooth

### Tabel Relasi (untuk array di MongoDB):
- `frame_images` - Array images di frame
- `frame_tags` - Array tags di frame
- `frame_likes` - Array likes di frame
- `frame_uses` - Array uses di frame
- `photo_images` - Array images di photo
- `photo_videos` - Array videos di photo
- `photo_collab_images` - Array merged images di photo collab
- `photo_collab_stickers` - Array stickers di photo collab
- `ticket_images` - Array images di ticket
- `broadcast_target_roles` - Array target roles di broadcast

## Troubleshooting

### Error: "Access denied for user"
- Pastikan username dan password MySQL di `config.py` sudah benar
- Pastikan user MySQL memiliki hak akses CREATE, INSERT, DROP

### Error: "Cannot add foreign key constraint"
- Script sudah menghandle urutan migrasi untuk foreign keys
- Pastikan database kosong sebelum menjalankan migration

### Error: "File not found"
- Pastikan semua file JSON ada di folder `migration/backup_data/`
- Periksa nama file di `config.py` bagian `DATA_FILES`
- Pastikan folder `backup_data` sudah dibuat di dalam folder `migration`

### Data tidak lengkap
- Periksa file JSON apakah formatnya benar (JSON Array)
- Lihat log error untuk mengetahui record mana yang gagal
- Set `VERBOSE = True` di `config.py` untuk log lebih detail

## Catatan Penting

1. **Backup dulu!** - Pastikan backup data MongoDB sebelum migrasi
2. **Database baru** - Script akan DROP semua tabel yang ada, gunakan database baru
3. **Keamanan** - File `config.py` sudah di-ignore oleh git untuk melindungi password
4. **Template Config** - Gunakan `config.example.py` sebagai template, jangan commit `config.py`
5. **Foreign Keys** - Migration mengikuti urutan yang benar untuk menghindari error foreign key
6. **ObjectId** - MongoDB ObjectId dikonversi menjadi VARCHAR(24)
7. **Date Format** - Tanggal dari MongoDB dikonversi ke format MySQL DATETIME
8. **Array Fields** - Array di MongoDB dipecah menjadi tabel terpisah dengan relasi

## Modifikasi

### Menambah Collection Baru:

1. Tambahkan mapping di `config.py`:
```python
DATA_FILES = {
    ...
    'new_collection': 'test.new_collection.json',
}
```

2. Tambahkan di urutan migrasi:
```python
MIGRATION_ORDER = [
    ...
    'new_collection',
]
```

3. Buat method migrasi di `converter.py`:
```python
def migrate_new_collection(self, data: List[Dict]) -> bool:
    # Implement migration logic
    pass
```

## Git & Security

### File yang Di-ignore

File `.gitignore` sudah dikonfigurasi untuk mengabaikan:
- `config.py` - File konfigurasi dengan password database
- `backup_data/` - Folder berisi data JSON dari MongoDB (data sensitif)
- `__pycache__/` dan `*.pyc` - Python cache files
- `venv/` - Virtual environment folder
- Log files dan temporary files

### Best Practices

1. **JANGAN** commit file `config.py` dan folder `backup_data/` ke repository
2. **GUNAKAN** `config.example.py` sebagai template untuk tim
3. **SHARE** password database dan data backup melalui channel aman (bukan git)
4. Setiap developer buat `config.py` sendiri dan export data sendiri dari MongoDB

### Setup untuk Developer Baru

```bash
# Clone repository
git clone <repository-url>
cd migration

# Buat folder untuk data
mkdir backup_data

# Export data dari MongoDB (lihat Langkah 1)
# mongoexport --db=test --collection=users --out=backup_data/test.users.json --jsonArray
# ... export collection lainnya

# Copy template konfigurasi
cp config.example.py config.py

# Edit dengan kredensial Anda
nano config.py

# Install dependencies
pip install -r requirements.txt

# Test koneksi
python test_connection.py
```

## Support

Untuk pertanyaan atau issue, silakan buat issue di repository atau hubungi developer.

---

**Created:** 2026-02-15
**Version:** 1.0.0
**Author:** Snaplove Development Team - Slaviors Group

