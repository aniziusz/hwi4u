PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
CREATE TABLE connection_options (
 kind TEXT NOT NULL CHECK(kind IN ('interface','protocol')),
 value TEXT NOT NULL CHECK(length(trim(value))>0 AND value=lower(value)),
 PRIMARY KEY(kind,value)
);
CREATE TABLE device_connectivity (
 device_id TEXT NOT NULL REFERENCES devices(device_id),
 kind TEXT NOT NULL CHECK(kind IN ('interface','protocol')),
 supported_status TEXT NOT NULL CHECK(supported_status IN ('unknown','none','recorded')),
 usage_status TEXT NOT NULL CHECK(usage_status IN ('unknown','none','recorded')),
 source TEXT CHECK(source IS NULL OR length(trim(source))>0),
 assessed_on TEXT CHECK(assessed_on IS NULL OR (length(assessed_on)=10 AND assessed_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(assessed_on,'+0 days') IS NOT NULL AND date(assessed_on,'+0 days')=assessed_on)),
 CHECK((supported_status='unknown' AND usage_status='unknown') OR source IS NOT NULL),
 CHECK(usage_status!='recorded' OR supported_status='recorded'),
 CHECK(supported_status!='none' OR usage_status='none'),
 PRIMARY KEY(device_id,kind)
);
CREATE TABLE device_connections (
 device_id TEXT NOT NULL,
 kind TEXT NOT NULL,
 value TEXT NOT NULL,
 in_use INTEGER NOT NULL DEFAULT 0 CHECK(in_use IN (0,1)),
 PRIMARY KEY(device_id,kind,value),
 FOREIGN KEY(device_id,kind) REFERENCES device_connectivity(device_id,kind),
 FOREIGN KEY(kind,value) REFERENCES connection_options(kind,value) ON UPDATE CASCADE ON DELETE RESTRICT
);
INSERT INTO connection_options(kind,value) VALUES('interface','ethernet');
INSERT INTO connection_options(kind,value) VALUES('interface','wi-fi');
INSERT INTO connection_options(kind,value) VALUES('interface','bluetooth');
INSERT INTO connection_options(kind,value) VALUES('interface','usb');
INSERT INTO connection_options(kind,value) VALUES('interface','rs-232');
INSERT INTO connection_options(kind,value) VALUES('interface','rs-485');
INSERT INTO connection_options(kind,value) VALUES('interface','thread');
INSERT INTO connection_options(kind,value) VALUES('interface','z-wave');
INSERT INTO connection_options(kind,value) VALUES('interface','zigbee');
INSERT INTO connection_options(kind,value) VALUES('interface','dect');
INSERT INTO connection_options(kind,value) VALUES('interface','proprietary radio');
INSERT INTO connection_options(kind,value) VALUES('protocol','modbus tcp');
INSERT INTO connection_options(kind,value) VALUES('protocol','modbus rtu');
INSERT INTO connection_options(kind,value) VALUES('protocol','mqtt');
INSERT INTO connection_options(kind,value) VALUES('protocol','http/https');
INSERT INTO connection_options(kind,value) VALUES('protocol','matter');
INSERT INTO connection_options(kind,value) VALUES('protocol','knx');
INSERT INTO connection_options(kind,value) VALUES('protocol','bacnet');
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
PRAGMA user_version=12;
COMMIT;
