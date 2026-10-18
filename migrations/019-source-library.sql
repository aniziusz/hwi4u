BEGIN;
CREATE TABLE source_entries (
 source_id TEXT PRIMARY KEY NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN('website','document','photo','observation','legacy_text')),
 title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 200),
 url TEXT,
 relative_path TEXT,
 original_name TEXT,
 sha256 TEXT,
 body TEXT,
 observed_on TEXT CHECK(observed_on IS NULL OR (length(observed_on)=10 AND date(observed_on,'+0 days')=observed_on AND date(observed_on,'+0 days') IS NOT NULL)),
 evidence_status TEXT NOT NULL CHECK(evidence_status IN('uncertain','user_reported','verified')),
 source_note TEXT,
 origin_key TEXT UNIQUE,
 supersedes TEXT REFERENCES source_entries(source_id),
 created_at TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%fZ','now')),
 CHECK((kind='website' AND url IS NOT NULL AND relative_path IS NULL) OR (kind IN('document','photo') AND relative_path IS NOT NULL AND sha256 IS NOT NULL AND original_name IS NOT NULL AND url IS NULL) OR (kind IN('observation','legacy_text') AND body IS NOT NULL AND length(trim(body))>0 AND url IS NULL AND relative_path IS NULL)),
 CHECK(evidence_status!='verified' OR observed_on IS NOT NULL)
);
CREATE TABLE source_links (
 device_id TEXT NOT NULL REFERENCES devices(device_id),
 scope TEXT NOT NULL CHECK(scope IN('device','software','network','interface','protocol')),
 source_id TEXT NOT NULL REFERENCES source_entries(source_id),
 PRIMARY KEY(device_id,scope,source_id)
);
CREATE TABLE source_link_history (
 history_id INTEGER PRIMARY KEY AUTOINCREMENT,
 device_id TEXT NOT NULL REFERENCES devices(device_id),
 links_json TEXT NOT NULL CHECK(json_valid(links_json)),
 recorded_at TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TRIGGER source_entry_update BEFORE UPDATE ON source_entries BEGIN SELECT RAISE(ABORT,'Revise sources by creating a new immutable entry'); END;
CREATE TRIGGER source_entry_delete BEFORE DELETE ON source_entries BEGIN SELECT RAISE(ABORT,'Preserve source evidence'); END;
CREATE TRIGGER source_history_update BEFORE UPDATE ON source_link_history BEGIN SELECT RAISE(ABORT,'Preserve source assignment history'); END;
CREATE TRIGGER source_history_delete BEFORE DELETE ON source_link_history WHEN NOT EXISTS(SELECT 1 FROM deleted_devices WHERE device_id=OLD.device_id) BEGIN SELECT RAISE(ABORT,'Preserve source assignment history'); END;
CREATE TEMP TABLE legacy_source_text AS SELECT device_id,'device' AS scope,source AS body FROM devices WHERE length(trim(source))>0
 UNION ALL SELECT device_id,'software',source FROM device_software WHERE length(trim(source))>0
 UNION ALL SELECT device_id,'network',source FROM device_network WHERE length(trim(source))>0
 UNION ALL SELECT device_id,kind,source FROM device_connectivity WHERE length(trim(source))>0;
INSERT INTO source_entries(source_id,kind,title,body,evidence_status,source_note)
 SELECT lower(hex(randomblob(16))),'legacy_text',substr(body,1,200),body,'uncertain','Preserved existing source text; observation date and independent verification are unknown.' FROM legacy_source_text GROUP BY body;
INSERT INTO source_links(device_id,scope,source_id) SELECT DISTINCT l.device_id,l.scope,s.source_id FROM legacy_source_text l JOIN source_entries s ON s.body=l.body;
INSERT INTO source_link_history(device_id,links_json) SELECT d.device_id,json_object('device',json((SELECT json_group_array(source_id) FROM (SELECT source_id FROM source_links WHERE device_id=d.device_id AND scope='device' ORDER BY source_id))),'software',json((SELECT json_group_array(source_id) FROM (SELECT source_id FROM source_links WHERE device_id=d.device_id AND scope='software' ORDER BY source_id))),'network',json((SELECT json_group_array(source_id) FROM (SELECT source_id FROM source_links WHERE device_id=d.device_id AND scope='network' ORDER BY source_id))),'interface',json((SELECT json_group_array(source_id) FROM (SELECT source_id FROM source_links WHERE device_id=d.device_id AND scope='interface' ORDER BY source_id))),'protocol',json((SELECT json_group_array(source_id) FROM (SELECT source_id FROM source_links WHERE device_id=d.device_id AND scope='protocol' ORDER BY source_id)))) FROM devices d WHERE EXISTS(SELECT 1 FROM source_links l WHERE l.device_id=d.device_id);
DROP TABLE legacy_source_text;
PRAGMA user_version=19;
COMMIT;
