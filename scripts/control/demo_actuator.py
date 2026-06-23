import serial
import time

ARDUINO_PORT = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_55533343737351E052E1-if00"
BAUD_RATE = 9600


def send_demo_status(light_status: str, ac_status: str, ac_temp):
    """
    傳送展場 demo 狀態給 Arduino LCD + LED

    light_status: "on" / "off"
    ac_status: "on" / "off"
    ac_temp: int / None
    """

    light_cmd = "ON" if light_status == "on" else "OFF"
    ac_cmd = "ON" if ac_status == "on" else "OFF"

    if ac_temp is None:
        ac_temp = 28

    command = f"LIGHT={light_cmd};AC={ac_cmd};TEMP={int(ac_temp)}\n"

    ser = None

    try:
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        ser.write(command.encode("utf-8"))
        print(f"[DEMO ACTUATOR] sent: {command.strip()}")

        return {
            "success": True,
            "command": command.strip(),
        }

    except Exception as e:
        print(f"[DEMO ACTUATOR ERROR] {e}")

        return {
            "success": False,
            "error": str(e),
        }

    finally:
        if ser and ser.is_open:
            ser.close()