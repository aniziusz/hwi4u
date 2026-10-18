BEGIN IMMEDIATE;
ALTER TABLE devices ADD COLUMN scrapped_date TEXT CHECK(scrapped_date IS NULL OR (length(scrapped_date)=10 AND scrapped_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'));
PRAGMA user_version=4;
COMMIT;
