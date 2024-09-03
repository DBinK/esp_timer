import machine

rtc = machine.RTC()

print(rtc.datetime())

# 导入相关模块
from machine import Pin, SoftI2C, RTC
import time
import socket
import struct

# 构建RTC对象
rtc = RTC()

# NTP服务器地址
NTP_SERVER = "pool.ntp.org"

def get_ntp_time():
    # 创建UDP socket
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(1)  # 设置超时时间为1秒

    # NTP请求数据
    ntp_request = b'\x1b' + 47 * b'\0'
    
    try:
        # 发送请求
        client.sendto(ntp_request, (NTP_SERVER, 123))
        # 接收响应
        response, _ = client.recvfrom(48)
        
        # 解析时间戳
        timestamp = struct.unpack('!I', response[40:44])[0]
        # 转换为UTC时间
        return time.localtime(timestamp - 2208988800)  # NTP时间戳转换为Unix时间戳
    except Exception as e:
        print("获取NTP时间失败:", e)
        return None
    finally:
        client.close()

# 首次上电配置时间，按顺序分别是：年，月，日，星期，时，分，秒，次秒级
if rtc.datetime()[0] != 2024:
    ntp_time = get_ntp_time()
    if ntp_time:
        rtc.datetime((ntp_time[0], ntp_time[1], ntp_time[2], ntp_time[6], ntp_time[3], ntp_time[4], ntp_time[5], 0))
    else:
        rtc.datetime((2024, 1, 1, 0, 0, 0, 0, 0))  # 如果获取失败，使用默认时间

while True:
    print(rtc.datetime())  # 打印时间
    time.sleep(1)  # 延时1秒