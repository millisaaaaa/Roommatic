from scripts.crawler.search_appliance import search_appliance_online
from scripts.crawler.save_catalog import save_appliance_to_catalog
from scripts.crawler.find_catalog import find_appliance_in_catalog

def get_or_create_appliance(brand: str, model: str, category: str):
    existing = find_appliance_in_catalog(category, brand, model)

    if existing:
        print("資料庫已存在，直接使用：")
        print(existing)
        return existing

    print("資料庫查無資料，開始爬取...")
    result = search_appliance_online(brand, model, category)

    if not result:
        print("查無資料")
        return None

    save_appliance_to_catalog(result)
    print("已寫入 appliance_catalog：")
    print(result)
    return result

if __name__ == "__main__":
    get_or_create_appliance(
        brand="Panasonic",
        model="CS-UJ36BA2-CU-UJ36BCA2",
        category="air_conditioner"
    )