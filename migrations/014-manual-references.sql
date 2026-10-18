PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
CREATE TABLE device_manuals (
 reference_id TEXT PRIMARY KEY NOT NULL,
 device_id TEXT NOT NULL REFERENCES devices(device_id),
 title TEXT NOT NULL CHECK(length(trim(title))>0),
 kind TEXT NOT NULL CHECK(kind IN ('online','local')),
 url TEXT,
 relative_path TEXT UNIQUE,
 original_name TEXT,
 sha256 TEXT,
 language TEXT CHECK(language IS NULL OR length(trim(language))>0),
 edition TEXT CHECK(edition IS NULL OR length(trim(edition))>0),
 applicable_model TEXT CHECK(applicable_model IS NULL OR length(trim(applicable_model))>0),
 source TEXT NOT NULL CHECK(length(trim(source))>0),
 notes TEXT,
 recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
 CHECK((kind='online' AND url IS NOT NULL AND (url LIKE 'https://%' OR url LIKE 'http://%') AND relative_path IS NULL AND original_name IS NULL AND sha256 IS NULL)
 OR (kind='local' AND url IS NULL AND relative_path IS NOT NULL AND relative_path LIKE 'manuals/%' AND original_name IS NOT NULL AND sha256 IS NOT NULL AND length(sha256)=64))
);
CREATE INDEX manuals_device ON device_manuals(device_id);
PRAGMA user_version=14;
COMMIT;
