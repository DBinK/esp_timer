import time
from machine import Pin, SoftI2C, RTC, Timer
from ssd1306 import SSD1306_I2C


class CountdownTimer:
    def __init__(self, scl_pin, sda_pin):
        self.rtc = RTC()
        self.i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.oled = SSD1306_I2C(width=128, height=64, i2c=self.i2c)
        self.led = Pin(8, Pin.OUT)

        self.cntdown_on = False
        self.keypass_cnt = 0
        self.cntdown_interval = 5  # * 60
        self.target_time = 0
        self.cntdown_time = 0
        self.start_time = 0
        self.cntdown_period_add = 0
        self.cntdown_period_now = 0

        self.r_key = Pin(1, Pin.IN, Pin.PULL_UP)
        self.r_key.irq(self.r_key_passed, Pin.IRQ_FALLING) 

        self.l_key = Pin(0, Pin.IN, Pin.PULL_UP)
        self.l_key.irq(self.l_key_passed, Pin.IRQ_FALLING) 

        self.timer = Timer(0)  # 定义定时器
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=self.main)
    
    def r_key_passed(self, key_callback):
        time.sleep_ms(100)          # 消除抖动
        if self.r_key.value() == 0:   # 确认按键被按下
            self.cntdown_on = False
            self.keypass_cnt = 0

    def l_key_passed(self, key_callback):
        time.sleep_ms(100)          # 消除抖动
        if self.l_key.value() == 0:   # 确认按键被按下
            self.keypass_cnt += 1
            self.cntdown_period_add = self.cntdown_interval * self.keypass_cnt

            if not self.cntdown_on:
                self.cntdown_on = True
                self.start_time = time.time()
                self.target_time = self.start_time + self.cntdown_period_add
                self.cntdown_period_now = self.target_time - time.time()
            else:
                self.target_time = self.start_time + self.cntdown_period_add
                self.cntdown_period_now = self.target_time - time.time()

    def main(self, timer_callback):
        self.oled.fill(0)

        date_time = self.rtc.datetime()
        date_str = f"{date_time[1]:02}.{date_time[2]:02}"  # mm:dd
        time_str = f"{date_time[4]:02}:{date_time[5]:02}:{date_time[6]:02}"  # hh:mm:ss
        date_time_str = f"{date_str} {time_str}"

        print(date_time_str)

        self.oled.text("Date: Time:", 10, 10)
        self.oled.text(date_time_str, 10, 25)
        self.oled.block(0, 0, 128, 64) 

        if self.cntdown_on:

            self.cntdown_time = self.target_time - time.time()
            self.oled.text(f"cnt {self.cntdown_time} s", 10, 45)

            rate = self.cntdown_time / self.cntdown_period_now
            self.oled.block(0, 56, int(128 * (rate)), 64, fill=True)

            if self.cntdown_time <= 0:
                self.oled.fill(0)
                self.oled.show()
                self.led.value(0)

                time.sleep(0.3)

                self.oled.fill(1)
                self.oled.text(f"cnt {self.cntdown_time} s", 10, 45, 0)
                self.oled.show()
                self.led.value(1)

            if self.cntdown_time <= -15:
                self.cntdown_on = False
                self.keypass_cnt = 0

                self.led.value(0)

            print(f"倒计时 {self.cntdown_time:.1f} s")

        self.oled.show()


# 使用示例
countdown_timer = CountdownTimer(scl_pin=4, sda_pin=3)
