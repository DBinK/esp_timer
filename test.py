import serial
import time

def serial_speed_test(port, baudrate=115200, num_iterations=1000):
    # 打开串口
    ser = serial.Serial(port, baudrate, timeout=1)
    
    # 等待串口准备好
    time.sleep(2)
    
    # 发送和接收数据
    start_time = time.time()
    for i in range(num_iterations):
        # 发送数据
        ser.write(b'U')
        ser.flush()
        
        # 等待接收数据
        while ser.in_waiting <= 0:
            pass
        
        # 读取返回的数据
        received = ser.read(1)
        if received != b'U':
            print(f"错误: 接收到的数据为 {received}")
    
    end_time = time.time()
    ser.close()
    
    # 计算速率
    elapsed_time = end_time - start_time
    speed = num_iterations / elapsed_time  # 每秒发送的次数
    print(f"测试完成: 发送 {num_iterations} 次，耗时 {elapsed_time:.3f} 秒，速率 {speed:.2f} 次/秒")

# 调用函数进行测试
serial_speed_test('COM170', 115200)