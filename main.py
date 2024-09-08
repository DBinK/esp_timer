import time
from machine import Pin, SoftI2C, RTC, Timer
from ssd1306 import SSD1306_I2C

class CountdownTimer:
    def __init__(self, scl_pin, sda_pin, key_pin, countdown_interval=5):
        self.rtc = RTC()
        self.i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.oled = SSD1306_I2C(width=128, height=64, i2c=self.i2c)

        self.cntdown_on = False
        self.keypass_cnt = 0
        self.countdown_interval = countdown_interval
        self.start_time = 0

        self.KEY = Pin(key_pin, Pin.IN, Pin.PULL_UP)
        self.KEY.irq(self.init_timer, Pin.IRQ_FALLING)  # 定义中断，下降沿触发
        
        self.timer = Timer(0)  # 定义定时器
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=self.main)

    def init_timer(self, key_callback):
        time.sleep_ms(50)  # 消除抖动
        if self.KEY.value() == 0:  # 确认按键被按下
            self.keypass_cnt += 1 
            if self.cntdown_on:
                self.start_time = time.time() + (self.countdown_interval * self.keypass_cnt)
            else:
                self.cntdown_on = True
                self.start_time = time.time()

    def main(self, timer_callback):
        self.oled.fill(0)  # 清屏
        
        date_time = self.rtc.datetime()
        date_str = f'{date_time[1]:02}.{date_time[2]:02}'  # mm:dd
        time_str = f'{date_time[4]:02}:{date_time[5]:02}:{date_time[6]:02}'  # hh:mm:ss
        date_time_str = f'{date_str} {time_str}'

        print(date_time_str)
        
        self.oled.text('TEST', 10, 10)
        self.oled.text(date_time_str, 10, 25)
        self.oled.block(1, 1, 128, 64)  # UI 矩形屏幕边框

        if self.cntdown_on:
            pass_time = time.time() - self.start_time
            self.oled.text(f'cnt {self.countdown_interval - pass_time:.1f} s', 10, 45)

            if pass_time >= self.countdown_interval:
                self.cntdown_on = False
                self.keypass_cnt = 0 

            print(f"倒计时 {pass_time:.1f} s")
        
        self.oled.show()

# 使用示例
countdown_timer = CountdownTimer(scl_pin=1, sda_pin=0, key_pin=9, countdown_interval=5)