# MicroPython SSD1306 OLED driver, I2C and SPI interfaces Modified by Bigrich-Luo
 
import time
import framebuf
 
# register definitions
SET_CONTRAST        = const(0x81)
SET_ENTIRE_ON       = const(0xa4)
SET_NORM_INV        = const(0xa6)
SET_DISP            = const(0xae)
SET_MEM_ADDR        = const(0x20)
SET_COL_ADDR        = const(0x21)
SET_PAGE_ADDR       = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP       = const(0xa0)
SET_MUX_RATIO       = const(0xa8)
SET_COM_OUT_DIR     = const(0xc0)
SET_DISP_OFFSET     = const(0xd3)
SET_COM_PIN_CFG     = const(0xda)
SET_DISP_CLK_DIV    = const(0xd5)
SET_PRECHARGE       = const(0xd9)
SET_VCOM_DESEL      = const(0xdb)
SET_CHARGE_PUMP     = const(0x8d)
 
  
class SSD1306:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        # Note the subclass must initialize self.framebuf to a framebuffer.
        # This is necessary because the underlying data buffer is different
        # between I2C and SPI implementations (I2C needs an extra byte).
        self.poweron()
        self.init_display()
 
    def init_display(self):
        for cmd in (
            SET_DISP | 0x00, # off
            # address setting
            SET_MEM_ADDR, 0x00, # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01, # column addr 127 mapped to SEG0
            SET_MUX_RATIO, self.height - 1,
            SET_COM_OUT_DIR | 0x08, # scan from COM[N] to COM0
            SET_DISP_OFFSET, 0x00,
            SET_COM_PIN_CFG, 0x02 if self.height == 32 else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV, 0x80,
            SET_PRECHARGE, 0x22 if self.external_vcc else 0xf1,
            SET_VCOM_DESEL, 0x30, # 0.83*Vcc
            # display
            SET_CONTRAST, 0xff, # maximum
            SET_ENTIRE_ON, # output follows RAM contents
            SET_NORM_INV, # not inverted
            # charge pump
            SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01): # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()
 
    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)
 
    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)
 
    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))
 
    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_framebuf()
 
    def fill(self, col):
        """
        使用指定颜色填充整个帧缓冲区。

        col (int): 用于填充的颜色，通常为0或1。
        """
        self.framebuf.fill(col)
    
    def pixel(self, x, y, col):
        """
        在指定位置设置一个像素点。

        x (int): 像素的X坐标。
        y (int): 像素的Y坐标。
        col (int): 像素的颜色。
        """
        self.framebuf.pixel(x, y, col)
    
    def scroll(self, dx, dy):
        """
        按指定方向滚动帧缓冲区的内容。

        dx (int): X轴方向的滚动距离。
        dy (int): Y轴方向的滚动距离。
        """
        self.framebuf.scroll(dx, dy)
    
    def text(self, string, x, y, col=1, scale=1):
        """
        在指定位置绘制文本。

        string (str): 要显示的字符串。
        x (int): 文本起始的X坐标。
        y (int): 文本起始的Y坐标。
        col (int, 可选): 文本的颜色，默认为1。
        scale (float, 可选): 文本的缩放比例，默认为1。
        """
        if scale == 1:
            self.framebuf.text(string, x, y, col)
        else:
            for i, char in enumerate(string):
                self._draw_char_scaled(char, x + int(i * 8 * scale), y, col, scale)

    def _draw_char_scaled(self, char, x, y, col, scale):
        """
        绘制缩放后的字符。

        char (str): 要绘制的字符。
        x (int): 字符起始的X坐标。
        y (int): 字符起始的Y坐标。
        col (int): 字符的颜色。
        scale (float): 字符的缩放比例。
        """
        # 获取字符的位图
        char_bitmap = framebuf.FrameBuffer(bytearray(8), 8, 8, framebuf.MONO_HLSB)
        char_bitmap.fill(not col)  # 根据col值设置背景颜色
        char_bitmap.text(char, 0, 0, col)  # 绘制字符

        # 绘制缩放后的字符
        for j in range(8):
            for i in range(8):
                if char_bitmap.pixel(i, j) == col:
                    self._draw_scaled_pixel(x + i * scale, y + j * scale, scale, col)

    def _draw_scaled_pixel(self, x, y, scale, col):
        """
        绘制缩放后的像素点。

        x (float): 像素的X坐标。
        y (float): 像素的Y坐标。
        scale (float): 像素的缩放比例。
        col (int): 像素的颜色。
        """
        for dy in range(int(scale)):
            for dx in range(int(scale)):
                self.pixel(int(x + dx), int(y + dy), col)


    def line(self, x0, y0, x1, y1, col=1):
        """
        绘制一条直线。
        x0, y0 (int): 起始点的坐标。
        x1, y1 (int): 结束点的坐标。
        col (int): 线的颜色。
        """
        self.framebuf.line(x0, y0, x1, y1, col)

    def rect(self, x, y, w, h, col=1):
        """
        绘制一个矩形。
        x, y (int): 矩形左上角的坐标。
        w, h (int): 矩形的宽度和高度。
        col (int): 矩形的颜色。
        """
        self.framebuf.rect(x, y, w, h, col)

    def fill_rect(self, x, y, w, h, col=1):
        """
        填充一个矩形。
        x, y (int): 矩形左上角的坐标。
        w, h (int): 矩形的宽度和高度。
        col (int): 矩形的颜色。
        """
        self.framebuf.fill_rect(x, y, w, h, col)

    def block(self, x1, y1, x2, y2, fill=False, thickness=1, col=1):
        """
        绘制一个矩形。

        x1, y1 (int): 矩形左上角的坐标。
        x2, y2 (int): 矩形右下角的坐标。
        fill (bool): 是否填充矩形。
        thickness (int): 矩形框的粗细。
        col (int): 矩形的颜色。
        """
        if fill:
            for x in range(x1, x2):
                for y in range(y1, y2):
                    self.pixel(x, y, col)
        else:
            # 绘制矩形的四条边
            for x in range(x1, x2):
                for t in range(thickness):
                    self.pixel(x, y1 - t, col)  # 上边
                    self.pixel(x, y2 + t - 1, col)  # 下边
            for y in range(y1, y2):
                for t in range(thickness):
                    self.pixel(x1 - t, y, col)  # 左边
                    self.pixel(x2 + t - 1, y, col)  # 右边
    def circle(self, x_center, y_center, radius, fill=False, col=1):
        """
        绘制一个圆形。

        x_center, y_center (int): 圆心的坐标。
        radius (int): 圆的半径。
        fill (bool): 是否填充圆形。
        col (int): 圆的颜色。
        """
        if fill:
            for x in range(x_center - radius, x_center + radius + 1):
                for y in range(y_center - radius, y_center + radius + 1):
                    if (x - x_center) ** 2 + (y - y_center) ** 2 <= radius ** 2:
                        self.pixel(x, y, col)
        else:
            # 使用中点圆算法绘制圆的边界
            x = radius
            y = 0
            p = 1 - radius  # 初始决策参数

            while x > y:
                # 绘制八个对称点
                self.pixel(x_center + x, y_center + y, col)
                self.pixel(x_center - x, y_center + y, col)
                self.pixel(x_center + x, y_center - y, col)
                self.pixel(x_center - x, y_center - y, col)
                self.pixel(x_center + y, y_center + x, col)
                self.pixel(x_center - y, y_center + x, col)
                self.pixel(x_center + y, y_center - x, col)
                self.pixel(x_center - y, y_center - x, col)

                y += 1
                if p <= 0:
                    p += 2 * y + 1
                else:
                    x -= 1
                    p += 2 * y - 2 * x + 1




 
class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        # Add an extra byte to the data buffer to hold an I2C data/command byte
        # to use hardware-compatible I2C transactions.  A memoryview of the
        # buffer is used to mask this byte from the framebuffer operations
        # (without a major memory hit as memoryview doesn't copy to a separate
        # buffer).
        self.buffer = bytearray(((height // 8) * width) + 1)
        self.buffer[0] = 0x40  # Set first byte of data buffer to Co=0, D/C=1
        self.framebuf = framebuf.FrameBuffer1(memoryview(self.buffer)[1:], width, height)
        super().__init__(width, height, external_vcc)
 
    def write_cmd(self, cmd):
        self.temp[0] = 0x80 # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)
 
    def write_framebuf(self):
        # Blast out the frame buffer using a single I2C transaction to support
        # hardware I2C interfaces.
        self.i2c.writeto(self.addr, self.buffer)
 
    def poweron(self):
        pass
 
 
class SSD1306_SPI(SSD1306):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        self.buffer = bytearray((height // 8) * width)
        self.framebuf = framebuf.FrameBuffer1(self.buffer, width, height)
        super().__init__(width, height, external_vcc)
 
    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs.on()
        self.dc.off()
        self.cs.off()
        self.spi.write(bytearray([cmd]))
        self.cs.on()
 
    def write_framebuf(self):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs.on()
        self.dc.on()
        self.cs.off()
        self.spi.write(self.buffer)
        self.cs.on()
 
    def poweron(self):
        self.res.on()
        time.sleep_ms(1)
        self.res.off()
        time.sleep_ms(10)
        self.res.on()
