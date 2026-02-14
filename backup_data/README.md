# Backup Data Folder

Folder ini berisi data JSON yang di-export dari MongoDB untuk proses migrasi ke MySQL.

## Cara Mengisi Folder Ini

Export semua collection dari MongoDB menggunakan `mongoexport`:

```bash
# Export users
mongoexport --db=test --collection=users --out=backup_data/test.users.json --jsonArray

# Export frames
mongoexport --db=test --collection=frames --out=backup_data/test.frames.json --jsonArray

# Export photos
mongoexport --db=test --collection=photos --out=backup_data/test.photos.json --jsonArray

# Export follows
mongoexport --db=test --collection=follows --out=backup_data/test.follows.json --jsonArray

# Export tickets
mongoexport --db=test --collection=tickets --out=backup_data/test.tickets.json --jsonArray

# Export reports
mongoexport --db=test --collection=reports --out=backup_data/test.reports.json --jsonArray

# Export photocollabs
mongoexport --db=test --collection=photocollabs --out=backup_data/test.photocollabs.json --jsonArray

# Export aiphotoboothusages
mongoexport --db=test --collection=aiphotoboothusages --out=backup_data/test.aiphotoboothusages.json --jsonArray

# Export broadcasts
mongoexport --db=test --collection=broadcasts --out=backup_data/test.broadcasts.json --jsonArray

# Export notifications
mongoexport --db=test --collection=notifications --out=backup_data/test.notifications.json --jsonArray

# Export maintenances
mongoexport --db=test --collection=maintenances --out=backup_data/test.maintenances.json --jsonArray
```

## File yang Dibutuhkan

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

## Catatan Penting

⚠️ **File JSON di folder ini TIDAK akan di-commit ke git** karena sudah ada di `.gitignore`.

File-file ini berisi data sensitif dari database production/testing dan hanya untuk keperluan lokal migration.
