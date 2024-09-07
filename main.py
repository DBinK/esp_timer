import time
from machine import Pin, SoftI2C, RTC, Timer
from libs.ssd1306 import SSD1306_I2C

# 初始化各个对象
rtc = RTC()
i2c = SoftI2C(scl=Pin(1), sda=Pin(0))
oled = SSD1306_I2C(width=128, height=64, i2c=i2c)

KEY = Pin(9, Pin.IN, Pin.PULL_UP)  # 构建KEY对象

init_s = 0
cnt_s  = 0

def init_time(KEY_callback):
    global init_s, cnt_s
    time.sleep_ms(10)  # 消除抖动
    if KEY.value() == 0:  # 确认按键被按下
        init_s += 5  # 增加5秒
        cnt_s   = time.time()
# 定义定时器中断的回调函数
def main(timer_callback):
    global init_s, cnt_s
    
    oled.fill(0)  # 清屏
    
    date_time = rtc.datetime()
    
    # 设置时间和日期的格式
    date_str = f'{date_time[1]:02}.{date_time[2]:02}'  # mm:dd
    time_str = f'{date_time[4]:02}:{date_time[5]:02}:{date_time[6]:02}'  # hh:mm:ss

    print(time_str)
    
    oled.text(date_str, 10, 10)
    oled.text(time_str, 10, 25)

    oled.block(1, 1, 128, 64)  # UI 矩形屏幕边框

    cnt = (init_s + cnt_s) - time.time()

    if cnt < 0:
        oled.text(f'times up {cnt} s', 10, 40)
        print("时间到")
    elif cnt > 0:
        oled.text(f'cnt down {cnt} s', 10, 40)
    
    print(f"倒计时 {cnt} s")
    
    oled.show()

KEY.irq(init_time, Pin.IRQ_FALLING)  # 定义中断，下降沿触发

timer = Timer(0)  # 定义定时器
timer.init(period=1000, mode=Timer.PERIODIC, callback=main)