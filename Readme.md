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

​	Create the database and tables:

> see `spot.sql`

5. Configure the application
  Open the app.py file and update the database connection configuration with your own credentials:

  If you are using the default setting of MariaDB ( for example, using WinNMP), there's no need to change it. 

```python
db_config = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'database': 'web_programming'
}
```

6. Generate test data
You can use the build-in function `generate_test_data()` to easily generate some data for testing.

It is automatically enabled before running the server for easier testing: 

in `app.py`, near the end of the file:

```python
if __name__ == "__main__":
    generate_test_data()  
    app.run(debug=True)
```
7. Run the application
You can now start the Flask application:

```bash
python app.py
```
Open your web browser and go to http://127.0.0.1:5000/ to view the website.


#### API Endpoints

##### 1. User Registration

- **URL:** `/register`
- **Method:** `POST`
- **Description:** Registers a new user.

- **Request Parameters:**
  - `username` (string)
  - `password` (string)

- **Response:**
  - On success: Redirects to login.
  - On failure: Error message.
  
  

##### 2. User Login

- **URL:** `/login`
- **Method:** `POST`
- **Description:** Authenticates a user.
- **Request Parameters:**
  - `username` (string)
  - `password` (string)
- **Response:**
  - On success: Redirects to main page.
  - On failure: Error message.



##### 3. Place Order

- **URL:** `/place_order`
- **Method:** `POST`
- **Description:** Places a new buy or sell order.
- **Request Parameters:**
  - `type` (int) - `1` for `buy` and `2` for `sell`
  - `tokenid`(int) - default is `1`
  - `price` (decimal)
  - `amount` (decimal)
- **Response:**
  - On success: JSON with status `success`.
  - On failure: JSON with error message.



##### 4. Get Order Book

- **URL:** `/order_book`
- **Method:** `GET`
- **Description:** Retrieves the current order book.
- **Response:**
  - JSON array of orders.

```bash
curl -X GET "http://127.0.0.1:5000/order_book?type=buy"

curl -X GET "http://127.0.0.1:5000/order_book?type=sell"
```

```bash
{
    "orders": [
        {"token_id":1, "order_type": 1, "price": 150.00, "amount": 10},  
        {"token_id":1, "order_type": 1, "price": 149.50, "amount": 20},
        {"token_id":1, "order_type": 1, "price": 149.00, "amount": 15}
    ]
}

```


##### 5. Get K-Line Data

- **URL:** `/kline_data`
- **Method:** `GET`
- **Description:** Retrieves K-line data based on historical trades.

- **Response:**
  - JSON array of candlestick data with the following fields:
    - `timestamp` (string): The time of the candlestick.
    - `open` (decimal): The opening price.
    - `high` (decimal): The highest price.
    - `low` (decimal): The lowest price.
    - `close` (decimal): The closing price.
    - `volume` (decimal): The traded volume.
    - `turnover` (decimal): The turnover (price * volume).

```bash
curl -X GET http://127.0.0.1:5000/kline_data
```
```bash
[
    {
        "timestamp": "2024-09-01 09:00:00",
        "open": 150.00,
        "high": 155.00,
        "low": 149.00,
        "close": 152.00,
        "volume": 100.5,
        "turnover": 15176.50
    },
    {
        "timestamp": "2024-09-01 10:00:00",
        "open": 152.00,
        "high": 154.50,
        "low": 151.00,
        "close": 153.50,
        "volume": 120.3,
        "turnover": 18456.45
    },
    {
        "timestamp": "2024-09-01 11:00:00",
        "open": 153.50,
        "high": 157.00,
        "low": 152.50,
        "close": 156.00,
        "volume": 95.8,
        "turnover": 14899.60
    }
]
```




#### License

This project is open-source and available under the MIT License.

#### Acknowledgments

Flask framework documentation: Flask
MariaDB documentation: MariaDB