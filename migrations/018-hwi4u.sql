BEGIN;
DROP VIEW device_label_aliases;
DROP VIEW device_short_ids;
DROP TRIGGER device_label_insert;
DROP TRIGGER device_label_reclassify;
DROP TRIGGER short_label_immutable;
DROP TRIGGER short_label_retain;
ALTER TABLE device_short_labels RENAME TO previous_short_labels;
DROP INDEX short_labels_device;
CREATE TABLE device_short_labels (
 label_id INTEGER PRIMARY KEY AUTOINCREMENT,
 device_id TEXT NOT NULL,
 prefix TEXT NOT NULL CHECK(length(prefix)=2 AND prefix NOT GLOB '*[^A-Z]*'),
 number INTEGER NOT NULL CHECK(number BETWEEN 0 AND 99999),
 UNIQUE(prefix,number)
);
CREATE INDEX short_labels_device ON device_short_labels(device_id,label_id);
CREATE VIEW device_label_aliases AS SELECT device_id,prefix||printf('%05d',number) AS short_id FROM device_short_labels WHERE device_id IN(SELECT device_id FROM devices);
CREATE VIEW device_short_ids AS SELECT l.device_id,l.prefix||printf('%05d',l.number) AS short_id
FROM device_short_labels l WHERE l.device_id IN(SELECT device_id FROM devices) AND l.label_id=(SELECT max(other.label_id) FROM device_short_labels other WHERE other.device_id=l.device_id);
INSERT INTO device_short_labels SELECT * FROM previous_short_labels;
DROP TABLE previous_short_labels;
CREATE TRIGGER device_label_insert AFTER INSERT ON devices BEGIN
 INSERT INTO device_short_labels(device_id,prefix,number)
 SELECT NEW.device_id,p.prefix,
 (WITH RECURSIVE candidates(n,attempt) AS (
 SELECT abs(random()%100000),1
 UNION ALL SELECT (n+1)%100000,attempt+1 FROM candidates
 WHERE attempt<100000 AND EXISTS(SELECT 1 FROM device_short_labels WHERE prefix=p.prefix AND number=n)
 ) SELECT n FROM candidates WHERE NOT EXISTS(SELECT 1 FROM device_short_labels WHERE prefix=p.prefix AND number=n) LIMIT 1)
 FROM (SELECT coalesce((SELECT prefix FROM device_type_codes WHERE type_name=NEW.device_type),'UN') AS prefix) p;
END;
CREATE TRIGGER device_label_reclassify AFTER UPDATE OF device_type ON devices
WHEN coalesce((SELECT prefix FROM device_type_codes WHERE type_name=NEW.device_type),'UN') IS NOT (SELECT prefix FROM device_short_labels WHERE device_id=NEW.device_id ORDER BY label_id DESC LIMIT 1)
BEGIN
 INSERT INTO device_short_labels(device_id,prefix,number)
 SELECT NEW.device_id,p.prefix,
 (WITH RECURSIVE candidates(n,attempt) AS (
 SELECT abs(random()%100000),1
 UNION ALL SELECT (n+1)%100000,attempt+1 FROM candidates
 WHERE attempt<100000 AND EXISTS(SELECT 1 FROM device_short_labels WHERE prefix=p.prefix AND number=n)
 ) SELECT n FROM candidates WHERE NOT EXISTS(SELECT 1 FROM device_short_labels WHERE prefix=p.prefix AND number=n) LIMIT 1)
 FROM (SELECT coalesce((SELECT prefix FROM device_type_codes WHERE type_name=NEW.device_type),'UN') AS prefix) p;
END;
CREATE TRIGGER short_label_immutable BEFORE UPDATE ON device_short_labels BEGIN
 SELECT RAISE(ABORT,'Short device labels cannot be changed');
END;
CREATE TRIGGER short_label_retain BEFORE DELETE ON device_short_labels BEGIN
 SELECT RAISE(ABORT,'Retain short label aliases');
END;
ALTER TABLE devices ADD COLUMN purchased_at TEXT CHECK(purchased_at IS NULL OR (length(trim(purchased_at)) BETWEEN 1 AND 200));
CREATE TABLE deleted_devices (
 device_id TEXT PRIMARY KEY NOT NULL,
 deleted_at TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%fZ','now')),
 snapshot_json TEXT NOT NULL CHECK(json_valid(snapshot_json))
);
CREATE TRIGGER deleted_device_reuse BEFORE INSERT ON devices WHEN EXISTS(SELECT 1 FROM deleted_devices WHERE device_id=NEW.device_id) BEGIN
 SELECT RAISE(ABORT,'Deleted device IDs remain reserved');
END;
CREATE TRIGGER short_label_owner BEFORE INSERT ON device_short_labels WHEN NOT EXISTS(SELECT 1 FROM devices WHERE device_id=NEW.device_id) BEGIN
 SELECT RAISE(ABORT,'Short label needs an existing device');
END;
DROP TRIGGER network_observation_delete;
CREATE TRIGGER network_observation_delete BEFORE DELETE ON network_observations WHEN NOT EXISTS(SELECT 1 FROM deleted_devices WHERE device_id=OLD.device_id) BEGIN SELECT RAISE(ABORT,'Preserve network observation history'); END;
CREATE TRIGGER deletion_history_update BEFORE UPDATE ON deleted_devices BEGIN SELECT RAISE(ABORT,'Preserve deletion history'); END;
CREATE TRIGGER deletion_history_delete BEFORE DELETE ON deleted_devices BEGIN SELECT RAISE(ABORT,'Preserve deletion history'); END;
PRAGMA user_version=18;
COMMIT;
