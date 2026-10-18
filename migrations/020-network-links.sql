PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
CREATE TABLE network_links (
 link_id TEXT PRIMARY KEY NOT NULL,
 endpoint_a TEXT NOT NULL REFERENCES network_interfaces(interface_id),
 endpoint_b TEXT NOT NULL REFERENCES network_interfaces(interface_id),
 medium TEXT NOT NULL CHECK(medium IN('ethernet','fiber','wi-fi','powerline','other')),
 state TEXT NOT NULL CHECK(state IN('planned','observed','retired')),
 speed_mbps REAL CHECK(speed_mbps IS NULL OR (speed_mbps>0 AND speed_mbps<=10000000)),
 source TEXT,
 observed_on TEXT CHECK(observed_on IS NULL OR (length(observed_on)=10 AND date(observed_on,'+0 days')=observed_on)),
 evidence_status TEXT NOT NULL CHECK(evidence_status IN('user_reported','verified','uncertain')),
 notes TEXT,
 CHECK(endpoint_a<endpoint_b), UNIQUE(endpoint_a,endpoint_b),
 CHECK(evidence_status!='verified' OR (observed_on IS NOT NULL AND length(trim(source))>0))
);
CREATE TABLE network_link_sources (
 link_id TEXT NOT NULL REFERENCES network_links(link_id),
 source_id TEXT NOT NULL REFERENCES source_entries(source_id),
 PRIMARY KEY(link_id,source_id)
);
CREATE TABLE network_link_history (
 history_id INTEGER PRIMARY KEY AUTOINCREMENT,
 link_id TEXT NOT NULL,
 action TEXT NOT NULL CHECK(action IN('save','remove')),
 snapshot_json TEXT NOT NULL CHECK(json_valid(snapshot_json)),
 recorded_at TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TRIGGER network_link_history_update BEFORE UPDATE ON network_link_history BEGIN SELECT RAISE(ABORT,'Preserve connection history'); END;
CREATE TRIGGER network_link_history_delete BEFORE DELETE ON network_link_history BEGIN SELECT RAISE(ABORT,'Preserve connection history'); END;
PRAGMA user_version=20;
COMMIT;
