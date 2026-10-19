PRAGMA foreign_keys=ON;
BEGIN;
ALTER TABLE devices ADD COLUMN manufacturer TEXT CHECK(manufacturer IS NULL OR length(manufacturer) BETWEEN 1 AND 200);
ALTER TABLE devices ADD COLUMN model TEXT CHECK(model IS NULL OR length(model) BETWEEN 1 AND 200);
ALTER TABLE devices ADD COLUMN serial_number TEXT CHECK(serial_number IS NULL OR length(serial_number) BETWEEN 1 AND 200);
PRAGMA user_version=24;
COMMIT;
