import csv
from scripts.database.db_config import get_connection
from scripts.crawler.find_catalog import find_appliance_in_catalog
from scripts.crawler.search_appliance import search_appliance_online
from scripts.crawler.save_catalog import save_appliance_to_catalog

CSV_PATH = "/home/pi/Roommatic/data/appliance_seed.csv"


def is_power_reasonable(category: str, rated_power):
    """
    檢查抓到的 rated_power 是否落在合理範圍。
    回傳:
    True  = 合理
    False = 可疑
    """

    if rated_power is None:
        return False

    try:
        power = float(rated_power)
    except Exception:
        return False

    if category == "air_conditioner":
        return 200 <= power <= 3000

    if category == "fan":
        return 5 <= power <= 200

    if category == "light":
        return 1 <= power <= 100

    return False


def save_preset_light(category: str, brand: str, model: str):
    """
    專門處理 Generic 燈具模板，例如 LED-10W
    """
    rated_power = None

    try:
        # LED-10W / T8-40W / CeilingLight-24W
        power_str = model.split("-")[-1].upper().replace("W", "")
        rated_power = float(power_str)
    except Exception:
        rated_power = None

    data = {
        "category": category,
        "brand": brand,
        "model": model,
        "rated_power": rated_power,
        "source_type": "preset",
        "source_url": None
    }

    # 燈具 preset 也檢查一下，避免 model 寫錯
    if not is_power_reasonable(category, rated_power):
        print(f"燈具功率可疑，改寫入 manual: {brand} {model} | rated_power={rated_power}")

        data["rated_power"] = None
        data["source_type"] = "manual"

    save_appliance_to_catalog(data)
    print(f"已寫入 {data['source_type']}: {brand} {model} | rated_power={data['rated_power']}")


def save_manual_empty(category: str, brand: str, model: str, reason: str):
    """
    抓不到或功率可疑時，先寫 manual 空資料。
    這樣前端仍然查得到型號，但 rated_power 留給人工確認。
    """
    fallback_data = {
        "category": category,
        "brand": brand,
        "model": model,
        "rated_power": None,
        "source_type": "manual",
        "source_url": None
    }

    save_appliance_to_catalog(fallback_data)
    print(f"{reason}，已寫入 manual 空資料: {brand} {model}")


def process_row(row: dict):
    category = row["category"].strip()
    brand = row["brand"].strip()
    model = row["model"].strip()

    print(f"\n處理中: {category} | {brand} | {model}")

    # 1. 先查 DB 是否已存在
    existing = find_appliance_in_catalog(category, brand, model)
    if existing:
        print("已存在，跳過")
        return

    # 2. Generic 燈具直接當 preset 寫入
    if category == "light" and brand.lower() == "generic":
        save_preset_light(category, brand, model)
        return

    # 3. 其他設備走 crawler
    result = search_appliance_online(brand, model, category)

    if result:
        rated_power = result.get("rated_power")

        # 4. 檢查 crawler 抓到的功率是否合理
        if is_power_reasonable(category, rated_power):
            save_appliance_to_catalog(result)
            print(
                f"已寫入 crawler: {brand} {model} | rated_power={rated_power}"
            )
        else:
            print(
                f"⚠️ crawler 抓到可疑功率，不直接採用: "
                f"{brand} {model} | rated_power={rated_power}"
            )
            print(f"來源網址: {result.get('source_url')}")

            save_manual_empty(
                category,
                brand,
                model,
                reason="crawler 功率超出合理範圍或為空"
            )

    else:
        save_manual_empty(
            category,
            brand,
            model,
            reason="crawler 無結果"
        )


def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            process_row(row)

    print("\n全部處理完成！")


if __name__ == "__main__":
    main()