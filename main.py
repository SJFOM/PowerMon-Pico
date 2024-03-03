from machine import Pin,SPI,PWM
import framebuf
import time

# pin asignment
BL : int = 13
DC : int = 8
RST : int = 12
MOSI : int = 11
SCK : int = 10
CS : int = 9

class LCD_1inch14(framebuf.FrameBuffer):
    
    def __init__(self, rotation:int=0, brightness:int=16_384):
        # colors coded as RGB565 (swapped bytes)
        self.RED   =   0x00F8
        self.GREEN =   0xE007
        self.BLUE  =   0x1F00
        self.YELLOW =  0xE0FF
        self.MAGENTA = 0x1FF8
        self.CYAN =    0xFF07
        self.BLACK =   0x0000
        self.WHITE =   0xFFFF
        
        # Set screen dimensions
        self.width = 240
        self.height = 135
        
        self.brightness = brightness
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        # Set up SPI control
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1_000_000)
        self.spi = SPI(1,10_000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        # Control Back-Light frequency & brightness
        self.pwm = PWM(Pin(BL))
        self.pwm.freq(1000)
        self.set_brightness(self.brightness)

    def set_brightness(self, brightness:int):
        """Set LCD brightness from 0 to 65535"""
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
        self.write_data(0x70) # 0 degrees (default)
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
        
    def rgb565(self,r: int,g: int,b: int) -> int:
        """Encodes RGB888 to RGB565 swapping its bytes"""
        return ((g & 0x1c) << 11) | (g >> 5) | ((b & 0xf8) << 5) | (r & 0xf8)
    
    def gray565(self,gray: int) -> int:
        """Encodes 8-bit grayscale to RGB565 swapping its bytes"""
        return ((gray & 0x1c) << 11) | (gray >> 5) | ((gray & 0xf8) << 5) | (gray & 0xf8)
    
    
    
if __name__=='__main__':

    LCD = LCD_1inch14()
    LCD.set_brightness(100)
    #color BRG
    LCD.fill(LCD.WHITE)
    LCD.rect(10,5,150,30,LCD.RED,True)
    LCD.text("Raspberry Pi Pico",20,17,LCD.WHITE)
    display_color = 0x001F
    # # display_color = LCD.BLUE
    LCD.text("1.14' IPS LCD TEST",20,57,LCD.BLACK)
    for i in range(0,12):      
        LCD.rect(i*30+60,100,30,50,(display_color),True)
        display_color = display_color << 1
    LCD.show()
    
    # while True:               
    #     LCD.fill(LCD.WHITE)
    #     LCD.text("Button0",20,110,LCD.BLACK)
    #     LCD.text("Button1",150,110,LCD.BLACK)
    #     LCD.text("Button2",270,110,LCD.BLACK)
    #     LCD.text("Button3",400,110,LCD.BLACK)        
    #     LCD.show()  
    #     time.sleep(0.1)
