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
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


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
                (
                    username,
                    encrypted_password,
                ),
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
        cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
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
    token_id = data["token_id"]
    order_type = data["type"]
    price = data["price"]
    amount = data["amount"]
    user_id = session["user_id"]

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # TODO: 写一下撮合交易的逻辑
    cursor.execute(
        "INSERT INTO order_book (token_id, user_id, order_type, price, amount) VALUES (%s, %s, %s, %s, %s)",
        (
            token_id,
            user_id,
            order_type,
            price,
            amount,
        ),
    )
    connection.commit()

    cursor.execute(
        "INSERT INTO trade_history (token_id, user_id, order_type, price, amount) VALUES (%s, %s, %s, %s, %s)",
        (
            token_id,
            user_id,
            order_type,
            price,
            amount,
        ),
    )
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"status": "success"})


# 获取订单簿数据
@app.route("/order_book", methods=["GET"])
def get_order_book():
    order_type = request.args.get("type", "").lower()

    # Validate order_type to be either 'buy' or 'sell'
    if order_type not in ["buy", "sell"]:
        return jsonify({"error": "Invalid order_type. Must be 'buy' or 'sell'."}), 400

    token_id = int(request.args.get("token_id", 1))  # 可能没有这个参数。如果没有这个参数，那么它就是1

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    # Use parameterized query to prevent SQL injection
    if order_type == "buy":
        query = "SELECT token_id, order_type, price, amount FROM order_book WHERE order_type = 1 ORDER BY price DESC LIMIT 20"
    else:
        query = "SELECT token_id, order_type, price, amount FROM order_book WHERE order_type = 2 ORDER BY price ASC LIMIT 20"
    # TODO: 按照价格排序后再给前端送过去？还是让前端自己排序？
    cursor.execute(query)

    orders = cursor.fetchall()
    cursor.close()
    connection.close()

    # TODO: 订单簿按照一个指定宽度来聚合：比如，如果有多个相同价格范围的订单，那么将它们合并成一个条目来显示
    return jsonify({"orders": orders})


# 获取K线数据
@app.route("/kline_data")
def get_kline_data():
    # TODO: 检查下K线生成逻辑的代码是否正确
    # TODO: 检查下是不是没有的交易数据的时候也正常生成了K线
    # TODO: 看看请求中要不要加上时间范围，在sql中补充上
    # TODO: sql注入攻击的预防
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    # token_id = int(request.args.get("token_id", 1))  # 可能没有这个参数。如果没有这个参数，那么它就是1
    token_id = 1

    # 获取交易历史数据
    cursor.execute(
        "SELECT price, amount, timestamp FROM trade_history where token_id = %s and timestamp > NOW() - INTERVAL 1 DAY ORDER BY timestamp ASC",
        (token_id,),
    )
    trades = cursor.fetchall()

    cursor.close()
    connection.close()

    # 生成K线数据
    kline_data = []
    if trades:
        interval = timedelta(minutes=1)  # 按分钟分割K线
        start_time = trades[0]["timestamp"]
        end_time = start_time + interval

        open_price = trades[0]["price"]
        high_price = open_price
        low_price = open_price
        close_price = open_price
        volume = 0
        turnover = 0

        for trade in trades:
            if trade["timestamp"] >= end_time:  # 新的K线
                kline_data.append(
                    {
                        "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": open_price,
                        "close": close_price,
                        "high": high_price,
                        "low": low_price,
                        "volume": volume,
                        "turnover": turnover,
                    }
                )
                start_time = end_time
                end_time = start_time + interval
                open_price = trade["price"]
                high_price = open_price
                low_price = open_price
                volume = 0
                turnover = 0

            close_price = trade["price"]
            if close_price > high_price:
                high_price = close_price
            if close_price < low_price:
                low_price = close_price
            volume += trade["amount"]
            turnover += trade["price"] * trade["amount"]

        kline_data.append(
            {
                "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "open": open_price,
                "close": close_price,
                "high": high_price,
                "low": low_price,
                "volume": volume,
                "turnover": turnover,
            }
        )

    return jsonify(kline_data)


# 生成测试数据的函数
def generate_test_data():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # 清空已有数据
    cursor.execute("TRUNCATE TABLE trade_history")
    cursor.execute("TRUNCATE TABLE order_book")

    order_types = [1, 2]  # 1: buy, 2: sell
    price_previous = random.uniform(49000, 71000)

    # 生成随机的订单簿数据
    for _ in range(100):
        # 买单
        order_type = 1
        price = price_previous - round(random.uniform(10, 1000), 2)
        amount = random.uniform(0.1, 10)  # Randomly generate amount
        timestamp = datetime.now() - timedelta(seconds=random.randint(1, 1000))  # 倒着生成
        query = """
        INSERT INTO order_book (token_id, user_id, order_type, price, amount, timestamp)
        VALUES (%s,%s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                1,
                111,
                order_type,
                price,
                amount,
                timestamp,
            ),
        )

        # 卖单
        order_type = 2
        price = price_previous + round(random.uniform(10, 1000), 2)
        amount = random.uniform(0.1, 10)
        timestamp = datetime.now() - timedelta(seconds=random.randint(1, 1000))
        query = """
        INSERT INTO order_book (token_id, user_id, order_type, price, amount, timestamp)
        VALUES (%s,%s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                1,
                111,
                order_type,
                price,
                amount,
                timestamp,
            ),
        )
        # TODO: 非重要优化：插入数据时，多条数据一起插入而不是一条一条插入

    # 生成随机的历史交易数据
    timestamp = datetime.now()

    for _ in range(2000):  # 生成数据
        timestamp = timestamp - timedelta(seconds=random.randint(10, 60))  # 倒着生成
        price_then = price_previous + random.uniform(-50, 50)
        # high_price = max(open_price, close_price) + random.uniform(0, 5)
        # low_price = min(open_price, close_price) - random.uniform(0, 5)
        amount = random.uniform(0.1, 10)
        order_type = random.choice(order_types)

        cursor.execute(
            "INSERT INTO trade_history (token_id, user_id, order_type, price, amount, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                1,
                2049,
                order_type,
                price_then,
                amount,
                timestamp,
            ),
        )
        price_previous = price_then

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    generate_test_data()  # 在应用启动时生成测试数据插入数据库
    app.run(debug=True)
