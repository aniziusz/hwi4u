PRAGMA foreign_keys=ON;
BEGIN;
CREATE TABLE tag_choices(
 tag_id TEXT PRIMARY KEY NOT NULL,
 label TEXT NOT NULL CHECK(length(label) BETWEEN 1 AND 50 AND label=trim(label)),
 normalized_key TEXT NOT NULL UNIQUE CHECK(length(normalized_key)>0)
);
CREATE TABLE device_tags(
 device_id TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
 tag_id TEXT NOT NULL REFERENCES tag_choices(tag_id) ON DELETE RESTRICT,
 PRIMARY KEY(device_id,tag_id)
);
CREATE TABLE device_tag_history(
 history_id INTEGER PRIMARY KEY,
 device_id TEXT NOT NULL,
 before_json TEXT NOT NULL CHECK(json_valid(before_json)),
 after_json TEXT NOT NULL CHECK(json_valid(after_json)),
 recorded_at TEXT NOT NULL,
 source TEXT NOT NULL DEFAULT 'user_entry',
 verification TEXT NOT NULL DEFAULT 'user_reported'
);
CREATE TRIGGER tag_history_no_update BEFORE UPDATE ON device_tag_history BEGIN SELECT RAISE(ABORT,'Tag history is immutable.'); END;
CREATE TRIGGER tag_history_no_delete BEFORE DELETE ON device_tag_history BEGIN SELECT RAISE(ABORT,'Tag history is immutable.'); END;
PRAGMA user_version=26;
COMMIT;
