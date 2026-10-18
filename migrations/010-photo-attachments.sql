PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
CREATE TABLE device_photos (
 photo_id TEXT PRIMARY KEY NOT NULL,
 device_id TEXT NOT NULL REFERENCES devices(device_id),
 relative_path TEXT NOT NULL UNIQUE CHECK(relative_path LIKE 'photos/%'),
 thumbnail_path TEXT NOT NULL UNIQUE CHECK(thumbnail_path LIKE 'photos/%'),
 caption TEXT,
 source TEXT NOT NULL CHECK(length(trim(source))>0),
 original_name TEXT NOT NULL,
 sha256 TEXT NOT NULL CHECK(length(sha256)=64),
 thumbnail_sha256 TEXT NOT NULL CHECK(length(thumbnail_sha256)=64),
 recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
CREATE INDEX photos_device ON device_photos(device_id);
PRAGMA user_version=10;
COMMIT;
