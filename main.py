import time

from machine import Pin, SoftI2C, RTC, Timer
from ssd1306 import SSD1306_I2C

# 初始化各个对象
rtc = RTC()
i2c = SoftI2C(scl=Pin(1), sda=Pin(0))
oled = SSD1306_I2C(width=128, height=64, i2c=i2c)
KEY = Pin(9, Pin.IN, Pin.PULL_UP)  # 构建KEY对象

cntdown_on = 0        # 倒计时启动标志
keypass_cnt = 0
cntdown_interval = 5  # 倒计时的间隔时间单位 s

def init_time(KEY_callback):
    global cntdown_on, start_time, keypass_cnt
    time.sleep_ms(100)  # 消除抖动
    if KEY.value() == 0:  # 确认按键被按下

        keypass_cnt += 1 

        if cntdown_on:
            start_time  = time.time() + (cntdown_interval * keypass_cnt)
        else:
            cntdown_on = True
            start_time  = time.time()

# 定义定时器中断的回调函数
def main(timer_callback):
    global cntdown_on, start_time, cntdown_interval, keypass_cnt
    
    oled.fill(0)  # 清屏
    
    date_time = rtc.datetime()
    
    # 设置时间和日期的格式
    date_str = f'{date_time[1]:02}.{date_time[2]:02}'  # mm:dd
    time_str = f'{date_time[4]:02}:{date_time[5]:02}:{date_time[6]:02}'  # hh:mm:ss
    
    date_time_str = f'{date_str} {time_str}'  # 

    print(date_time_str)
    
    oled.text('TEST', 10, 10)
    oled.text(date_time_str, 10, 25)

    oled.block(1, 1, 128, 64)  # UI 矩形屏幕边框

    if cntdown_on:
        pass_time = time.time() - start_time

        oled.text(f'cnt {cntdown_interval - pass_time} s', 10, 45)

        if pass_time >= cntdown_interval:
            cntdown_on  = False
            keypass_cnt = 0 
    
        print(f"倒计时 {pass_time} s")
    
    oled.show()

KEY.irq(init_time, Pin.IRQ_FALLING)  # 定义中断，下降沿触发

timer = Timer(0)  # 定义定时器
timer.init(period=1000, mode=Timer.PERIODIC, callback=main)