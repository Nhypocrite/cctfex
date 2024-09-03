# Cryptocurrency Trading Website

This is a simple stock trading website built with Flask and MySQL (MariaDB). The website allows users to register, log in, place buy and sell orders, and view a K-line (candlestick) chart based on historical trade data.

#### Features

- User registration and login

- Place buy and sell orders
- View order book
- View K-line chart based on historical trade data
- Simple frontend using HTML, CSS, and JavaScript

#### Available API Endpoint

For testing purposes, you can use the following API endpoint:

`https://intis.top/cctfex/`

#### Prerequisites

1. Before you begin, ensure you have met the following requirements:

- Python 3.x installed on your machine

- MariaDB (or MySQL) installed and running
- Git installed

2. Set up the virtual environment (**optional** but recommended)
You can create a virtual environment to manage dependencies:

```bash
python -m venv venv-cctfex

# On Windows, run:
venv-cctfex\Scripts\activate
# On Unix or MacOS, run:
source venv-cctfex/bin/activate

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
        {
            "amount": "2.87",
            "order_type": 1,
            "price": "51814.29",
            "token_id": 1
        },
        {
            "amount": "4.13",
            "order_type": 1,
            "price": "51806.58",
            "token_id": 1
        },
        {
            "amount": "3.42",
            "order_type": 1,
            "price": "51756.91",
            "token_id": 1
        },
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
        "close": "60145.54",
        "high": "60145.54",
        "low": "60106.72",
        "open": "60106.72",
        "timestamp": "2024-09-03 06:26:49",
        "turnover": "200275.3314",
        "volume": "3.33"
    },
    {
        "close": "60112.71",
        "high": "60133.74",
        "low": "60112.71",
        "open": "60133.74",
        "timestamp": "2024-09-03 06:27:49",
        "turnover": "560429.2122",
        "volume": "9.32"
    },
    {
        "close": "60073.11",
        "high": "60073.11",
        "low": "60073.11",
        "open": "60073.11",
        "timestamp": "2024-09-03 06:28:49",
        "turnover": "310577.9787",
        "volume": "5.17"
    },
]
```




#### License

This project is open-source and available under the MIT License.

#### Acknowledgments

Flask framework documentation: Flask
MariaDB documentation: MariaDB