-- MySQL 8.x initialization for local dev on port 3307
-- 1) Change MySQL port to 3307 in your my.cnf and restart MySQL:
--    [mysqld]
--    port=3307
--    bind-address=0.0.0.0
--    character-set-server=utf8mb4
--    collation-server=utf8mb4_0900_ai_ci
-- 2) Apply this script once with an admin user (e.g., root):
--    mysql -u root -p -P 3307 -h 127.0.0.1 < scripts/mysql_init.sql

-- Database
CREATE DATABASE IF NOT EXISTS demo_db
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

-- Application user
-- CREATE USER IF NOT EXISTS 'apple'@'%' IDENTIFIED BY '1234';

-- Grant privileges
-- GRANT ALL PRIVILEGES ON demo_db.* TO 'apple'@'%' WITH GRANT OPTION;
-- FLUSH PRIVILEGES;

-- Application schema
USE demo_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(64) NOT NULL UNIQUE,
  age INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed data
INSERT IGNORE INTO users (id, username, age) VALUES
  (1, 'alice', 23),
  (2, 'bob', 31);

select * from users;