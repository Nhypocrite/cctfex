from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import mysql.connector
import hashlib
import random
from datetime import datetime, timedelta

app = Flask(__name__)
salt = "NTUSALT1234"

# 配置数据库连接
db_config = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "database": "web_programming",
}


def hash_password(password):
    return hashlib.sha256((password+salt).encode('utf-8')).hexdigest()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        encrypted_password = hash_password(request.form["password"])
        
        # 插入用户数据到数据库
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, encrypted_password),
            )
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for("login"))
        except mysql.connector.Error as err:
            return "Fail: {}".format(err), 400
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        encrypted_password = hash_password(request.form["password"])

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, username, password FROM users WHERE username = %s", (username,)
        )
        user = cursor.fetchone()

        if user and user[2] == encrypted_password:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("index"))

        cursor.close()
        connection.close()

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("login"))


# 主页
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session["username"])

# 下单操作
@app.route("/place_order", methods=["POST"])
def place_order():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    data = request.json
    order_type = data["type"]
    price = data["price"]
    amount = data["amount"]
    user_id = session["user_id"]

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    # TODO: 写一下撮合交易
    cursor.execute(
        "INSERT INTO order_book (user_id, order_type, price, amount) VALUES (%s, %s, %s, %s)",
        (user_id, order_type, price, amount),
    )
    connection.commit()

    cursor.execute(
        "INSERT INTO trade_history (user_id, order_type, price, amount) VALUES (%s, %s, %s, %s)",
        (user_id, order_type, price, amount),
    )
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"status": "success"})

# 获取订单簿数据
@app.route("/order_book", methods=["GET"])
def get_order_book():
    order_type = request.args.get('order_type', '').lower()
    
    # Validate order_type to be either 'buy' or 'sell'
    if order_type not in ['buy', 'sell']:
        return jsonify({"error": "Invalid order_type. Must be 'buy' or 'sell'."}), 400

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    
    # Use parameterized query to prevent SQL injection
    if order_type == 'buy':
        query = "SELECT order_type, price, amount FROM order_book WHERE order_type = 1 ORDER BY price DESC LIMIT 10"
    else:
        query = "SELECT order_type, price, amount FROM order_book WHERE order_type = 2 ORDER BY price ASC LIMIT 10"

    cursor.execute(query)
    
    orders = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return jsonify({"orders": orders})


# 获取K线数据
@app.route('/kline_data')
def get_kline_data():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    
    # 获取交易历史数据
    cursor.execute("SELECT price, timestamp FROM trade_history ORDER BY timestamp ASC")
    trades = cursor.fetchall()
    
    cursor.close()
    connection.close()

    # 生成K线数据
    kline_data = []
    if trades:
        interval = timedelta(hours=1)  # 按小时分割K线
        start_time = trades[0]['timestamp']
        end_time = start_time + interval

        open_price = trades[0]['price']
        high_price = open_price
        low_price = open_price
        close_price = open_price

        for trade in trades:
            if trade['timestamp'] >= end_time:
                kline_data.append({
                    "open": open_price,
                    "close": close_price,
                    "high": high_price,
                    "low": low_price
                })
                start_time = end_time
                end_time = start_time + interval
                open_price = trade['price']
                high_price = open_price
                low_price = open_price

            close_price = trade['price']
            if close_price > high_price:
                high_price = close_price
            if close_price < low_price:
                low_price = close_price

        kline_data.append({
            "open": open_price,
            "close": close_price,
            "high": high_price,
            "low": low_price
        })

    return jsonify(kline_data)


# 生成测试数据的函数
def generate_test_data():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # 清空已有数据
    cursor.execute("DELETE FROM trade_history")
    cursor.execute("DELETE FROM order_book")

    # 生成随机的历史交易数据
    start_time = datetime.now() - timedelta(days=10)
    for _ in range(1000):  # 生成100条数据
        timestamp = start_time + timedelta(minutes=random.randint(1, 1440))
        open_price = random.uniform(100, 200)
        close_price = open_price + random.uniform(-5, 5)
        high_price = max(open_price, close_price) + random.uniform(0, 5)
        low_price = min(open_price, close_price) - random.uniform(0, 5)
        amount = random.uniform(1, 10)

        cursor.execute(
            "INSERT INTO trade_history (user_id, order_type, price, amount, timestamp) VALUES (%s, %s, %s, %s, %s)",
            (111, "buy", close_price, amount, timestamp),
        )

    # TODO: 订单簿厚一点，否则可能被打穿 
    # 生成随机的订单簿数据
    order_types = [1, 2]
    for _ in range(300):
        order_type = random.choice(order_types)
        price = round(random.uniform(10, 100), 2)  # Randomly generate price, rounded to two decimal places
        amount = random.randint(1, 100)  # Randomly generate amount
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = """
        INSERT INTO order_book (order_type, price, amount, timestamp)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (order_type, price, amount, timestamp))
    

    connection.commit()
    cursor.close()
    connection.close()




if __name__ == "__main__":
    generate_test_data()  # 在应用启动时生成测试数据插入数据库
    app.run(debug=True)
