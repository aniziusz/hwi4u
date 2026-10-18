PRAGMA foreign_keys=OFF;
BEGIN IMMEDIATE;
UPDATE device_states SET value=lower(value);
UPDATE physical_conditions SET value=lower(value);
CREATE TABLE devices_new (
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
INSERT INTO devices_new ("device_id","purchase_date","purchase_price","purchase_currency","installation_date","current_state","scrapped_date","physical_condition","name","source","recorded_at") SELECT "device_id","purchase_date","purchase_price","purchase_currency","installation_date",lower("current_state"),"scrapped_date",lower("physical_condition"),"name","source","recorded_at" FROM devices;
DROP TABLE devices;
ALTER TABLE devices_new RENAME TO devices;
PRAGMA user_version=9;
COMMIT;
PRAGMA foreign_keys=ON;
