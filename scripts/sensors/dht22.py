def read_dht22():
    """
    執行一次 DHT22 蒐集流程，回傳平均後的溫度與濕度
    回傳格式:
    {"ta": 25.3, "rh": 44.24}
    """

    import pandas as pd
    import serial
    from time import sleep

    columns = ["Humidity", "Temperature", "Heat Index"]
    DHT_df = pd.DataFrame(columns=columns)

    COM_PORT = '/dev/ttyACM0'
    BAUD_RATES = 9600

    ser = None

    try:
        ser = serial.Serial(COM_PORT, BAUD_RATES, timeout=0.5)
        sleep(2)

        while True:
            sleep(2)

            while ser.in_waiting:
                try:
                    h = ser.readline().decode('utf-8', errors='ignore').strip()
                    t = ser.readline().decode('utf-8', errors='ignore').strip()
                    hic = ser.readline().decode('utf-8', errors='ignore').strip()

                    if h == "" or t == "" or hic == "":
                        continue

                    DHT_set = pd.Series([float(h), float(t), float(hic)], index=columns)

                    if not DHT_df.empty:
                        DHT_df = pd.concat([DHT_df, pd.DataFrame([DHT_set])], ignore_index=True)
                    else:
                        DHT_df = pd.DataFrame([DHT_set])

                except ValueError:
                    continue

            if len(DHT_df) >= 30:
                break

    finally:
        if ser and ser.is_open:
            ser.close()

    # 全空列刪除
    DHT_df = DHT_df.dropna(how='all')

    # 補平均
    for col in ['Humidity', 'Temperature']:
        DHT_mean = DHT_df[col].mean()
        DHT_df[col] = DHT_df[col].fillna(DHT_mean)

    # 離群值處理：超出平均 ± 2*std -> 換成平均
    for col in ["Humidity", "Temperature"]:
        DHT_mean = DHT_df[col].mean()
        DHT_std = DHT_df[col].std()

        lower_bound = DHT_mean - 2 * DHT_std
        upper_bound = DHT_mean + 2 * DHT_std

        test_mask = (DHT_df[col] < lower_bound) | (DHT_df[col] > upper_bound)
        DHT_df.loc[test_mask, col] = round(DHT_mean, 1)

    DHT_h_mean = round(DHT_df["Humidity"].mean(), 2)
    DHT_t_mean = round(DHT_df["Temperature"].mean(), 2)

    return {
        "ta": DHT_t_mean,
        "rh": DHT_h_mean
    }