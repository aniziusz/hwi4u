PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
CREATE TABLE os_families (
 value TEXT PRIMARY KEY NOT NULL CHECK(length(trim(value))>0 AND value=lower(value))
);
INSERT INTO os_families(value) VALUES('linux'),('windows'),('macos'),('android'),('ios'),('other');
CREATE TABLE device_software (
 device_id TEXT PRIMARY KEY NOT NULL REFERENCES devices(device_id),
 os_status TEXT NOT NULL DEFAULT 'unknown' CHECK(os_status IN ('unknown','not_applicable','recorded')),
 os_family TEXT REFERENCES os_families(value) ON UPDATE CASCADE ON DELETE RESTRICT,
 os_name TEXT CHECK(os_name IS NULL OR length(trim(os_name))>0),
 os_version TEXT CHECK(os_version IS NULL OR length(trim(os_version))>0),
 firmware_status TEXT NOT NULL DEFAULT 'unknown' CHECK(firmware_status IN ('unknown','not_applicable','recorded')),
 firmware_version TEXT CHECK(firmware_version IS NULL OR length(trim(firmware_version))>0),
 source TEXT CHECK(source IS NULL OR length(trim(source))>0),
 checked_on TEXT CHECK(checked_on IS NULL OR (length(checked_on)=10 AND checked_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(checked_on,'+0 days') IS NOT NULL AND date(checked_on,'+0 days')=checked_on)),
 CHECK((os_status='unknown' AND firmware_status='unknown') OR source IS NOT NULL),
 CHECK((os_status='recorded' AND (os_family IS NOT NULL OR os_name IS NOT NULL)) OR (os_status!='recorded' AND os_family IS NULL AND os_name IS NULL AND os_version IS NULL)),
 CHECK((firmware_status='recorded' AND firmware_version IS NOT NULL) OR (firmware_status!='recorded' AND firmware_version IS NULL))
);
PRAGMA user_version=13;
COMMIT;
