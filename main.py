import time
from machine import Pin, SoftI2C, RTC, Timer
from libs.ssd1306 import SSD1306_I2C

# 初始化各个对象
rtc = RTC()
i2c = SoftI2C(scl=Pin(1), sda=Pin(0))
oled = SSD1306_I2C(width=128, height=64, i2c=i2c)

# 清屏
oled.fill(0)

# 定义定时器中断的回调函数
def main(timer_callback):
    
    oled.fill(0) # 清屏
    
    date_time = rtc.datetime()
    
    # 设置时间和日期的格式s
    time_str = f'{date_time[1]:02}.{date_time[2]:02}'  # mm:dd
    date_str = f'{date_time[4]:02}:{date_time[5]:02}:{date_time[6]:02}' # hh:mm:ss

    print(time_str)
    
    oled.text(time_str, 10, 10)
    oled.text(date_str, 10, 25)

    oled.block(1, 1, 128, 64)  # UI 矩形屏幕边框
    
    oled.show()

# 定义定时器
timer = Timer(0)
timer.init(period=1000, mode=Timer.PERIODIC, callback=main)