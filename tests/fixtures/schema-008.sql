BEGIN TRANSACTION;
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
CREATE TABLE device_states (value TEXT PRIMARY KEY NOT NULL CHECK(length(trim(value))>0));
INSERT INTO "device_states" VALUES('Awaiting installation');
INSERT INTO "device_states" VALUES('In use');
INSERT INTO "device_states" VALUES('Spare');
INSERT INTO "device_states" VALUES('In storage');
INSERT INTO "device_states" VALUES('Under assessment');
INSERT INTO "device_states" VALUES('Under repair');
INSERT INTO "device_states" VALUES('Retired');
INSERT INTO "device_states" VALUES('Sold');
INSERT INTO "device_states" VALUES('Given away');
INSERT INTO "device_states" VALUES('Returned');
INSERT INTO "device_states" VALUES('Lost');
INSERT INTO "device_states" VALUES('Stolen');
INSERT INTO "device_states" VALUES('Scrapped');
CREATE TABLE "devices" (
 device_id TEXT PRIMARY KEY CHECK(length(trim(device_id))>0),
 purchase_date TEXT CHECK(purchase_date IS NULL OR (length(purchase_date)=10 AND purchase_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')),
 purchase_price TEXT CHECK(purchase_price IS NULL OR (length(trim(purchase_price))>0 AND purchase_price NOT GLOB '*[^0-9.]*' AND purchase_price GLOB '[0-9]*' AND length(purchase_price)-length(replace(purchase_price,'.',''))<=1)),
 purchase_currency TEXT CHECK(purchase_currency IS NULL OR (length(purchase_currency)=3 AND purchase_currency NOT GLOB '*[^A-Z]*')),
 installation_date TEXT CHECK(installation_date IS NULL OR (length(installation_date)=10 AND installation_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')),
 current_state TEXT REFERENCES device_states(value) ON UPDATE RESTRICT ON DELETE RESTRICT CHECK(current_state IS NULL OR current_state IN ('Awaiting installation','In use','Spare','In storage','Under assessment','Under repair','Retired','Sold','Given away','Returned','Lost','Stolen','Scrapped')),
 scrapped_date TEXT CHECK(scrapped_date IS NULL OR (length(scrapped_date)=10 AND scrapped_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')),
 physical_condition TEXT REFERENCES physical_conditions(value) ON UPDATE RESTRICT ON DELETE RESTRICT CHECK(physical_condition IS NULL OR physical_condition IN ('Working','Partially working','Faulty','Untested')),
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
CREATE TABLE physical_conditions (value TEXT PRIMARY KEY NOT NULL CHECK(length(trim(value))>0));
INSERT INTO "physical_conditions" VALUES('Working');
INSERT INTO "physical_conditions" VALUES('Partially working');
INSERT INTO "physical_conditions" VALUES('Faulty');
INSERT INTO "physical_conditions" VALUES('Untested');
CREATE TABLE relationships (
 relationship_id INTEGER PRIMARY KEY,
 from_device TEXT NOT NULL REFERENCES devices(device_id),
 to_device TEXT NOT NULL REFERENCES devices(device_id),
 relation TEXT NOT NULL CHECK(length(trim(relation))>0),
 source TEXT NOT NULL CHECK(length(trim(source))>0),
 CHECK(from_device != to_device),
 UNIQUE(from_device,to_device,relation)
);
CREATE INDEX facts_device ON facts(device_id);
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
COMMIT;
PRAGMA user_version=8;
