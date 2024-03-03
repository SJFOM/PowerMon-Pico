from machine import Pin, SoftI2C
import framebuf
import time
import ST7789VW
import INA219

if __name__ == "__main__":

    # Setup the LCD screen
    LCD = ST7789VW.LCD_1inch14()
    LCD.set_brightness(100)

    # Talk to the INA219 current sensor
    i2c = SoftI2C(sda=Pin(29), scl=Pin(28), freq=100_000)
    INA = INA219.INA219(shunt_ohms=0.1, i2c=i2c)
    INA.configure()
    INA.sleep()

    # color BRG
    LCD.fill(LCD.WHITE)
    LCD.rect(10, 5, 150, 30, LCD.RED, True)
    LCD.text("Raspberry Pi Pico", 20, 17, LCD.WHITE)
    display_color = 0x001F
    LCD.write_text(text="HELLO", x=10, y=50, size=5, color=LCD.BLACK)
    for i in range(0, 12):
        LCD.rect(i * 30 + 60, 100, 30, 50, (display_color), True)
        display_color = display_color << 1
    LCD.show()
    time.sleep(1)

    while True:
        INA.wake()
        ina_voltage: float = INA.voltage()
        ina_current: float = INA.current()
        ina_power: float = INA.power()

        LCD.fill(LCD.WHITE)
        LCD.write_text(text=f"{ina_voltage:.2f} V", x=10, y=20, size=3, color=LCD.BLACK)
        LCD.write_text(
            text=f"{ina_current:.2f} mA", x=10, y=60, size=3, color=LCD.GREEN
        )
        LCD.write_text(text=f"{ina_power:.2f} mW", x=10, y=100, size=3, color=LCD.CYAN)
        LCD.show()

        INA.sleep()
        time.sleep(1)
