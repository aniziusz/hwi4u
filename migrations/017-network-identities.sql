PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
CREATE TEMP TABLE check_existing_names(name TEXT CHECK(length(name)<=100));
INSERT INTO check_existing_names SELECT name FROM devices;
DROP TABLE check_existing_names;
CREATE TABLE device_network (
 device_id TEXT PRIMARY KEY NOT NULL REFERENCES devices(device_id),
 hostname TEXT CHECK(hostname IS NULL OR length(hostname) BETWEEN 1 AND 253),
 source TEXT CHECK(source IS NULL OR length(trim(source))>0),
 observed_on TEXT CHECK(observed_on IS NULL OR (date(observed_on,'+0 days') IS NOT NULL AND date(observed_on,'+0 days')=observed_on AND length(observed_on)=10)),
 evidence_status TEXT NOT NULL CHECK(evidence_status IN('user_reported','verified','uncertain')),
 CHECK(evidence_status!='verified' OR (source IS NOT NULL AND observed_on IS NOT NULL))
);
CREATE TABLE network_interfaces (
 interface_id TEXT PRIMARY KEY NOT NULL,
 device_id TEXT NOT NULL REFERENCES device_network(device_id),
 label TEXT NOT NULL CHECK(length(trim(label)) BETWEEN 1 AND 100),
 mac_address TEXT CHECK(mac_address IS NULL OR (length(mac_address)=17 AND mac_address NOT GLOB '*[^0-9a-f:]*')),
 UNIQUE(device_id,label)
);
CREATE TABLE network_addresses (
 interface_id TEXT NOT NULL REFERENCES network_interfaces(interface_id),
 address TEXT NOT NULL CHECK(length(address)>0),
 PRIMARY KEY(interface_id,address)
);
CREATE TABLE network_observations (
 observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
 device_id TEXT NOT NULL REFERENCES devices(device_id),
 profile_json TEXT NOT NULL CHECK(json_valid(profile_json)),
 recorded_at TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX network_observations_device ON network_observations(device_id,observation_id);
CREATE TRIGGER network_observation_update BEFORE UPDATE ON network_observations BEGIN
 SELECT RAISE(ABORT,'Preserve network observation history');
END;
CREATE TRIGGER network_observation_delete BEFORE DELETE ON network_observations BEGIN
 SELECT RAISE(ABORT,'Preserve network observation history');
END;
CREATE TRIGGER device_name_length_insert BEFORE INSERT ON devices WHEN length(NEW.name)>100 BEGIN
 SELECT RAISE(ABORT,'Name must be at most 100 characters');
END;
CREATE TRIGGER device_name_length_update BEFORE UPDATE OF name ON devices WHEN length(NEW.name)>100 BEGIN
 SELECT RAISE(ABORT,'Name must be at most 100 characters');
END;
PRAGMA user_version=17;
COMMIT;
