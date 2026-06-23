# /home/pi/Roommatic/scripts/sensors/d1mini.py

from __future__ import annotations

import re
import time
import serial


# 如果你的 D1 mini 不是 /dev/ttyUSB0，請改這裡
PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600
TIMEOUT = 3


def _open_serial():
    ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)
    time.sleep(2)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser


def read_dht22() -> dict:
    """
    向 D1 mini 發送 TEMP 指令，讀取 DHT22 溫濕度。

    D1 mini 預期回傳：
    TEMP=26.80,RH=61.20

    回傳格式：
    {
        "ta": 26.8,
        "rh": 61.2
    }
    """

    ser = _open_serial()

    try:
        ser.write(b"TEMP\n")

        start = time.time()

        while time.time() - start < TIMEOUT:
            line = ser.readline().decode("utf-8", errors="ignore").strip()

            if not line:
                continue

            print(f"[D1MINI] {line}")

            if line == "DHT_ERROR":
                raise RuntimeError("D1 mini 回傳 DHT_ERROR，請檢查 DHT22 接線或感測器狀態。")

            match = re.search(r"TEMP=([-+]?\d+\.?\d*),RH=([-+]?\d+\.?\d*)", line)

            if match:
                ta = float(match.group(1))
                rh = float(match.group(2))

                return {
                    "ta": ta,
                    "rh": rh,
                }

        raise TimeoutError("讀取 D1 mini DHT22 超時，沒有收到 TEMP=...,RH=...")

    finally:
        ser.close()


def send_ir_command(command: str) -> str:
    """
    向 D1 mini 發送 IR 控制指令。
    例如：
    GREE26
    GREE_OFF
    KEL26
    KEL_OFF
    """

    ser = _open_serial()

    try:
        ser.write((command.strip() + "\n").encode("utf-8"))

        start = time.time()
        messages = []

        while time.time() - start < TIMEOUT:
            line = ser.readline().decode("utf-8", errors="ignore").strip()

            if not line:
                continue

            print(f"[D1MINI] {line}")
            messages.append(line)

            if line == "IR_DONE":
                return "IR_DONE"

            if line.startswith("UNKNOWN_CMD"):
                raise RuntimeError(f"D1 mini 不認得指令：{line}")

        raise TimeoutError(f"IR 指令 {command} 發送超時，沒有收到 IR_DONE。已收到：{messages}")

    finally:
        ser.close()

def read_dht22_processed(samples: int = 10, interval: float = 2.0) -> dict:
    """
    多次讀取 DHT22，並在 Raspberry Pi 端做資料前處理。

    處理內容：
    1. 多次取樣
    2. 移除讀取失敗資料
    3. 合理範圍檢查
    4. 異常值剔除
    5. 平均後回傳
    """

    import statistics
    import time

    ta_values = []
    rh_values = []

    for _ in range(samples):
        try:
            data = read_dht22()

            ta = float(data["ta"])
            rh = float(data["rh"])

            # 合理範圍檢查
            if not (-40 <= ta <= 80):
                continue

            if not (0 <= rh <= 100):
                continue

            ta_values.append(ta)
            rh_values.append(rh)

        except Exception as e:
            print(f"[DHT PROCESS] sample failed: {e}")

        time.sleep(interval)

    if len(ta_values) == 0 or len(rh_values) == 0:
        raise RuntimeError("DHT22 前處理失敗：沒有取得任何有效資料。")

    # 異常值剔除：用平均值 ± 2 倍標準差
    def remove_outliers(values: list[float]) -> list[float]:
        if len(values) < 3:
            return values

        mean_value = statistics.mean(values)
        std_value = statistics.stdev(values)

        lower = mean_value - 2 * std_value
        upper = mean_value + 2 * std_value

        filtered = [v for v in values if lower <= v <= upper]

        if len(filtered) == 0:
            return values

        return filtered

    ta_filtered = remove_outliers(ta_values)
    rh_filtered = remove_outliers(rh_values)

    ta_mean = round(statistics.mean(ta_filtered), 2)
    rh_mean = round(statistics.mean(rh_filtered), 2)

    print(
        f"[DHT PROCESS] samples={samples}, "
        f"valid_ta={len(ta_values)}, valid_rh={len(rh_values)}, "
        f"ta={ta_mean}, rh={rh_mean}"
    )

    return {
        "ta": ta_mean,
        "rh": rh_mean,
    }

if __name__ == "__main__":
    print(read_dht22())
    # print(send_ir_command("GREE26"))