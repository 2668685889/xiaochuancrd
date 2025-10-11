-- 创建数据库
CREATE DATABASE IF NOT EXISTS xiaochuanERP CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户并授权
CREATE USER IF NOT EXISTS 'xiaochuan_user'@'localhost' IDENTIFIED BY 'xiaochuan';
GRANT ALL PRIVILEGES ON xiaochuanERP.* TO 'xiaochuan_user'@'localhost';
FLUSH PRIVILEGES;