import time
from machine import Timer

def update_time(callback):
    global time_now
    time_now = time.localtime()
    print(f"现在是{time_now[0]}年{time_now[1]}月{time_now[2]}日 {time_now[3]}时{time_now[4]}分{time_now[5]}秒")
    print(time_now)

#使用定时器1
tim = Timer(0)
tim.init(period=1000, mode=Timer.PERIODIC,callback=update_time) #周期为1000ms