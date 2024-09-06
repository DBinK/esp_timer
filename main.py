
import time
from machine import Pin, SoftI2C, RTC
from libs.ssd1306 import SSD1306_I2C


# 定义对应的管脚对象
i2c = SoftI2C(scl=Pin(1), sda=Pin(0))

# 创建 OLED 对象
oled = SSD1306_I2C(width=128, height=64, i2c=i2c)

# 清屏
oled.fill(1)
time.sleep(1)
oled.fill(0)

# 矩形
oled.block(1, 1, 128, 64, fill=False, thickness=1, col=1)

# 圆圈
oled.circle(64, 32, 20, fill=False, col=1)

clock = time.localtime()

# 打印
oled.text(f'time:{clock[3]}:{clock[4]}:{clock[5]}', 10, 10)
oled.text(f'date:{clock[0]}:{clock[1]}:{clock[2]}', 10, 30)


# # 显示内容
oled.show()
