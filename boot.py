# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import network, time, ntptime
from machine import Pin, RTC

# 释放所有GPIO, 断电重上电不再失控
def release_all_GPIO():
    for i in range(0, 48):
        try:
            GND = Pin(i, Pin.OUT, value=0)
            print(f"releasing gpio {i}")
        except:
            print(f"skip gpio {i}")
            continue

release_all_GPIO()

LED = Pin(8, Pin.OUT)  # 构建led对象
LED.value(1)  # 点亮LED，也可以使用led.on()

# WIFI连接函数
def WIFI_Connect():
    wlan = network.WLAN(network.STA_IF)  # STA模式
    wlan.active(True)  # 激活接口
    start_time = time.time()  # 记录时间做超时判断

    if not wlan.isconnected():
        print('connecting to network...')
        
        try:
            # wlan.connect('ovo', '00000000')  # 输入WIFI账号密码
            wlan.connect('DT46', '12345678')  # 输入WIFI账号密码
        except:
            print('WIFI Connect Failed!')

        while not wlan.isconnected():
            # LED闪烁提示
            LED.value(1)
            time.sleep_ms(300)
            LED.value(0)
            time.sleep_ms(300)

            # 超时判断, 15秒没连接成功判定为超时
            if time.time() - start_time > 15:
                LED.value(0)
                print('WIFI Connected Timeout!')
                break

    if wlan.isconnected():
        # LED点亮
        LED.value(1)

        # 串口打印信息
        print('network information:', wlan.ifconfig())

        # 同步时间
        time.sleep(1)
        ntptime.settime()
        
        # 获取当前UTC时间
        utc_time = time.localtime()
        print("UTC时间:", utc_time)

        # 计算并打印北京时间（UTC+8）
        beijing_time = time.localtime(time.mktime(utc_time) + 8 * 3600)
        
        # 创建 RTC 对象
        rtc = RTC()
        rtc.datetime(beijing_time)
        
        print("北京时间:", rtc.datetime())

# 执行WIFI连接函数
WIFI_Connect()