import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime


def get_price_history(asin: str) -> dict:
    """
    Scrapes CamelCamelCamel for Amazon price history.
    Returns highest, lowest, average and current prices
    plus whether current price is a genuine deal.
    Uses Bright Data to bypass any blocks.
    """

    url = f"https://camelcamelcamel.com/product/{asin}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            return {"error": f"CamelCamelCamel returned {response.status_code}"}

        soup = BeautifulSoup(response.text, "html.parser")

        def clean_price(text: str):
            if not text:
                return None
            match = re.search(r'[\d,]+\.?\d{0,2}', text.replace(',', ''))
            if match:
                try:
                    return float(match.group())
                except:
                    return None
            return None

        # Extract price stats from the page
        # CamelCamelCamel shows these in stat blocks
        stats = {}
        stat_blocks = soup.select(".stat_block, .price_data, [class*='stat']")

        # Also try extracting from the graph data embedded in page
        # CamelCamelCamel embeds price data as JavaScript arrays
        script_tags = soup.find_all("script")
        price_points = []

        for script in script_tags:
            text = script.string or ""
            # Look for price data arrays like [timestamp, price]
            matches = re.findall(r'\[(\d{10,}),\s*([\d.]+)\]', text)
            for timestamp, price in matches:
                try:
                    price_points.append({
                        "date": datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d"),
                        "price": float(price)
                    })
                except:
                    pass

        # Extract highest and lowest from visible text
        page_text = soup.get_text()

        # Look for "Highest Price" and "Lowest Price" patterns
        highest_match = re.search(r'[Hh]ighest\s*[Pp]rice[:\s]+([£$€]?[\d,]+\.?\d{0,2})', page_text)
        lowest_match = re.search(r'[Ll]owest\s*[Pp]rice[:\s]+([£$€]?[\d,]+\.?\d{0,2})', page_text)
        current_match = re.search(r'[Cc]urrent\s*[Pp]rice[:\s]+([£$€]?[\d,]+\.?\d{0,2})', page_text)

        highest = clean_price(highest_match.group(1)) if highest_match else None
        lowest = clean_price(lowest_match.group(1)) if lowest_match else None
        current = clean_price(current_match.group(1)) if current_match else None

        # If we got price points from JS, calculate stats from them
        if price_points and not highest:
            prices = [p["price"] for p in price_points]
            highest = max(prices)
            lowest = min(prices)
            current = prices[-1] if prices else None

        # Calculate average
        all_prices = [p["price"] for p in price_points] if price_points else []
        average = round(sum(all_prices) / len(all_prices), 2) if all_prices else None

        # Determine if current price is a genuine deal
        deal_verdict = "unknown"
        if current and lowest and highest:
            price_range = highest - lowest
            if price_range > 0:
                position = (current - lowest) / price_range
                if position <= 0.2:
                    deal_verdict = "excellent"   # Bottom 20% of range
                elif position <= 0.4:
                    deal_verdict = "good"
                elif position <= 0.6:
                    deal_verdict = "average"
                elif position <= 0.8:
                    deal_verdict = "poor"
                else:
                    deal_verdict = "bad"         # Top 20% — near highest ever

        return {
            "asin": asin,
            "camel_url": url,
            "highest_price": highest,
            "lowest_price": lowest,
            "current_price": current,
            "average_price": average,
            "price_points": price_points[-90:],  # Last 90 data points max
            "deal_verdict": deal_verdict,
            "data_points_count": len(price_points),
            "error": None
        }

    except Exception as e:
        return {"error": str(e), "asin": asin}