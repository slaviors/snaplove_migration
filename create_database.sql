-- Create database for SnapLove migration
-- Run this manually if you prefer to create the database before running migration

CREATE DATABASE IF NOT EXISTS `snaplove_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Grant privileges (adjust username as needed)
-- GRANT ALL PRIVILEGES ON snaplove_db.* TO 'your_mysql_user'@'localhost';
-- FLUSH PRIVILEGES;
