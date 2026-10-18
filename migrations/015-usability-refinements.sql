PRAGMA foreign_keys=OFF;
BEGIN IMMEDIATE;
DROP TRIGGER connections_insert;
DROP TRIGGER connections_update;
DROP TRIGGER connectivity_status_update;
CREATE TABLE device_connectivity_new (
 device_id TEXT NOT NULL REFERENCES devices(device_id),
 kind TEXT NOT NULL CHECK(kind IN ('interface','protocol')),
 supported_status TEXT NOT NULL CHECK(supported_status IN ('unknown','none','recorded')),
 usage_status TEXT NOT NULL CHECK(usage_status IN ('unknown','none','recorded')),
 source TEXT CHECK(source IS NULL OR length(trim(source))>0),
 assessed_on TEXT CHECK(assessed_on IS NULL OR (length(assessed_on)=10 AND assessed_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(assessed_on,'+0 days') IS NOT NULL AND date(assessed_on,'+0 days')=assessed_on)),
 CHECK(usage_status!='recorded' OR supported_status='recorded'),
 CHECK(supported_status!='none' OR usage_status='none'),
 PRIMARY KEY(device_id,kind)
);
INSERT INTO device_connectivity_new SELECT * FROM device_connectivity;
DROP TABLE device_connectivity;
ALTER TABLE device_connectivity_new RENAME TO device_connectivity;
CREATE TRIGGER connections_insert BEFORE INSERT ON device_connections BEGIN
 SELECT RAISE(ABORT,'Supported status must be recorded') WHERE NOT EXISTS (
 SELECT 1 FROM device_connectivity WHERE device_id=NEW.device_id AND kind=NEW.kind AND supported_status='recorded');
 SELECT RAISE(ABORT,'Usage status must be recorded for in-use values') WHERE NEW.in_use=1 AND NOT EXISTS (
 SELECT 1 FROM device_connectivity WHERE device_id=NEW.device_id AND kind=NEW.kind AND usage_status='recorded');
END;
CREATE TRIGGER connections_update BEFORE UPDATE ON device_connections BEGIN
 SELECT RAISE(ABORT,'Supported status must be recorded') WHERE NOT EXISTS (
 SELECT 1 FROM device_connectivity WHERE device_id=NEW.device_id AND kind=NEW.kind AND supported_status='recorded');
 SELECT RAISE(ABORT,'Usage status must be recorded for in-use values') WHERE NEW.in_use=1 AND NOT EXISTS (
 SELECT 1 FROM device_connectivity WHERE device_id=NEW.device_id AND kind=NEW.kind AND usage_status='recorded');
END;
CREATE TRIGGER connectivity_status_update BEFORE UPDATE ON device_connectivity BEGIN
 SELECT RAISE(ABORT,'Clear supported choices before changing status') WHERE NEW.supported_status!='recorded' AND EXISTS (
 SELECT 1 FROM device_connections WHERE device_id=OLD.device_id AND kind=OLD.kind);
 SELECT RAISE(ABORT,'Clear in-use choices before changing usage status') WHERE NEW.usage_status!='recorded' AND EXISTS (
 SELECT 1 FROM device_connections WHERE device_id=OLD.device_id AND kind=OLD.kind AND in_use=1);
END;
DELETE FROM device_connections WHERE kind='protocol' AND value='knx';
UPDATE device_connectivity SET usage_status='unknown' WHERE usage_status='recorded' AND NOT EXISTS(SELECT 1 FROM device_connections d WHERE d.device_id=device_connectivity.device_id AND d.kind=device_connectivity.kind AND d.in_use=1);
UPDATE device_connectivity SET supported_status='unknown' WHERE supported_status='recorded' AND NOT EXISTS(SELECT 1 FROM device_connections d WHERE d.device_id=device_connectivity.device_id AND d.kind=device_connectivity.kind);
DELETE FROM connection_options WHERE kind='protocol' AND value='knx';
INSERT INTO os_families(value) VALUES('freebsd');
INSERT INTO connection_options(kind,value) VALUES('protocol','nvme');
INSERT INTO connection_options(kind,value) VALUES('interface','m.2'),('interface','sata'),('interface','pcie'),('interface','so-dimm'),('interface','hdmi'),('interface','displayport');
CREATE TABLE device_numbers (
 short_number INTEGER PRIMARY KEY AUTOINCREMENT,
 device_id TEXT NOT NULL UNIQUE REFERENCES devices(device_id)
);
INSERT INTO device_numbers(device_id) SELECT device_id FROM devices ORDER BY recorded_at,name,device_id;
CREATE VIEW device_short_ids AS SELECT device_id,printf('hw-%04d',short_number) AS short_id FROM device_numbers;
CREATE TRIGGER device_number_insert AFTER INSERT ON devices BEGIN
 INSERT INTO device_numbers(device_id) VALUES(NEW.device_id);
END;
CREATE TRIGGER device_number_immutable BEFORE UPDATE ON device_numbers BEGIN
 SELECT RAISE(ABORT,'Short device IDs cannot be changed');
END;
PRAGMA user_version=15;
COMMIT;
PRAGMA foreign_keys=ON;
