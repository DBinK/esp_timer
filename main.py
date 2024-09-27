import time
from machine import Pin, SoftI2C, RTC, Timer # type: ignore

import wifi
from ssd1306 import SSD1306_I2C

def debounce(delay_ns):
    """装饰器: 防止函数在指定时间内被重复调用"""
    def decorator(func):
        last_call_time = 0
        result = None
        def wrapper(*args, **kwargs):
            nonlocal last_call_time, result
            current_time = time.time_ns()
            if current_time - last_call_time > delay_ns:
                last_call_time = current_time
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

class CountdownTimer:
    def __init__(self):

        # 初始化各种对象
        self.rtc = RTC()
        self.i2c = SoftI2C(scl=Pin(4), sda=Pin(10))
        self.oled = SSD1306_I2C(width=128, height=64, i2c=self.i2c)
        self.led = Pin(8, Pin.OUT)

        # 初始化变量
        self.oled_on = True
        self.cntdown_on = False
        self.keypass_cnt = 0
        self.cntdown_interval = 5 * 60  # 单个定时周期
        self.target_time = 0
        self.cntdown_time = 0
        self.start_time = 0
        self.cntdown_period_now = 0

        # 按键&定时器初始化
        self.l_key = Pin(5, Pin.IN, Pin.PULL_UP)
        self.l_key.irq(self.l_key_passed, Pin.IRQ_FALLING) 

        self.r_key = Pin(7, Pin.IN, Pin.PULL_UP)
        self.r_key.irq(self.r_key_passed, Pin.IRQ_FALLING) 

        self.m_key = Pin(6, Pin.IN, Pin.PULL_UP)
        self.m_key.irq(self.m_key_passed, Pin.IRQ_FALLING) 

        self.timer = Timer(0)  # 定义定时器
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=self.main)
        
        # 初始化屏幕
        self.oled.fill(1)
        self.oled.text("Wellcome", 0, 30, 0, scale=2) 
        self.oled.show()
        wifi.wifi_connect()
        time.sleep(1)
        
    @debounce(150_000_000)  # 设置ns内不重复执行
    def m_key_passed(self, key_callback):
        # time.sleep_ms(100)            # 消除抖动
        if self.m_key.value() == 0:  # 确认按键被按下
            self.oled_on = not self.oled_on
            print(f"oled_on: {self.oled_on}")

    @debounce(150_000_000)  # 设置ns内不重复执行
    def l_key_passed(self, key_callback):
        # time.sleep_ms(100)            # 消除抖动
        if self.l_key.value() == 0:     # 确认按键被按下
            self.cntdown_on = False
            self.keypass_cnt = 0

    @debounce(150_000_000)  # 设置ns内不重复执行
    def r_key_passed(self, key_callback):
        # time.sleep_ms(100)            # 消除抖动
        if self.r_key.value() == 0:     # 确认按键被按下

            self.keypass_cnt += 1

            if self.l_key.value() == 0:
                cntdown_period_add = 60 * self.keypass_cnt
            else:
                cntdown_period_add = self.cntdown_interval * self.keypass_cnt

            if not self.cntdown_on:
                self.cntdown_on = True
                self.start_time = time.time()
                self.target_time = self.start_time + cntdown_period_add
                self.cntdown_period_now = self.target_time - time.time()
            else:
                self.target_time = self.start_time + cntdown_period_add
                self.cntdown_period_now = self.target_time - time.time()

    def main(self, timer_callback):

        week_list = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        self.oled.fill(0)

        date_time = self.rtc.datetime()

        date_str   = f"{date_time[1]:02}.{date_time[2]:02}"  # mm:dd:week
        time_str   = f"{date_time[4]:02}:{date_time[5]:02}"  # hh:mm
        second_str = f"{date_time[6]:02}" # ss
        week_str   = f"{week_list[date_time[3]]}"

        date_time_second_str = f"{date_str} {time_str}:{second_str}"

        print(date_time_second_str)

        if date_time[6] == 0: # 整分报时
            wifi.blink_led()

        if self.oled_on:

            self.oled.block(0, 0, 44, 14, fill=True)    # 日期背景
            self.oled.text(date_str, 1, 3, col=0)         # 显示日期

            self.oled.block(128-44, 0, 128, 14, fill=True)    # 星期背景
            self.oled.text(week_str, 128-44+10, 3, col=0)

            self.oled.text(time_str, 4, 25, scale=3)      # 显示时间
            self.oled.text(second_str, 55, 4, scale=1)      # 显示秒数
            self.oled.block(0, 0, 128, 64) 

        if self.cntdown_on:

            self.cntdown_time = self.target_time - time.time()
            rate = self.cntdown_time / self.cntdown_period_now

            if self.cntdown_time < 1000:
                self.oled.block(0, 64-9, int(100 * (rate)), 64, fill=True)       # 进度条
                self.oled.text(f"{self.cntdown_time}", int(100 * (rate))+2, 55)  # 倒计时
            else:
                self.oled.block(0, 64-9, int(90 * (rate)), 64, fill=True)       # 进度条
                self.oled.text(f"{self.cntdown_time}", int(90 * (rate))+2, 55)  # 倒计时


            if self.cntdown_time < 0:
                self.oled.fill(0)
                self.oled.show()
                self.led.value(0)

                time.sleep(0.3)

                self.oled.fill(1)
                self.oled.text(f"{self.cntdown_time}", 17, 20, 0, scale=4)  # 倒计时结束
                self.oled.show()
                self.led.value(1)

            if self.cntdown_time <= -60*3:
                self.cntdown_on = False
                self.keypass_cnt = 0

                self.led.value(0)

            print(f"倒计时 {self.cntdown_time:.1f} s")

        self.oled.show()

if __name__ == "__main__":
    countdown_timer = CountdownTimer()
