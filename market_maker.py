import app

if __name__ == '__main__':
    # 在应用启动时生成测试数据插入数据库
    app.generate_test_data()  

    # 生成订单
    app.generate_order(0.2)

