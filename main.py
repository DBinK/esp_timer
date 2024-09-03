'''
实验名称：外部中断
版本：v1.0
作者：WalnutPi
说明：通过按键改变LED的亮灭状态（外部中断方式）
'''

from machine import Pin
import time

LED=Pin(8,Pin.OUT) #构建LED对象,开始熄灭
KEY=Pin(9,Pin.IN,Pin.PULL_UP) #构建KEY对象
state=0  #LED引脚状态

#LED状态翻转函数
def fun(KEY):
    global state
    time.sleep_ms(10) #消除抖动
    if KEY.value()==0: #确认按键被按下
        state = not state
        LED.value(state)

KEY.irq(fun,Pin.IRQ_FALLING) #定义中断，下降沿触发
