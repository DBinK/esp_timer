import time
import network # type: ignore
import ntptime # type: ignore
from machine import Pin, RTC # type: ignore

LED = Pin(8, Pin.OUT)  # 构建led对象
LED.value(0)           # 点亮LED

wlan = network.WLAN(network.STA_IF)  # STA模式

# WIFI连接函数
def WIFI_Connect():
    wlan.active(True)         # 激活接口
    start_time = time.time()  # 记录时间做超时判断

    if not wlan.isconnected():
        print('connecting to network...')
        # print(wlan.scan())
        
        try:
            # wlan.connect('ovo', '00000000')  # 输入WIFI账号密码
            wlan.connect('WX264', '00000000')  # 输入WIFI账号密码
            # wlan.connect('DT46', '12345678')  # 输入WIFI账号密码

        except Exception as e:
            print(f'错误 Exception：{e}')

        while not wlan.isconnected():

            # 超时判断, 15秒没连接成功判定为超时
            if time.time() - start_time > 9:
                #LED.value(1)
                print('WIFI Connected Timeout!')
                break

            # LED闪烁提示
            LED.value(0)
            time.sleep_ms(500)
            LED.value(1)
            time.sleep_ms(500)

    if wlan.isconnected():
        # 串口打印信息
        print('network information:', wlan.ifconfig())
        
        # 同步时间
        try:
            time.sleep(1)
            ntptime.host = 'ntp.aliyun.com'
            ntptime.settime()
        except OSError as e:
            print('NTP time sync failed:', e)
        
        # 获取当前UTC时间
        utc_time = time.localtime()
        print("UTC时间:", utc_time)

        # 计算并更新北京时间（UTC+8） 到 RTC
        rtc = RTC()
        rtc.datetime((utc_time[0], utc_time[1], utc_time[2], utc_time[6], utc_time[3] + 8, utc_time[4], utc_time[5], 0))
        
        print("rtc 北京时间:", rtc.datetime())

def Is_Connected():
    return wlan.isconnected()


if __name__ == '__main__':
    WIFI_Connect()