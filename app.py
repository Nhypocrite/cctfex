import decimal
from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from flask_cors import CORS
import mysql.connector
import hashlib
import random
import os
import threading
import time
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# 设置 secret_key，应该是一个随机且安全的字符串，用于 session 加密
app.secret_key = os.urandom(24)# 使用 os.urandom(24) 来生成一个安全的密钥

salt = "NTUSALT1234"

# 配置数据库连接
db_config = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "database": "web_programming",
    "charset":"utf8mb4",
    "collation":"utf8mb4_general_ci"
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
def place_order_handler():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    data = request.json
    token_id = data["token_id"]
    order_type = data["type"]
    price = data["price"]
    amount = data["amount"]
    user_id = session["user_id"]
    err = place_order(token_id, order_type, price, amount, user_id)
    if err:
        return jsonify({"status": "error", "message": err}), 400
    return jsonify({"status": "success"})



# 下单操作的函数
def place_order(token_id, order_type, price, amount, user_id) -> str:
    print("received order:", token_id, order_type, price, amount, user_id)
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # cursor.execute(
    #     "INSERT INTO order_book (token_id, user_id, order_type, price, amount, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
    #     (
    #         token_id,
    #         user_id,
    #         order_type,
    #         price,
    #         amount,
    #         datetime.now(),
    #     ),
    # )
    # connection.commit()

    if order_type == "buy" or order_type == '1': # if the type is 'buy'
            cursor.execute(
                "SELECT id, user_id, price, amount FROM order_book WHERE token_id = %s AND order_type = '2' AND price <= %s ORDER BY price ASC",
                (token_id, price),
            )
    else: # else the type is sell
        cursor.execute(
            "SELECT id, user_id, price, amount FROM order_book WHERE token_id = %s AND order_type = '1' AND price >= %s ORDER BY price DESC",
            (token_id, price),
        )

    matching_orders = cursor.fetchall()

    for match in matching_orders:
        match_id, match_user_id, match_price, match_amount = match

        if amount <= 0:
            break

        trade_amount = min(amount, match_amount)
        amount -= trade_amount

        cursor.execute(
            "INSERT INTO trade_history (token_id, user_id, order_type, price, amount, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                token_id,
                user_id,
                order_type,
                match_price,
                trade_amount,
                datetime.now(),
            ),
        )
        connection.commit()

        if  trade_amount == match_amount:
            cursor.execute("DELETE FROM order_book WHERE id = %s", 
                           (match_id,)
                           )

        else:
            cursor.execute(
                "UPDATE order_book SET amount = amount - %s WHERE id = %s",
                (trade_amount, match_id),
            )
        connection.commit()

    # 如果还有未消耗完的订单，那么插入到订单簿中
    if amount > 0:
        cursor.execute(
            "INSERT INTO order_book (token_id, user_id, order_type, price, amount, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
            (token_id, user_id, order_type, price, amount, datetime.now()),
        )
        connection.commit()

    cursor.close()
    connection.close()
    return ""



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
        query = "SELECT token_id, order_type, price, amount FROM order_book WHERE order_type = 1 and token_id = %s ORDER BY price DESC LIMIT 5"
    else:
        query = "SELECT token_id, order_type, price, amount FROM order_book WHERE order_type = 2 and token_id = %s ORDER BY price ASC LIMIT 5"
    # TODO: 按照价格排序后再给前端送过去？还是让前端自己排序？
    cursor.execute(query, (token_id,))

    orders = cursor.fetchall()
    cursor.close()
    connection.close()

    # TODO: 订单簿按照一个指定宽度来聚合：比如，如果有多个相同价格范围的订单，那么将它们合并成一个条目来显示
    return jsonify({"orders": orders})

# 获取交易历史数据
@app.route("/trade_history", methods=["GET"])
def get_trade_history():
    token_id = int(request.args.get("token_id", 1))  # 可能没有这个参数。如果没有这个参数，那么它就是1
    history_limit = int(request.args.get("limit", 20)) 

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    # 获取交易历史数据
    cursor.execute(
        "SELECT order_type, price, amount, timestamp FROM trade_history where token_id = %s ORDER BY timestamp DESC LIMIT %s",
        (token_id, history_limit,),
    )
    trades = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(trades)


# 获取K线数据
@app.route("/kline_data")
def get_kline_data():
    # TODO: 检查下K线生成逻辑的代码是否正确
    
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    # if not exist, token_id = 1
    try:
        token_id = int(request.args.get("token_id", 1))
    except ValueError:
        token_id = 1

    # get data from how many days before to toady
    try:
        hours = int(request.args.get("hours", 2))
    except ValueError:
        hours = 1

    # 获取交易历史数据
    cursor.execute(
        "SELECT price, amount, timestamp FROM trade_history where token_id = %s and timestamp > NOW() - INTERVAL %s HOUR ORDER BY timestamp ASC",
        (token_id, hours),
    )
    trades = cursor.fetchall()

    cursor.close()
    connection.close()

    # 生成K线数据
    kline_data = []
    if trades:
        # 开始第一条K线
        start_time = trades[0]["timestamp"].replace(second=0, microsecond=0)
        interval = timedelta(minutes=1)  # 按分钟分割K线

        end_time = start_time + interval

        open_price = trades[0]["price"]
        high_price = open_price
        low_price = open_price
        close_price = open_price
        volume = 0
        turnover = 0

        for trade in trades:
            if trade["timestamp"] >= end_time:  # 开始新的K线
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
                open_price = close_price    # 开盘价是上一个K线的收盘价
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


# 触发重新生成测试数据
@app.route("/refresh_test_data")
def refresh_test_data():
    generate_test_data()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({
        "message": "Test data successfully refreshed!",
        "updated_at": current_time,
        "refresh_details": {
            "trade_history": "4000 trades added (in the past 1000 min, interval ~15s)",
            "order_book": "top 200 buy/sell orders updated"
        },
    })


# 生成测试数据的函数
def generate_test_data():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # 清空已有数据
    cursor.execute("TRUNCATE TABLE trade_history")
    cursor.execute("TRUNCATE TABLE order_book")

    order_types = [1, 2]  # 1: buy, 2: sell
    price_initlial = random.uniform(49000, 71000)
    price_previous = price_initlial

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
    price_previous = price_initlial
    timestamp = datetime.now()

    for _ in range(4000):  # 生成数据
        timestamp = timestamp - timedelta(seconds=random.randint(5, 25))  # 倒着生成
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


# 实时生成新的订单的函数
def generate_order(rate=0.2):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    while True:
        cursor.execute("SELECT id, price FROM order_book ORDER BY timestamp DESC LIMIT 1",)
        last_order = cursor.fetchone()
        if last_order:
            price_previous = last_order[1]
        else:
            price_previous = random.uniform(49000, 71000)

        # 生成随机的订单簿数据
        user_id = random.randint(1, 999)
        order_type = random.choice([1, 2])  # 1: buy, 2: sell
        price = round(decimal.Decimal(price_previous) + decimal.Decimal(random.uniform(-100, 100)), 2)
        amount = round(decimal.Decimal(random.uniform(0.1, 10)), 2)
        place_order(1, order_type, price, amount, user_id)

        # 更新前一次价格为当前价格，模拟市场变化
        price_previous = price

        # 按照速率暂停（rate秒）
        time.sleep(rate)



if __name__ == "__main__":

    # # 在应用启动时生成测试数据插入数据库
    # generate_test_data()  

    # # 暂时在外部手动执行，并行有点问题
    # # 启动生成订单的线程，速率为每0.2秒生成一条订单
    # order_thread = threading.Thread(target=generate_order, args=(1,))
    # order_thread.daemon = True  # 守护线程，主程序退出时自动终止
    # order_thread.start()

    app.run(debug=False, use_reloader=False)
