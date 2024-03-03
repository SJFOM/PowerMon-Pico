from machine import Pin, SoftI2C
import framebuf
import time
import ST7789VW
import INA219


def fit_value_to_screen(value: float) -> str:
    value_prepend_space: str = "" if value < 0 else " "
    value_raw_str: str = "{:.2f}".format(value)
    if abs(value) > 1000:
        value_raw_str = str(int(value))
    elif abs(value) > 100:
        value_raw_str = "{:.0f}".format(value)
    elif abs(value) > 10:
        value_raw_str = "{:.1f}".format(value)

    return value_prepend_space + value_raw_str


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
    LCD.fill(LCD.CYAN)
    LCD.rect(10, 5, 150, 30, LCD.RED, True)
    LCD.text("Raspberry Pi Pico", 20, 17, LCD.WHITE)
    display_color = LCD.WHITE
    LCD.write_text(text="PowerMon", x=10, y=50, size=3, color=LCD.BLACK)
    for i in range(0, 12):
        LCD.rect(i * 30 + 60, 100, 30, 50, (display_color), True)
        display_color = display_color << 1
    LCD.show()
    time.sleep(3)

    while True:
        INA.wake()
        ina_voltage: float = INA.supply_voltage()
        ina_current: float = INA.current()
        ina_power: float = INA.power()

        LCD.fill(LCD.BLACK)
        LCD.write_text(
            text=f"V :{fit_value_to_screen(ina_voltage)}",
            x=10,
            y=20,
            size=3,
            color=LCD.WHITE,
        )
        LCD.write_text(
            text=f"mA:{fit_value_to_screen(ina_current)}",
            x=10,
            y=60,
            size=3,
            color=LCD.WHITE,
        )
        LCD.write_text(
            text=f"mW:{fit_value_to_screen(ina_power)}",
            x=10,
            y=100,
            size=3,
            color=LCD.WHITE,
        )
        LCD.show()

        INA.sleep()
        time.sleep(0.1)
