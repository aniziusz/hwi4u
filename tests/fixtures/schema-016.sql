PRAGMA foreign_keys = ON;
BEGIN;
CREATE TABLE device_states (value TEXT PRIMARY KEY NOT NULL CHECK(length(trim(value))>0));
INSERT INTO device_states(value) VALUES ('awaiting installation'),('in use'),('spare'),('in storage'),('under assessment'),('under repair'),('retired'),('sold'),('given away'),('returned'),('lost'),('stolen'),('scrapped');
CREATE TABLE physical_conditions (value TEXT PRIMARY KEY NOT NULL CHECK(length(trim(value))>0));
INSERT INTO physical_conditions(value) VALUES ('working'),('partially working'),('faulty'),('untested');
CREATE TABLE device_type_groups (
 group_name TEXT PRIMARY KEY NOT NULL CHECK(length(trim(group_name))>0 AND group_name=lower(group_name))
);
CREATE TABLE device_types (
 type_name TEXT PRIMARY KEY NOT NULL CHECK(length(trim(type_name))>0 AND type_name=lower(type_name)),
 group_name TEXT NOT NULL REFERENCES device_type_groups(group_name) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX types_group ON device_types(group_name);
INSERT INTO device_type_groups(group_name) VALUES('computers');
INSERT INTO device_types(type_name,group_name) VALUES('server','computers');
INSERT INTO device_types(type_name,group_name) VALUES('desktop computer','computers');
INSERT INTO device_types(type_name,group_name) VALUES('laptop','computers');
INSERT INTO device_types(type_name,group_name) VALUES('single-board computer','computers');
INSERT INTO device_type_groups(group_name) VALUES('networking');
INSERT INTO device_types(type_name,group_name) VALUES('router','networking');
INSERT INTO device_types(type_name,group_name) VALUES('firewall appliance','networking');
INSERT INTO device_types(type_name,group_name) VALUES('network switch','networking');
INSERT INTO device_types(type_name,group_name) VALUES('wireless access point','networking');
INSERT INTO device_types(type_name,group_name) VALUES('modem','networking');
INSERT INTO device_types(type_name,group_name) VALUES('ont','networking');
INSERT INTO device_types(type_name,group_name) VALUES('network adapter','networking');
INSERT INTO device_type_groups(group_name) VALUES('storage');
INSERT INTO device_types(type_name,group_name) VALUES('nas appliance','storage');
INSERT INTO device_types(type_name,group_name) VALUES('external storage enclosure','storage');
INSERT INTO device_types(type_name,group_name) VALUES('hdd','storage');
INSERT INTO device_types(type_name,group_name) VALUES('ssd','storage');
INSERT INTO device_types(type_name,group_name) VALUES('usb flash drive','storage');
INSERT INTO device_types(type_name,group_name) VALUES('memory card','storage');
INSERT INTO device_types(type_name,group_name) VALUES('optical drive','storage');
INSERT INTO device_types(type_name,group_name) VALUES('tape drive','storage');
INSERT INTO device_type_groups(group_name) VALUES('internal components');
INSERT INTO device_types(type_name,group_name) VALUES('mainboard','internal components');
INSERT INTO device_types(type_name,group_name) VALUES('cpu','internal components');
INSERT INTO device_types(type_name,group_name) VALUES('memory module','internal components');
INSERT INTO device_types(type_name,group_name) VALUES('graphics card','internal components');
INSERT INTO device_types(type_name,group_name) VALUES('storage controller','internal components');
INSERT INTO device_types(type_name,group_name) VALUES('expansion card','internal components');
INSERT INTO device_types(type_name,group_name) VALUES('power supply','internal components');
INSERT INTO device_types(type_name,group_name) VALUES('case','internal components');
INSERT INTO device_types(type_name,group_name) VALUES('cooling component','internal components');
INSERT INTO device_type_groups(group_name) VALUES('power');
INSERT INTO device_types(type_name,group_name) VALUES('ups','power');
INSERT INTO device_types(type_name,group_name) VALUES('power distribution unit','power');
INSERT INTO device_types(type_name,group_name) VALUES('power adapter','power');
INSERT INTO device_types(type_name,group_name) VALUES('battery','power');
INSERT INTO device_type_groups(group_name) VALUES('peripherals');
INSERT INTO device_types(type_name,group_name) VALUES('monitor','peripherals');
INSERT INTO device_types(type_name,group_name) VALUES('keyboard','peripherals');
INSERT INTO device_types(type_name,group_name) VALUES('mouse','peripherals');
INSERT INTO device_types(type_name,group_name) VALUES('printer','peripherals');
INSERT INTO device_types(type_name,group_name) VALUES('scanner','peripherals');
INSERT INTO device_types(type_name,group_name) VALUES('external optical drive','peripherals');
INSERT INTO device_type_groups(group_name) VALUES('home automation');
INSERT INTO device_types(type_name,group_name) VALUES('automation hub','home automation');
INSERT INTO device_types(type_name,group_name) VALUES('sensor','home automation');
INSERT INTO device_types(type_name,group_name) VALUES('actuator','home automation');
INSERT INTO device_types(type_name,group_name) VALUES('smart plug','home automation');
INSERT INTO device_types(type_name,group_name) VALUES('camera','home automation');
INSERT INTO device_types(type_name,group_name) VALUES('smoke detector','home automation');
INSERT INTO device_types(type_name,group_name) VALUES('smoke detector hub','home automation');
INSERT INTO device_type_groups(group_name) VALUES('accessories');
INSERT INTO device_types(type_name,group_name) VALUES('cable','accessories');
INSERT INTO device_types(type_name,group_name) VALUES('adapter','accessories');
INSERT INTO device_types(type_name,group_name) VALUES('rack','accessories');
INSERT INTO device_types(type_name,group_name) VALUES('patch panel','accessories');
INSERT INTO device_type_groups(group_name) VALUES('telephony');
INSERT INTO device_types(type_name,group_name) VALUES('mobile phone','telephony');
INSERT INTO device_types(type_name,group_name) VALUES('dect telephone','telephony');
INSERT INTO device_types(type_name,group_name) VALUES('dect base station','telephony');
INSERT INTO device_type_groups(group_name) VALUES('gaming and entertainment');
INSERT INTO device_types(type_name,group_name) VALUES('gaming console','gaming and entertainment');
INSERT INTO device_type_groups(group_name) VALUES('building equipment');
INSERT INTO device_types(type_name,group_name) VALUES('boiler','building equipment');
INSERT INTO device_type_groups(group_name) VALUES('other');
INSERT INTO device_types(type_name,group_name) VALUES('other','other');
CREATE TABLE devices (
 device_type TEXT REFERENCES device_types(type_name) ON UPDATE CASCADE ON DELETE RESTRICT,
 device_id TEXT PRIMARY KEY CHECK(length(trim(device_id))>0),
 purchase_date TEXT CHECK(purchase_date IS NULL OR (length(purchase_date)=10 AND purchase_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')),
 purchase_price TEXT CHECK(purchase_price IS NULL OR (length(trim(purchase_price))>0 AND purchase_price NOT GLOB '*[^0-9.]*' AND purchase_price GLOB '[0-9]*' AND length(purchase_price)-length(replace(purchase_price,'.',''))<=1)),
 purchase_currency TEXT CHECK(purchase_currency IS NULL OR (length(purchase_currency)=3 AND purchase_currency NOT GLOB '*[^A-Z]*')),
 installation_date TEXT CHECK(installation_date IS NULL OR (length(installation_date)=10 AND installation_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')),
 current_state TEXT REFERENCES device_states(value) ON UPDATE RESTRICT ON DELETE RESTRICT CHECK(current_state IS NULL OR current_state IN ('awaiting installation','in use','spare','in storage','under assessment','under repair','retired','sold','given away','returned','lost','stolen','scrapped')),
 scrapped_date TEXT CHECK(scrapped_date IS NULL OR (length(scrapped_date)=10 AND scrapped_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')),
 physical_condition TEXT REFERENCES physical_conditions(value) ON UPDATE RESTRICT ON DELETE RESTRICT CHECK(physical_condition IS NULL OR physical_condition IN ('working','partially working','faulty','untested')),
 name TEXT NOT NULL CHECK(length(trim(name))>0),
 source TEXT NOT NULL CHECK(length(trim(source))>0),
 recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
CREATE TABLE facts (
 fact_id INTEGER PRIMARY KEY,
 device_id TEXT NOT NULL REFERENCES devices(device_id),
 field TEXT NOT NULL CHECK(length(trim(field))>0),
 value TEXT NOT NULL CHECK(length(trim(value))>0),
 unit TEXT,
 source TEXT NOT NULL CHECK(length(trim(source))>0),
 evidence_status TEXT NOT NULL DEFAULT 'user_reported'
 CHECK(evidence_status IN ('user_reported','verified','uncertain')),
 verified_on TEXT,
 recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
 CHECK(evidence_status != 'verified' OR verified_on IS NOT NULL)
);
CREATE INDEX facts_device ON facts(device_id);
CREATE TABLE relationships (
 relationship_id INTEGER PRIMARY KEY,
 from_device TEXT NOT NULL REFERENCES devices(device_id),
 to_device TEXT NOT NULL REFERENCES devices(device_id),
 relation TEXT NOT NULL CHECK(length(trim(relation))>0),
 source TEXT NOT NULL CHECK(length(trim(source))>0),
 CHECK(from_device != to_device),
 UNIQUE(from_device,to_device,relation)
);
CREATE TABLE component_installations (
 installation_id INTEGER PRIMARY KEY,
 parent_device TEXT NOT NULL REFERENCES devices(device_id),
 component_device TEXT NOT NULL REFERENCES devices(device_id),
 position TEXT CHECK(position IS NULL OR length(trim(position))>0),
 installed_on TEXT CHECK(installed_on IS NULL OR (length(installed_on)=10 AND installed_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(installed_on,'+0 days') IS NOT NULL AND date(installed_on,'+0 days')=installed_on)),
 removed_on TEXT CHECK(removed_on IS NULL OR (length(removed_on)=10 AND removed_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(removed_on,'+0 days') IS NOT NULL AND date(removed_on,'+0 days')=removed_on)),
 source TEXT NOT NULL CHECK(length(trim(source))>0),
 removal_source TEXT CHECK(removal_source IS NULL OR length(trim(removal_source))>0),
 recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
 CHECK(parent_device != component_device),
 CHECK(installed_on IS NULL OR removed_on IS NULL OR removed_on > installed_on),
 CHECK(removed_on IS NULL OR removal_source IS NOT NULL)
);
CREATE INDEX component_parent ON component_installations(parent_device);
CREATE INDEX component_child ON component_installations(component_device);
CREATE TRIGGER validate_component_insert BEFORE INSERT ON component_installations BEGIN
 SELECT RAISE(ABORT,'Component installation periods overlap') WHERE EXISTS (
 SELECT 1 FROM component_installations i WHERE i.component_device=NEW.component_device
 AND coalesce(i.installed_on,'0001-01-01') < coalesce(NEW.removed_on,'9999-12-31')
 AND coalesce(NEW.installed_on,'0001-01-01') < coalesce(i.removed_on,'9999-12-31'));
 SELECT RAISE(ABORT,'Assembly position already occupied during this period') WHERE NEW.position IS NOT NULL AND EXISTS (
 SELECT 1 FROM component_installations i WHERE i.parent_device=NEW.parent_device AND i.position=NEW.position
 AND coalesce(i.installed_on,'0001-01-01') < coalesce(NEW.removed_on,'9999-12-31')
 AND coalesce(NEW.installed_on,'0001-01-01') < coalesce(i.removed_on,'9999-12-31'));
 SELECT RAISE(ABORT,'Assembly cycle during installation period') WHERE EXISTS (
 WITH RECURSIVE ancestors(device,lo,hi) AS (
 SELECT NEW.parent_device,coalesce(NEW.installed_on,'0001-01-01'),coalesce(NEW.removed_on,'9999-12-31')
 UNION
 SELECT i.parent_device,max(a.lo,coalesce(i.installed_on,'0001-01-01')),min(a.hi,coalesce(i.removed_on,'9999-12-31'))
 FROM component_installations i JOIN ancestors a ON i.component_device=a.device
 WHERE max(a.lo,coalesce(i.installed_on,'0001-01-01')) < min(a.hi,coalesce(i.removed_on,'9999-12-31')))
 SELECT 1 FROM ancestors WHERE device=NEW.component_device);
END;
CREATE TRIGGER validate_component_update BEFORE UPDATE ON component_installations BEGIN
 SELECT RAISE(ABORT,'Component installation periods overlap') WHERE EXISTS (
 SELECT 1 FROM component_installations i WHERE i.installation_id != NEW.installation_id AND i.component_device=NEW.component_device
 AND coalesce(i.installed_on,'0001-01-01') < coalesce(NEW.removed_on,'9999-12-31')
 AND coalesce(NEW.installed_on,'0001-01-01') < coalesce(i.removed_on,'9999-12-31'));
 SELECT RAISE(ABORT,'Assembly position already occupied during this period') WHERE NEW.position IS NOT NULL AND EXISTS (
 SELECT 1 FROM component_installations i WHERE i.installation_id != NEW.installation_id AND i.parent_device=NEW.parent_device AND i.position=NEW.position
 AND coalesce(i.installed_on,'0001-01-01') < coalesce(NEW.removed_on,'9999-12-31')
 AND coalesce(NEW.installed_on,'0001-01-01') < coalesce(i.removed_on,'9999-12-31'));
 SELECT RAISE(ABORT,'Assembly cycle during installation period') WHERE EXISTS (
 WITH RECURSIVE ancestors(device,lo,hi) AS (
 SELECT NEW.parent_device,coalesce(NEW.installed_on,'0001-01-01'),coalesce(NEW.removed_on,'9999-12-31')
 UNION
 SELECT i.parent_device,max(a.lo,coalesce(i.installed_on,'0001-01-01')),min(a.hi,coalesce(i.removed_on,'9999-12-31'))
 FROM component_installations i JOIN ancestors a ON i.component_device=a.device
 WHERE i.installation_id != NEW.installation_id AND max(a.lo,coalesce(i.installed_on,'0001-01-01')) < min(a.hi,coalesce(i.removed_on,'9999-12-31')))
 SELECT 1 FROM ancestors WHERE device=NEW.component_device);
END;
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
CREATE INDEX devices_type ON devices(device_type);
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
INSERT INTO os_families(value) VALUES('freebsd');
INSERT INTO connection_options(kind,value) VALUES('protocol','nvme');
INSERT INTO connection_options(kind,value) VALUES('interface','m.2'),('interface','sata'),('interface','pcie'),('interface','so-dimm'),('interface','hdmi'),('interface','displayport');
CREATE TABLE device_type_codes (
 type_name TEXT PRIMARY KEY NOT NULL REFERENCES device_types(type_name) ON UPDATE CASCADE ON DELETE RESTRICT,
 prefix TEXT NOT NULL UNIQUE CHECK(length(prefix)=2 AND prefix NOT GLOB '*[^A-Z]*' AND prefix!='UN')
);
INSERT INTO device_type_codes(type_name,prefix) VALUES('server','SV');
INSERT INTO device_type_codes(type_name,prefix) VALUES('desktop computer','PC');
INSERT INTO device_type_codes(type_name,prefix) VALUES('laptop','LT');
INSERT INTO device_type_codes(type_name,prefix) VALUES('single-board computer','SB');
INSERT INTO device_type_codes(type_name,prefix) VALUES('router','RT');
INSERT INTO device_type_codes(type_name,prefix) VALUES('firewall appliance','FW');
INSERT INTO device_type_codes(type_name,prefix) VALUES('network switch','SW');
INSERT INTO device_type_codes(type_name,prefix) VALUES('wireless access point','AP');
INSERT INTO device_type_codes(type_name,prefix) VALUES('modem','MD');
INSERT INTO device_type_codes(type_name,prefix) VALUES('ont','ON');
INSERT INTO device_type_codes(type_name,prefix) VALUES('network adapter','NA');
INSERT INTO device_type_codes(type_name,prefix) VALUES('nas appliance','NS');
INSERT INTO device_type_codes(type_name,prefix) VALUES('external storage enclosure','SE');
INSERT INTO device_type_codes(type_name,prefix) VALUES('hdd','HD');
INSERT INTO device_type_codes(type_name,prefix) VALUES('ssd','SS');
INSERT INTO device_type_codes(type_name,prefix) VALUES('usb flash drive','UF');
INSERT INTO device_type_codes(type_name,prefix) VALUES('memory card','MC');
INSERT INTO device_type_codes(type_name,prefix) VALUES('optical drive','OD');
INSERT INTO device_type_codes(type_name,prefix) VALUES('tape drive','TD');
INSERT INTO device_type_codes(type_name,prefix) VALUES('mainboard','MB');
INSERT INTO device_type_codes(type_name,prefix) VALUES('cpu','CP');
INSERT INTO device_type_codes(type_name,prefix) VALUES('memory module','MM');
INSERT INTO device_type_codes(type_name,prefix) VALUES('graphics card','GC');
INSERT INTO device_type_codes(type_name,prefix) VALUES('storage controller','SC');
INSERT INTO device_type_codes(type_name,prefix) VALUES('expansion card','EC');
INSERT INTO device_type_codes(type_name,prefix) VALUES('power supply','PS');
INSERT INTO device_type_codes(type_name,prefix) VALUES('case','CS');
INSERT INTO device_type_codes(type_name,prefix) VALUES('cooling component','CL');
INSERT INTO device_type_codes(type_name,prefix) VALUES('ups','UP');
INSERT INTO device_type_codes(type_name,prefix) VALUES('power distribution unit','PD');
INSERT INTO device_type_codes(type_name,prefix) VALUES('power adapter','PA');
INSERT INTO device_type_codes(type_name,prefix) VALUES('battery','BT');
INSERT INTO device_type_codes(type_name,prefix) VALUES('monitor','MN');
INSERT INTO device_type_codes(type_name,prefix) VALUES('keyboard','KB');
INSERT INTO device_type_codes(type_name,prefix) VALUES('mouse','MS');
INSERT INTO device_type_codes(type_name,prefix) VALUES('printer','PR');
INSERT INTO device_type_codes(type_name,prefix) VALUES('scanner','SN');
INSERT INTO device_type_codes(type_name,prefix) VALUES('external optical drive','EO');
INSERT INTO device_type_codes(type_name,prefix) VALUES('automation hub','AH');
INSERT INTO device_type_codes(type_name,prefix) VALUES('sensor','SR');
INSERT INTO device_type_codes(type_name,prefix) VALUES('actuator','AC');
INSERT INTO device_type_codes(type_name,prefix) VALUES('smart plug','SP');
INSERT INTO device_type_codes(type_name,prefix) VALUES('camera','CA');
INSERT INTO device_type_codes(type_name,prefix) VALUES('smoke detector','SD');
INSERT INTO device_type_codes(type_name,prefix) VALUES('smoke detector hub','SH');
INSERT INTO device_type_codes(type_name,prefix) VALUES('cable','CB');
INSERT INTO device_type_codes(type_name,prefix) VALUES('adapter','AD');
INSERT INTO device_type_codes(type_name,prefix) VALUES('rack','RK');
INSERT INTO device_type_codes(type_name,prefix) VALUES('patch panel','PP');
INSERT INTO device_type_codes(type_name,prefix) VALUES('mobile phone','MP');
INSERT INTO device_type_codes(type_name,prefix) VALUES('dect telephone','DP');
INSERT INTO device_type_codes(type_name,prefix) VALUES('dect base station','DB');
INSERT INTO device_type_codes(type_name,prefix) VALUES('gaming console','GA');
INSERT INTO device_type_codes(type_name,prefix) VALUES('boiler','BL');
INSERT INTO device_type_codes(type_name,prefix) VALUES('other','OT');
INSERT INTO device_type_codes(type_name,prefix)
SELECT t.type_name,c.prefix FROM
 (SELECT type_name,row_number() OVER(ORDER BY type_name) AS rn FROM device_types WHERE type_name NOT IN(SELECT type_name FROM device_type_codes)) t
JOIN
 (SELECT prefix,row_number() OVER(ORDER BY prefix) AS rn FROM
  (SELECT char(65+a.n)||char(65+b.n) AS prefix FROM
   (WITH RECURSIVE nums(n) AS(VALUES(0) UNION ALL SELECT n+1 FROM nums WHERE n<25) SELECT n FROM nums) a CROSS JOIN
   (WITH RECURSIVE nums(n) AS(VALUES(0) UNION ALL SELECT n+1 FROM nums WHERE n<25) SELECT n FROM nums) b)
 WHERE prefix!='UN' AND prefix NOT IN(SELECT prefix FROM device_type_codes)) c USING(rn);
CREATE TABLE device_short_labels (
 label_id INTEGER PRIMARY KEY AUTOINCREMENT,
 device_id TEXT NOT NULL REFERENCES devices(device_id),
 prefix TEXT NOT NULL CHECK(length(prefix)=2 AND prefix NOT GLOB '*[^A-Z]*'),
 number INTEGER NOT NULL CHECK(number BETWEEN 0 AND 99999),
 UNIQUE(prefix,number)
);
CREATE INDEX short_labels_device ON device_short_labels(device_id,label_id);
CREATE VIEW device_label_aliases AS SELECT device_id,prefix||printf('%05d',number) AS short_id FROM device_short_labels;
CREATE VIEW device_short_ids AS SELECT l.device_id,l.prefix||printf('%05d',l.number) AS short_id
FROM device_short_labels l WHERE l.label_id=(SELECT max(other.label_id) FROM device_short_labels other WHERE other.device_id=l.device_id);
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
UPDATE devices SET device_type=device_type;
PRAGMA user_version = 16;
COMMIT;
