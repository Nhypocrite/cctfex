CREATE DATABASE IF NOT EXISTS web_programming;

USE web_programming;

-- 创建 users 表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(64) NOT NULL  -- 使用SHA-256进行密码哈希，长度为64
);

-- 创建 order_book 表
CREATE TABLE IF NOT EXISTS order_book (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token_id INT NOT NULL,
    user_id INT NOT NULL,
    order_type smallint NOT NULL,  -- 1-'buy', 2-'sell'
    price DECIMAL(10, 2) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    timestamp DATETIME NOT NULL,
    INDEX idx_token_id (token_id)  -- 添加索引用于排序

);

-- 创建 trade_history 表
CREATE TABLE IF NOT EXISTS trade_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token_id INT NOT NULL,
    user_id INT NOT NULL,
    order_type smallint NOT NULL,  -- 1-'buy', 2-'sell'
    price DECIMAL(10, 2) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    timestamp DATETIME NOT NULL,
    INDEX idx_token_id (token_id)  -- 添加索引用于排序

);