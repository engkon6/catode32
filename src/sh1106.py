"""
sh1106.py - MicroPython SH1106 I2C OLED driver
"""

import framebuf

class SH1106_I2C(framebuf.FrameBuffer):
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.buffer = bytearray(self.width * self.height // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def write_cmd(self, cmd):
        self.temp[0] = 0x80 # Co=1, D/C=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def init_display(self):
        for cmd in (
            0xAE,       # Display off
            0xD5, 0x80, # Clock divide ratio/oscillator
            0xA8, 0x3F, # Multiplex ratio (64)
            0xD3, 0x00, # Display offset
            0x40,       # Start line address
            0xAD, 0x8B, # Charge pump
            0xA1,       # Segment remap (0xA1 = normal, 0xA0 = flipped)
            0xC8,       # COM scan direction (0xC8 = normal, 0xC0 = flipped)
            0xDA, 0x12, # COM pins hardware config
            0x81, 0x7F, # Contrast
            0xD9, 0x22, # Pre-charge period
            0xDB, 0x40, # VCOMH deselect level
            0xA4,       # Entire display on (resume)
            0xA6,       # Normal display
            0xAF,       # Display on
        ):
            self.write_cmd(cmd)

    def poweroff(self):
        self.write_cmd(0xAE)

    def poweron(self):
        self.write_cmd(0xAF)

    def contrast(self, contrast):
        self.write_cmd(0x81)
        self.write_cmd(contrast & 0xFF)

    def invert(self, invert):
        self.write_cmd(0xA7 if invert else 0xA6)

    def show(self):
        for page in range(self.height // 8):
            self.write_cmd(0xB0 + page)
            self.write_cmd(0x02) # column offset 2 for 128x64 SH1106
            self.write_cmd(0x10)
            start = page * self.width
            end = start + self.width
            self.i2c.writeto_mem(self.addr, 0x40, self.buffer[start:end])
