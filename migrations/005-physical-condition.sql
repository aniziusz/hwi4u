PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
ALTER TABLE devices ADD COLUMN physical_condition TEXT CHECK(physical_condition IS NULL OR length(trim(physical_condition))>0);
PRAGMA user_version=5;
COMMIT;
