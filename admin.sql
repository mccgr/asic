CREATE SCHEMA IF NOT EXISTS asic;
CREATE ROLE asic;
ALTER SCHEMA asic OWNER TO asic;
CREATE ROLE asic_access;
GRANT USAGE ON SCHEMA asic TO asic_access;
