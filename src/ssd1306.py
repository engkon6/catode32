"""
ssd1306.py - SH1106 compatibility shim for SSD1306 API.

This module provides an SSD1306_I2C class that internally uses the SH1106
driver (robert-hh/SH1106), allowing Catode32's renderer.py to work with
SH1106 OLED displays without modification.
"""

from machine import Pin, I2C
from sh1106 import SH1106_I2C as _SH1106_I2C


class SSD1306_I2C(_SH1106_I2C):
    """SSD1306-compatible constructor that wraps SH1106_I2C."""

    def __init__(self, width, height, i2c, addr=0x3c):
        super().__init__(width, height, i2c, res=None, addr=addr,
                         rotate=0, external_vcc=False, delay=0)
