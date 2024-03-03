from machine import Pin, SPI, PWM
from micropython import const
import framebuf
import uctypes

# pin asignment
BL: int = const(13)
DC: int = const(8)
RST: int = const(12)
MOSI: int = const(11)
SCK: int = const(10)
CS: int = const(9)


class LCD_1inch14(framebuf.FrameBuffer):

    def __init__(self, rotation: int = 0, brightness: uctypes.UINT16 = 16_384):
        # colors coded as RGB565 (swapped bytes)
        self.RED = 0x00F8
        self.GREEN = 0xE007
        self.BLUE = 0x1F00
        self.YELLOW = 0xE0FF
        self.MAGENTA = 0x1FF8
        self.CYAN = 0xFF07
        self.BLACK = 0x0000
        self.WHITE = 0xFFFF

        # Set screen dimensions
        self.width = 240
        self.height = 135

        self.brightness = brightness

        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)

        # Set up SPI control
        self.cs(1)
        self.spi = SPI(
            1, 10_000_000, polarity=0, phase=0, sck=Pin(SCK), mosi=Pin(MOSI), miso=None
        )
        self.dc = Pin(DC, Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

        # Control Back-Light frequency & brightness
        self.pwm = PWM(Pin(BL))
        self.pwm.freq(1000)
        self.set_brightness(self.brightness)

    def set_brightness(self, brightness: uctypes.UINT16):
        """Set LCD brightness from 0 to 65535"""
        if brightness > ((2**16) - 1):
            print("Limiting brightness")
            brightness = (2**16) - 1
        self.pwm.duty_u16(brightness)

    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize display"""
        self.rst(1)
        self.rst(0)
        self.rst(1)

        # Set screen rotation
        self.write_cmd(0x36)
        self.write_data(0x70)  # 0 degrees (default)
        #         self.write_data(0xC0) # 90 degrees
        #         self.write_data(0xB0) # 180 degrees
        #         self.write_data(0x00) # 270 degrees

        self.write_cmd(0x3A)
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35)

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F)

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)

        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x28)
        self.write_data(0x01)
        self.write_data(0x17)
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x35)
        self.write_data(0x00)
        self.write_data(0xBB)

        self.write_cmd(0x2C)

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

    def off(self):
        """DISPOFF command and brightness to 0"""
        self.write_cmd(0x28)
        self.set_brightness(0)

    def on(self):
        """DISPON command and restore brightness"""
        self.write_cmd(0x29)
        self.set_brightness(self.brightness)

    def rgb565(self, r: int, g: int, b: int) -> int:
        """Encodes RGB888 to RGB565 swapping its bytes"""
        return ((g & 0x1C) << 11) | (g >> 5) | ((b & 0xF8) << 5) | (r & 0xF8)

    def gray565(self, gray: int) -> int:
        """Encodes 8-bit grayscale to RGB565 swapping its bytes"""
        return (
            ((gray & 0x1C) << 11) | (gray >> 5) | ((gray & 0xF8) << 5) | (gray & 0xF8)
        )

    def write_text(self, text, x, y, size, color):
        """Method to write Text on OLED/LCD Displays
        with a variable font size

        Args:
            text: the string of chars to be displayed
            x: x co-ordinate of starting position
            y: y co-ordinate of starting position
            size: font size of text
            color: color of text to be displayed
        """
        background = self.pixel(x, y)
        info = []
        # Creating reference charaters to read their values
        self.text(text, x, y, color)
        for i in range(x, x + (8 * len(text))):
            for j in range(y, y + 8):
                # Fetching amd saving details of pixels, such as
                # x co-ordinate, y co-ordinate, and color of the pixel
                px_color = self.pixel(i, j)
                info.append((i, j, px_color)) if px_color == color else None
        # Clearing the reference characters from the screen
        self.text(text, x, y, background)
        # Writing the custom-sized font characters on screen
        for px_info in info:
            self.fill_rect(
                size * px_info[0] - (size - 1) * x,
                size * px_info[1] - (size - 1) * y,
                size,
                size,
                px_info[2],
            )
