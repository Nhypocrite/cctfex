# Cryptocurrency Trading Website

This is a simple stock trading website built with Flask and MySQL (MariaDB). The website allows users to register, log in, place buy and sell orders, and view a K-line (candlestick) chart based on historical trade data.

#### Features

- User registration and login

- Place buy and sell orders
- View order book
- View K-line chart based on historical trade data
- Simple frontend using HTML, CSS, and JavaScript

#### Prerequisites

1. Before you begin, ensure you have met the following requirements:

- Python 3.x installed on your machine

- MariaDB (or MySQL) installed and running
- Git installed



2. Set up the virtual environment (**optional** but recommended)
You can create a virtual environment to manage dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```



3. Install dependencies
Install the required Python packages using the following command:

```bash
pip install -r requirements.txt
```



4. Set up the database
Login to MariaDB/MySQL:

```bash
mysql -u your_username -p

```

Create the database and tables:

```sql
CREATE DATABASE web_programming;

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
    user_id INT NOT NULL,
    order_type smallint NOT NULL,  -- 1-'buy' 或 2-'sell'
    price DECIMAL(10, 2) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建 trade_history 表
CREATE TABLE IF NOT EXISTS trade_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_type VARCHAR(10) NOT NULL,  -- 'buy' 或 'sell'
    price DECIMAL(10, 2) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

```

5. Configure the application
Open the app.py file and update the database connection configuration with your own credentials:

```python
db_config = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'database': 'stock_trading'
}
```
6. Run the application
You can now start the Flask application:

```bash
python app.py
```
Open your web browser and go to http://127.0.0.1:5000/ to view the website.

#### License

This project is open-source and available under the MIT License.

#### Acknowledgments

Flask framework documentation: Flask
MariaDB documentation: MariaDB