PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
ALTER TABLE devices ADD COLUMN location TEXT CHECK(location IS NULL OR (typeof(location)='text' AND length(trim(location)) BETWEEN 1 AND 200));
PRAGMA user_version=21;
COMMIT;
