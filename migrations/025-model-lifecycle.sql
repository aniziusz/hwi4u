PRAGMA foreign_keys=ON;
BEGIN;
CREATE TABLE device_lifecycle (
 device_id TEXT PRIMARY KEY REFERENCES devices(device_id) ON DELETE CASCADE,
 records_json TEXT NOT NULL
);
CREATE TABLE device_lifecycle_history (
 history_id INTEGER PRIMARY KEY, device_id TEXT NOT NULL,
 records_json TEXT NOT NULL, recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE model_profiles (
 profile_id TEXT PRIMARY KEY,
 manufacturer TEXT NOT NULL, model TEXT NOT NULL, variant TEXT NOT NULL,
 device_type TEXT REFERENCES device_types(type_name) ON UPDATE CASCADE,
 roles_json TEXT NOT NULL, lifecycle_json TEXT NOT NULL,
 sources_json TEXT NOT NULL, note TEXT NOT NULL,
 supersedes TEXT UNIQUE REFERENCES model_profiles(profile_id),
 recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
PRAGMA user_version=25;
COMMIT;
