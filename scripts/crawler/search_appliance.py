import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs, unquote


import re

def extract_power_from_text(text: str):
    """
    優先抓「消耗功率 / 額定功率」附近的值
    避開「冷氣能力 / 冷房能力」這類數值
    """
    text = text.lower()

    # 先把換行和多餘空白整理一下
    normalized = re.sub(r'\s+', ' ', text)

    # 優先關鍵字：真正比較像耗電功率
    power_keywords = [
        "消耗功率",
        "額定功率",
        "電功率",
        "power consumption",
        "input power",
        "rated power"
    ]

    # 排除關鍵字：這些通常不是耗電功率
    bad_keywords = [
        "冷氣能力",
        "冷房能力",
        "暖房能力",
        "能力",
        "capacity",
        "btu"
    ]

    # 先找含有功率關鍵字的附近文字
    for kw in power_keywords:
        pattern = rf'{kw}.{{0,30}}?(\d+(\.\d+)?)\s*(kw|w)'
        match = re.search(pattern, normalized)
        if match:
            value = float(match.group(1))
            unit = match.group(3)

            if unit == 'kw':
                return value * 1000
            return value

    # 如果上面沒抓到，再逐段檢查，但避開壞關鍵字
    segments = re.split(r'[。;；\n|]', normalized)

    for seg in segments:
        if any(bad in seg for bad in bad_keywords):
            continue

        if any(kw in seg for kw in power_keywords):
            kw_match = re.search(r'(\d+(\.\d+)?)\s*kw', seg)
            if kw_match:
                return float(kw_match.group(1)) * 1000

            w_match = re.search(r'(\d+(\.\d+)?)\s*w', seg)
            if w_match:
                return float(w_match.group(1))

    return None


def normalize_duckduckgo_url(raw_url: str):
    """
    把 DuckDuckGo 跳轉網址轉成真正商品頁網址
    """
    if not raw_url:
        return None

    # 補成完整網址
    if raw_url.startswith("//"):
        raw_url = "https:" + raw_url

    # 如果是 duckduckgo redirect link，解析 uddg 參數
    if "duckduckgo.com/l/?" in raw_url:
        parsed = urlparse(raw_url)
        query_dict = parse_qs(parsed.query)
        uddg_list = query_dict.get("uddg")

        if uddg_list:
            return unquote(uddg_list[0])

    return raw_url


def fetch_from_web(query: str):
    """
    用 DuckDuckGo 抓搜尋結果
    """
    url = f"https://html.duckduckgo.com/html/?q={query}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []

    for a in soup.select(".result__a")[:5]:
        link = a.get("href")
        real_link = normalize_duckduckgo_url(link)
        if real_link:
            results.append(real_link)

    return results

def scrape_power_from_page(url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(url, headers=headers, timeout=10)
        text = res.text

        power = extract_power_from_text(text)

        if power is None:
            print("這頁沒抓到『耗電功率』，可能只有冷房能力或規格是動態載入")
        else:
            print("成功抓到耗電功率:", power)

        return power

    except Exception as e:
        print("抓頁面失敗:", url, "錯誤:", e)
        return None


def search_appliance_online(brand: str, model: str, category: str):
    query = f"{brand} {model} 功率"
    urls = fetch_from_web(query)

    print("搜尋關鍵字:", query)
    print("找到的網址:")
    for u in urls:
        print(u)

    for url in urls:
        power = scrape_power_from_page(url)
        print("目前測試網址:", url, "=> 抓到功率:", power)

        if power:
            return {
                "category": category,
                "brand": brand,
                "model": model,
                "rated_power": power,
                "source_type": "crawler",
                "source_url": url
            }

    # fallback
    if category == "air_conditioner":
        default_power = 900
    elif category == "fan":
        default_power = 50
    elif category == "light":
        default_power = 12
    else:
        default_power = 100

    return {
        "category": category,
        "brand": brand,
        "model": model,
        "rated_power": default_power,
        "source_type": "preset",
        "source_url": None
    }