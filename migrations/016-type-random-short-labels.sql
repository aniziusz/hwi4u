PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
DROP TRIGGER device_number_insert;
DROP TRIGGER device_number_immutable;
DROP VIEW device_short_ids;
DROP TABLE device_numbers;
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
PRAGMA user_version=16;
COMMIT;
