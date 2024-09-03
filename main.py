from machine import Pin, Timer
import time

LED = Pin(8, Pin.OUT)  # 构建LED对象
KEY = Pin(9, Pin.IN, Pin.PULL_UP)  # 构建KEY对象
state = 0  # LED引脚状态
timer_duration = 0  # 计时器持续时间
timer = Timer(0)  # 创建定时器对象

# LED状态翻转函数
def fun(KEY):
    global state, timer_duration
    time.sleep_ms(10)  # 消除抖动
    if KEY.value() == 0:  # 确认按键被按下
        timer_duration += 5  # 每次按键增加5秒
        print("按键按下，计时器增加5秒")
        if timer_duration > 0:
            timer.init(period=1000, mode=Timer.PERIODIC, callback=led_blink)  # 启动定时器

# LED闪烁函数
def led_blink(timer):
    global state, timer_duration
    if timer_duration > 0:
        LED.value(state)  # 切换LED状态
        state = not state  # 翻转状态
        timer_duration -= 1  # 每秒减少计时
        print("倒计时:", timer_duration, "秒")
    else:
        timer.deinit()  # 停止定时器
        print("计时结束！")
        fast_blink()  # 时间到后快速闪烁

# 快速闪烁函数
def fast_blink():
    global state
    while True:
        LED.value(1)  # LED亮
        time.sleep(0.1)  # 等待0.1秒
        LED.value(0)  # LED灭
        time.sleep(0.1)  # 等待0.1秒

KEY.irq(fun, Pin.IRQ_FALLING)  # 定义中断，下降沿触发