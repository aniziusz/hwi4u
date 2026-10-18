PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
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
PRAGMA user_version=8;
COMMIT;
