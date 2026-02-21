# MongoDB to MySQL Migration Tool

Tool untuk migrasi data dari MongoDB (BSON format) ke MySQL untuk project Snaplove.

## Fitur

✅ Mendukung file BSON dan JSON  
✅ Auto-convert MongoDB ObjectId dan Date  
✅ Foreign key validation  
✅ Boolean type conversion  
✅ Nested data extraction (images, tags, likes, comments, dll)  
✅ Transaction support untuk data integrity  
✅ Detailed logging dan error reporting  

## Struktur Folder

```
snaplove_migration/
├── backup_data/        # Data BSON dari MongoDB (IGNORED by git)
│   ├── users.bson
│   ├── frames.bson
│   ├── photos.bson
│   └── ...
├── config.example.py   # Template konfigurasi (copy ke config.py)
├── config.py           # Konfigurasi database dan path (IGNORED by git)
├── converter.py        # Script utama untuk konversi
├── schema.sql          # Schema MySQL database
├── requirements.txt    # Dependencies Python
├── test_connection.py  # Script test koneksi
├── verify_migration.py # Script verify hasil migrasi
├── run_migration.bat   # Script otomatis (Windows)
├── run_migration.sh    # Script otomatis (Linux/Mac)
├── .gitignore          # Git ignore file
└── README.md           # Dokumentasi ini
```

## Prerequisites

1. **Python 3.7+** terinstall
2. **MySQL Server 5.7+** sudah berjalan
3. **Data BSON** dari MongoDB sudah di-export ke folder `backup_data/`

## Instalasi

### 1. Install Python Dependencies

```bash
cd snaplove_migration
pip install -r requirements.txt
```

Packages yang akan diinstall:
- PyMySQL (koneksi MySQL)
- cryptography (untuk MySQL authentication)
- pymongo (untuk decode BSON)
- bson (untuk parsing BSON files)

### 2. Konfigurasi Database

Copy file template dan edit dengan setting MySQL Anda:

**Windows:**
```cmd
copy config.example.py config.py
notepad config.py
```

**Linux/Mac:**
```bash
cp config.example.py config.py
nano config.py
```

Sesuaikan konfigurasi MySQL di `config.py`:

```python
MYSQL_CONFIG = {
    'host': 'localhost',      # Host MySQL server
    'port': 3306,             # Port MySQL
    'user': 'root',           # Username MySQL
    'password': 'your_password_here',  # ⚠️ GANTI dengan password MySQL Anda!
    'database': 'snaplove_db',  # Nama database target
}
```

**⚠️ PENTING:** 
- File `config.py` sudah ada di `.gitignore` sehingga credentials Anda tidak akan ter-commit ke git
- Pastikan MySQL user memiliki privilege: CREATE, INSERT, ALTER, DROP

## Cara Menggunakan

### Langkah 1: Export Data dari MongoDB

Export semua collection dari MongoDB ke format BSON menggunakan `mongodump`:

```bash
# Buat folder backup_data
mkdir backup_data

# Dump semua collection ke BSON
mongodump --db=your_database_name --out=./backup_data

# Atau untuk collection tertentu:
mongodump --db=your_database_name --collection=users --out=./backup_data
```

Pastikan file-file BSON berikut ada di folder `backup_data/`:
- `users.bson`
- `maintenances.bson`
- `follows.bson`
- `frames.bson`
- `tickets.bson`
- `reports.bson`
- `photos.bson`
- `photocollabs.bson`
- `photoposts.bson`
- `aiphotoboothusages.bson`
- `broadcasts.bson`
- `notifications.bson`

### Langkah 2: Test Koneksi MySQL

Sebelum migrasi, test koneksi database dan verifikasi file data:

```bash
python test_connection.py
```

Output yang diharapkan:
```
============================================================
Migration Setup Test
============================================================

1. Testing Python dependencies...

2. Testing MySQL connection...
✓ PyMySQL module found
✓ MySQL connection successful
  Host: localhost:3306
  User: root
  MySQL Version: 8.0.39

3. Checking data files...
✓ Data directory found: /path/to/backup_data
  ✓ users.bson (56,575 bytes)
  ✓ maintenances.bson (152 bytes)
  ... (semua file BSON)

Summary: 12 files found, 0 missing

============================================================
✓ All checks passed! Ready to run migration.
============================================================
```

### Langkah 3: Jalankan Migration

**Metode 1: Manual dengan Python**
```bash
python converter.py
```

**Metode 2: Otomatis (Windows)**
```cmd
run_migration.bat
```

**Metode 3: Otomatis (Linux/Mac)**
```bash
chmod +x run_migration.sh
./run_migration.sh
```

### Langkah 4: Verify Hasil Migration

Setelah migration selesai, verify data yang sudah dimigrasikan:

```bash
python verify_migration.py
```

Output yang diharapkan:
```
============================================================
MIGRATION VERIFICATION
============================================================

✓ users                         :     90 rows
✓ maintenances                  :      1 rows
✓ follows                       :     11 rows
✓ frames                        :     34 rows
✓ frame_images                  :     34 rows
✓ frame_tags                    :    106 rows
✓ frame_likes                   :     53 rows
...

Sample Users:
  - username1              (email@example.com)            [basic]
  - username2              (email2@example.com)           [verified_premium]

Sample Frames:
  - Frame Title 1                          [public] Official: True
  - Frame Title 2                          [private] Official: False

============================================================
✓ Verification completed!
============================================================
```

## Expected Migration Output

Script akan menampilkan progress untuk setiap tahap:

```
============================================================
MongoDB to MySQL Migration Tool
============================================================

✓ Connected to MySQL database: snaplove_db

[Step 1] Creating database schema...
✓ Database schema created successfully (50 statements)

[Step 2] Migrating data...

--- Migrating users ---
✓ Loaded 90 records from users.bson
✓ Users: 90 successful, 0 failed

--- Migrating maintenances ---
✓ Loaded 1 records from maintenances.bson
✓ Maintenances: 1 successful, 0 failed

--- Migrating follows ---
✓ Loaded 11 records from follows.bson
✓ Follows: 11 successful, 0 failed

--- Migrating frames ---
✓ Loaded 34 records from frames.bson
✓ Frames: 34 successful, 0 failed

... (continues for all collections)

============================================================
✓ Migration completed successfully!
============================================================
```

## Struktur Database

### Tabel Utama:
- `users` - Data pengguna (profile, email, password, role)
- `maintenances` - Settings maintenance mode
- `follows` - Relasi follow antar user
- `frames` - Frame template untuk photo booth
- `tickets` - Tiket support dari user
- `reports` - Report frame yang bermasalah
- `photos` - Foto yang di-upload user
- `photoposts` - Post foto ke timeline/feed
- `photo_collabs` - Kolaborasi foto antar user
- `aiphotobooth_usages` - Usage tracking AI photobooth per user
- `broadcasts` - Broadcast message dari admin
- `notifications` - Notifikasi untuk user

### Tabel Relasi (untuk array di MongoDB):
- `frame_images` - Array images di frame (multiple layouts)
- `frame_tags` - Array tags/labels di frame
- `frame_likes` - Array likes di frame (track siapa yang like)
- `frame_uses` - Array uses di frame (track siapa yang pakai)
- `photo_images` - Array images di photo (multiple shots)
- `photo_videos` - Array video files di live photo
- `photopost_images` - Array images di photo post
- `photopost_likes` - Array likes di photo post
- `photopost_comments` - Comments di photo post
- `photo_collab_images` - Array merged images di photo collab
- `photo_collab_stickers` - Array stickers/doodles di photo collab
- `ticket_images` - Array screenshot/images di ticket
- `broadcast_target_roles` - Array target roles untuk broadcast

## Data Conversion Details

### MongoDB → MySQL Type Mapping:
- **ObjectId** → `VARCHAR(24)` (string representation)
- **Date/ISODate** → `DATETIME` (MySQL datetime format)
- **Boolean** → `BOOLEAN` / `TINYINT(1)` (0 or 1)
- **Array** → Separate table dengan foreign key
- **Nested Object** → Flattened ke columns (e.g., `inviter.user_id` → `inviter_user_id`)
- **Null** → `NULL` (preserved)

### Special Handling:
- ✅ Foreign key validation (skip jika parent tidak ada)
- ✅ Optional foreign keys (set NULL jika user tidak ada)
- ✅ Boolean string conversion ('true'/'false' → 1/0)
- ✅ Transaction rollback on error
- ✅ Detailed error logging

## Troubleshooting

### Error: "Access denied for user"
- Pastikan username dan password MySQL di `config.py` sudah benar
- Pastikan user MySQL memiliki privileges: CREATE, INSERT, DROP, ALTER
- Test dengan: `mysql -u root -p` untuk verify credentials

### Error: "Cannot add foreign key constraint"
- Script sudah menghandle urutan migrasi dengan benar
- Pastikan database kosong sebelum menjalankan migration
- Jika masih error, drop database dan buat ulang

### Error: "File not found"
- Pastikan semua file BSON ada di folder `backup_data/`
- Periksa nama file di `config.py` bagian `DATA_FILES`
- Pastikan path `DATA_DIR` di config benar
- File harus .bson bukan .json

### Error: "Failed to load BSON"
- Pastikan file BSON valid (hasil dari `mongodump`)
- Coba export ulang dari MongoDB
- Periksa file size (file 0 bytes = kosong, skip saja)

### Data tidak lengkap / Record skipped
- Periksa log untuk detail error
- Set `VERBOSE = True` di `config.py` untuk log lebih detail
- Common issues:
  - Foreign key tidak ditemukan (parent record tidak ada)
  - Invalid data type (e.g., string di field integer)
  - NULL di field yang required

### Migration lambat
- Adjust `BATCH_SIZE` di config.py (coba 500 atau 2000)
- Disable VERBOSE untuk mengurangi I/O
- Pastikan MySQL tidak running di slow query mode
- Check MySQL server resources (CPU, memory)

## Catatan Penting

1. **⚠️ Backup dulu!** - Pastikan backup data MongoDB sebelum migrasi
2. **⚠️ Database baru** - Script akan DROP semua tabel yang ada, gunakan database kosong/baru
3. **🔒 Keamanan** - File `config.py` sudah di-ignore oleh git untuk melindungi password
4. **📋 Template Config** - Gunakan `config.example.py` sebagai template, jangan commit `config.py`
5. **🔗 Foreign Keys** - Migration mengikuti urutan yang benar untuk menghindari error foreign key
6. **🔄 Idempotent** - Anda bisa jalankan ulang migration (akan drop & recreate tables)
7. **📊 Validation** - Gunakan `verify_migration.py` untuk check hasil migration

## Modifikasi & Customization

### Menambah Collection Baru:

**1. Tambahkan mapping di `config.py`:**
```python
DATA_FILES = {
    'users': 'users.bson',
    'frames': 'frames.bson',
    # ... existing collections ...
    'new_collection': 'newcollection.bson',  # ← Add your new collection
}
```

**2. Tambahkan di urutan migrasi:**
```python
MIGRATION_ORDER = [
    'users',  # Must be first
    # ... existing collections ...
    'new_collection',  # ← Add in proper order (consider foreign keys)
]
```

**3. Tambahkan schema di `schema.sql`:**
```sql
CREATE TABLE `new_collection` (
  `id` VARCHAR(24) PRIMARY KEY,
  `field1` VARCHAR(255),
  `field2` TEXT,
  `user_id` VARCHAR(24),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**4. Buat method migrasi di `converter.py`:**
```python
def migrate_new_collection(self, data: List[Dict]) -> bool:
    """Migrate new collection"""
    if not data:
        return True
    
    cursor = self.connection.cursor()
    successful = 0
    failed = 0
    
    try:
        for record in data:
            try:
                collection_data = {
                    'id': self.convert_mongo_id(record.get('_id')),
                    'field1': record.get('field1'),
                    'field2': record.get('field2'),
                    'user_id': self.convert_mongo_id(record.get('user_id')),
                    'created_at': self.convert_date(record.get('created_at')),
                }
                
                placeholders = ', '.join(['%s'] * len(collection_data))
                columns = ', '.join(f'`{k}`' for k in collection_data.keys())
                sql = f"INSERT INTO new_collection ({columns}) VALUES ({placeholders})"
                
                cursor.execute(sql, list(collection_data.values()))
                successful += 1
                
            except Exception as e:
                failed += 1
                if VERBOSE:
                    print(f"  ✗ Failed to insert record: {e}")
        
        self.connection.commit()
        print(f"✓ New Collection: {successful} successful, {failed} failed")
        return True
        
    except Exception as e:
        print(f"✗ New Collection migration failed: {e}")
        self.connection.rollback()
        return False
```

**5. Registrasi method di `run_migration()`:**
```python
migration_methods = {
    'users': self.migrate_users,
    # ... existing methods ...
    'new_collection': self.migrate_new_collection,  # ← Add here
}
```

### Mengubah Database Target:

Edit di `config.py`:
```python
MYSQL_CONFIG = {
    'host': 'production-server.com',  # Change host
    'port': 3306,
    'user': 'prod_user',              # Change user
    'password': 'secure_password',    # Change password
    'database': 'production_db',      # Change database
}
```

### Custom Data Transformation:

Jika perlu transformasi khusus, edit method di `converter.py`:
```python
# Example: Custom field transformation
def migrate_users(self, data: List[Dict]) -> bool:
    for record in data:
        # Custom logic: uppercase username
        if record.get('username'):
            record['username'] = record['username'].upper()
        
        # Custom logic: hash password differently
        if record.get('password'):
            record['password'] = custom_hash(record['password'])
        
        # ... rest of migration logic
```

## Git & Security

### File yang Di-ignore (.gitignore)

```
# Configuration with credentials
config.py

# Data files (sensitive)
backup_data/
*.bson
*.json

# Python
__pycache__/
*.py[cod]
*.pyc
*.pyo
*.pyd
.Python
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp

# Logs
*.log
```

**⚠️ PENTING:** 
- Jangan commit file `config.py` (berisi password database)
- Jangan commit folder `backup_data/` (berisi data sensitif)
- Gunakan `config.example.py` sebagai template untuk setup baru

## FAQ

**Q: Apakah data MongoDB original akan terhapus?**  
A: Tidak, migration hanya membaca data dari file BSON. Data di MongoDB tetap aman.

**Q: Bisa dijalankan berkali-kali?**  
A: Ya, script akan drop dan recreate tables setiap kali dijalankan.

**Q: Bagaimana cara rollback jika ada error?**  
A: MySQL transactions akan auto-rollback jika ada error. Untuk manual rollback, drop database dan jalankan ulang.

**Q: Support JSON file juga?**  
A: Ya, script support BSON dan JSON. Deteksi otomatis berdasarkan extension file.

**Q: Berapa lama migration akan berjalan?**  
A: Tergantung jumlah data. Contoh: ~200 records dalam ~2-5 detik. Database besar (100K+ records) bisa 5-30 menit.

**Q: Apakah perlu stop aplikasi saat migration?**  
A: Untuk production, disarankan stop aplikasi atau gunakan database terpisah untuk migration testing dulu.

## Lisensi

Internal tool untuk project Snaplove.

## Kontributor

- Developer: [Your Name]
- Project: Snaplove Photo Booth App
- Date: February 2026

---

**Need help?** Contact development team atau buka issue di repository.
```

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

