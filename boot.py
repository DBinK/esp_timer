# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

from machine import Pin  # type: ignore

# 释放所有GPIO, 断电重上电不再失控
def release_all_GPIO():
    for i in range(0, 22):
        try:
            GND = Pin(i, Pin.OUT, value=0)
            print(f"releasing gpio {i}")
        except Exception as e:
            print(f"skip gpio {i}, error: {e}")
            continue

release_all_GPIO()