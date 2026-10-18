PRAGMA foreign_keys=OFF;
BEGIN IMMEDIATE;
CREATE TABLE devices_new (
 device_id TEXT PRIMARY KEY CHECK(length(trim(device_id))>0),
 purchase_date TEXT CHECK(purchase_date IS NULL OR (length(purchase_date)=10 AND purchase_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')),
 purchase_price TEXT CHECK(purchase_price IS NULL OR (length(trim(purchase_price))>0 AND purchase_price NOT GLOB '*[^0-9.]*' AND purchase_price GLOB '[0-9]*' AND length(purchase_price)-length(replace(purchase_price,'.',''))<=1)),
 purchase_currency TEXT CHECK(purchase_currency IS NULL OR (length(purchase_currency)=3 AND purchase_currency NOT GLOB '*[^A-Z]*')),
 installation_date TEXT CHECK(installation_date IS NULL OR (length(installation_date)=10 AND installation_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')),
 current_state TEXT CHECK(current_state IS NULL OR current_state IN ('Awaiting installation','In use','Spare','In storage','Under assessment','Under repair','Retired','Sold','Given away','Returned','Lost','Stolen','Scrapped')),
 scrapped_date TEXT CHECK(scrapped_date IS NULL OR (length(scrapped_date)=10 AND scrapped_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')),
 physical_condition TEXT CHECK(physical_condition IS NULL OR physical_condition IN ('Working','Partially working','Faulty','Untested')),
 name TEXT NOT NULL CHECK(length(trim(name))>0),
 source TEXT NOT NULL CHECK(length(trim(source))>0),
 recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
INSERT INTO devices_new ("device_id","name","source","recorded_at","purchase_date","purchase_price","purchase_currency","installation_date","current_state","scrapped_date","physical_condition") SELECT "device_id","name","source","recorded_at","purchase_date","purchase_price","purchase_currency","installation_date","current_state","scrapped_date","physical_condition" FROM devices;
DROP TABLE devices;
ALTER TABLE devices_new RENAME TO devices;
PRAGMA user_version=6;
COMMIT;
PRAGMA foreign_keys=ON;
