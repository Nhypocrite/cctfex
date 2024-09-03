document.addEventListener("DOMContentLoaded", function() {
    loadOrderBook();
    loadKlineData();
});

function loadOrderBook() {
    fetch('/order_book')
        .then(response => response.json())
        .then(data => {
            const orderBookTable = document.getElementById('orderBookTable');
            orderBookTable.innerHTML = '';
            data.orders.forEach(order => {
                let row = document.createElement('tr');
                row.innerHTML = `<td>${order.order_type.toUpperCase()}</td><td>${order.price}</td><td>${order.amount}</td>`;
                orderBookTable.appendChild(row);
            });
        });
}

function loadKlineData() {
    fetch('/kline_data')
        .then(response => response.json())
        .then(data => {
            drawKlineChart(data);
        });
}

function drawKlineChart(data) {
    const canvas = document.getElementById('klineCanvas');
    const ctx = canvas.getContext('2d');

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const maxPrice = Math.max(...data.map(d => d.high));
    const minPrice = Math.min(...data.map(d => d.low));
    const priceRange = maxPrice - minPrice;

    const candleWidth = canvas.width / data.length;

    data.forEach((candle, index) => {
        const x = index * candleWidth;
        const candleHeight = (candle.close - candle.open) / priceRange * canvas.height;
        const y = canvas.height - (candle.close - minPrice) / priceRange * canvas.height;

        ctx.beginPath();
        ctx.moveTo(x + candleWidth / 2, canvas.height - (candle.high - minPrice) / priceRange * canvas.height);
        ctx.lineTo(x + candleWidth / 2, canvas.height - (candle.low - minPrice) / priceRange * canvas.height);
        ctx.stroke();

        ctx.fillStyle = candle.close > candle.open ? 'green' : 'red';
        ctx.fillRect(x, y, candleWidth, candleHeight);
    });
}

function placeOrder() {
    const orderType = document.getElementById('orderType').value;
    const price = document.getElementById('price').value;
    const amount = document.getElementById('amount').value;

    fetch('/place_order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            type: orderType,
            price: price,
            amount: amount,
        }),
    })
    .then(response => response.json())
    .then(data => {
        loadOrderBook();
    });
}
