PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
CREATE TABLE location_places (
 place_id TEXT PRIMARY KEY NOT NULL,
 place_key TEXT NOT NULL UNIQUE,
 country TEXT, postal_code TEXT, city TEXT, street TEXT, house_number TEXT,
 building TEXT, floor TEXT, room TEXT
);
CREATE TABLE device_locations (
 device_id TEXT PRIMARY KEY NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
 state TEXT NOT NULL CHECK(state IN ('unknown','recorded','not_applicable')),
 place_id TEXT REFERENCES location_places(place_id),
 position TEXT, height_m TEXT, height_reference TEXT, notes TEXT,
 CHECK(height_reference IS NULL OR height_reference IN ('finished_floor','ground_level','other')),
 CHECK((height_m IS NULL AND height_reference IS NULL) OR (height_m IS NOT NULL AND height_reference IS NOT NULL)),
 CHECK(state='recorded' OR (place_id IS NULL AND position IS NULL AND height_m IS NULL AND notes IS NULL))
);
CREATE TABLE device_location_history (
 history_id INTEGER PRIMARY KEY,
 device_id TEXT NOT NULL,
 before_json TEXT NOT NULL CHECK(json_valid(before_json)),
 after_json TEXT NOT NULL CHECK(json_valid(after_json)),
 recorded_at TEXT NOT NULL,
 source TEXT NOT NULL DEFAULT 'user_entry',
 verification TEXT NOT NULL DEFAULT 'user_reported' CHECK(verification='user_reported')
);
CREATE TRIGGER location_place_no_update BEFORE UPDATE ON location_places BEGIN SELECT RAISE(ABORT,'Places are immutable; create or reuse another place.'); END;
CREATE TRIGGER location_place_no_delete BEFORE DELETE ON location_places BEGIN SELECT RAISE(ABORT,'Retain reusable places for placement history.'); END;
CREATE TRIGGER location_history_no_update BEFORE UPDATE ON device_location_history BEGIN SELECT RAISE(ABORT,'Placement history is immutable.'); END;
CREATE TRIGGER location_history_no_delete BEFORE DELETE ON device_location_history BEGIN SELECT RAISE(ABORT,'Placement history is immutable.'); END;
PRAGMA user_version=22;
COMMIT;
