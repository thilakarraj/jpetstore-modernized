-- Local MySQL 8 setup for JPetStore (run as a user with CREATE USER / GRANT privileges).
-- Replace placeholders before executing. Do not commit real passwords to git.

-- Application database (development)
CREATE DATABASE IF NOT EXISTS jpetstore
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Integration tests only (never run destructive tests against jpetstore)
CREATE DATABASE IF NOT EXISTS jpetstore_test
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Application user (adjust host for your environment: 'localhost', '127.0.0.1', or '%')
CREATE USER IF NOT EXISTS 'jpetstore_app'@'localhost' IDENTIFIED BY '<password>';
CREATE USER IF NOT EXISTS 'jpetstore_app'@'127.0.0.1' IDENTIFIED BY '<password>';

GRANT ALL PRIVILEGES ON jpetstore.* TO 'jpetstore_app'@'localhost';
GRANT ALL PRIVILEGES ON jpetstore.* TO 'jpetstore_app'@'127.0.0.1';
GRANT ALL PRIVILEGES ON jpetstore_test.* TO 'jpetstore_app'@'localhost';
GRANT ALL PRIVILEGES ON jpetstore_test.* TO 'jpetstore_app'@'127.0.0.1';

FLUSH PRIVILEGES;
