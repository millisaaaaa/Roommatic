from RPLCD.i2c import CharLCD
import time

LCD_ADDR = 0x27  # 如果 i2cdetect 看到的是 3f，就改成 0x3f

lcd = CharLCD(
    i2c_expander="PCF8574",
    address=LCD_ADDR,
    port=1,
    cols=16,
    rows=2,
    charmap="A00",
    auto_linebreaks=False
)


def show_roommatic_status(system_status="ON", people_num=None, pmv=None):
    """
    1602A LCD 顯示格式：
    line1: ROOMMATIC ON
    line2: P:1 PMV:+1.10
    """

    lcd.clear()

    line1 = f"ROOMMATIC {system_status}"

    if people_num is None:
        people_text = "P:--"
    else:
        people_text = f"P:{people_num}"

    if pmv is None:
        pmv_text = "PMV:--"
    else:
        pmv_text = f"PMV:{pmv:+.2f}"

    line2 = f"{people_text} {pmv_text}"

    lcd.write_string(line1[:16])
    lcd.cursor_pos = (1, 0)
    lcd.write_string(line2[:16])


def show_startup():
    lcd.clear()
    lcd.write_string("ROOMMATIC RUN")
    lcd.cursor_pos = (1, 0)
    lcd.write_string("Sensing...")


def show_error(message="Check Sensor"):
    lcd.clear()
    lcd.write_string("ROOMMATIC ERR")
    lcd.cursor_pos = (1, 0)
    lcd.write_string(message[:16])


def clear_lcd():
    lcd.clear()


if __name__ == "__main__":
    show_startup()
    time.sleep(2)

    show_roommatic_status(
        system_status="ON",
        people_num=1,
        pmv=1.10
    )
    time.sleep(5)

    clear_lcd()