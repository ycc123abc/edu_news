CREATE DATABASE IF NOT EXISTS test;

USE test;

CREATE TABLE IF NOT EXISTS edu_news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_web_name VARCHAR(255),
    source_name VARCHAR(255),
    source_url VARCHAR(512),
    title TEXT,
    url VARCHAR(512),
    time DATETIME,
    create_time DATETIME
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;