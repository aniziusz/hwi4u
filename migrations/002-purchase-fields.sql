PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;
ALTER TABLE devices ADD COLUMN purchase_date TEXT CHECK(purchase_date IS NULL OR (length(purchase_date)=10 AND purchase_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'));
ALTER TABLE devices ADD COLUMN purchase_price TEXT CHECK(purchase_price IS NULL OR (length(trim(purchase_price))>0 AND purchase_price NOT GLOB '*[^0-9.]*' AND purchase_price GLOB '[0-9]*' AND length(purchase_price)-length(replace(purchase_price,'.',''))<=1));
ALTER TABLE devices ADD COLUMN purchase_currency TEXT CHECK(purchase_currency IS NULL OR (length(purchase_currency)=3 AND purchase_currency NOT GLOB '*[^A-Z]*'));
PRAGMA user_version = 2;
COMMIT;
