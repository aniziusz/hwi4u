PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
ALTER TABLE devices ADD COLUMN installation_date TEXT CHECK(installation_date IS NULL OR (length(installation_date)=10 AND installation_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'));
ALTER TABLE devices ADD COLUMN current_state TEXT CHECK(current_state IS NULL OR length(trim(current_state))>0);
PRAGMA user_version=3;
COMMIT;
