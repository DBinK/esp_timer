import time
import network


# 设置路由器 WiFi 账号与密码
ssid = 'ovo'
password = '00000000'

# 创建 WIFI 连接对象
wlan = network.WLAN(network.STA_IF)
# 激活 wlan 接口
wlan.active(True)
# 扫描允许访问的 WiFi
print('扫描周围信号源：', wlan.scan())

print("正在连接 WiFi 中", end="")
#
wlan.connect(ssid, password)

# 如果一直没有连接成功，则每隔 0.1s 在命令号中打印一个 .
while not wlan.isconnected():
  print(".", end="")
  time.sleep(0.5)

# 连接成功之后，打印出 IP、子网掩码(netmask)、网关(gw)、DNS 地址
print(f"\n{wlan.ifconfig()}")