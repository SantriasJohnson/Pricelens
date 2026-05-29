from bs4 import BeautifulSoup
import re

PRICE_SELECTORS = [
    ".a-price-whole",
    ".a-offscreen",
    "#priceblock_ourprice",
    "#priceblock_dealprice",
    ".a-price .a-offscreen",
    "[data-price]",
    ".price",
    ".product-price",
    "[class*='price']",
    "[itemprop='price']",
]

ORIGINAL_PRICE_SELECTORS = [
    ".a-text-strike",
    ".a-price.a-text-price .a-offscreen",
    "#listPrice",
    ".priceBlockStrikePriceString",
]

SCARCITY_PHRASES = [
    "only 1 left in stock",
    "only 2 left in stock",
    "only 3 left in stock",
    "only 4 left in stock",
    "only 5 left in stock",
    "limited stock",
    "selling fast",
    "almost gone",
    "order soon",
    "in high demand",
    "deal ends today",
    "today's deal",
    "lightning deal"
]

CURRENCY_SYMBOLS = {
    "gb": "£",
    "us": "$",
    "in": "₹"
}

RATES_TO_GBP = {
    "£": 1.0,
    "$": 0.79,
    "₹": 0.0095
}


def clean_price(text: str):
    if not text:
        return None
    cleaned = re.sub(r'[^\d.]', '', text.replace(',', ''))
    match = re.search(r'\d+\.?\d{0,2}', cleaned)
    if match:
        try:
            val = float(match.group())
            return val if val > 0 else None
        except:
            return None
    return None


def extract_data(html: str, identity: dict) -> dict:
    if not html:
        return {
            "price": None,
            "original_price": None,
            "discount_percent": None,
            "scarcity": [],
            "title": None,
            "currency": "£"
        }

    soup = BeautifulSoup(html, "html.parser")

    # Currency based on country
    country = identity.get("country", "gb")
    currency = CURRENCY_SYMBOLS.get(country, "£")

    # Extract title
    title = None
    title_el = soup.select_one("#productTitle")
    if title_el:
        title = title_el.get_text(strip=True)

    # Extract current price
    price = None
    for selector in PRICE_SELECTORS:
        el = soup.select_one(selector)
        if el:
            text = el.get("content") or el.get_text(strip=True)
            candidate = clean_price(text)
            if candidate and candidate > 0:
                price = candidate
                break

    # Extract original price
    original_price = None
    for selector in ORIGINAL_PRICE_SELECTORS:
        el = soup.select_one(selector)
        if el:
            text = el.get_text(strip=True)
            candidate = clean_price(text)
            if candidate and candidate > 0 and (price is None or candidate > price):
                original_price = candidate
                break

    # Calculate discount
    discount_percent = None
    if price and original_price and original_price > price:
        discount_percent = round(((original_price - price) / original_price) * 100, 1)

    
    # Detect scarcity
    
    #page_text = soup.get_text().lower()
    #found_scarcity = [p for p in SCARCITY_PHRASES if p in page_text]
    # Only check product-specific sections, not ads or banners
    
    product_sections = [
        "#availability",
        "#urgencyMessage",
        "#dealBadge",
        "#dealContent",
        "#priceBlock_feature_div",
        "#buybox",
        "#apex_desktop"
    ]

    scarcity_text = ""
    for section in product_sections:
        el = soup.select_one(section)
        if el:
            scarcity_text += el.get_text().lower() + " "

# Fallback to full page if no sections found
    if not scarcity_text.strip():
        scarcity_text = soup.get_text().lower()

    found_scarcity = [p for p in SCARCITY_PHRASES if p in scarcity_text]
    return {
        "price": price,
        "original_price": original_price,
        "discount_percent": discount_percent,
        "scarcity": found_scarcity,
        "title": title,
        "currency": currency
    }


def compare(scraped_results: list) -> dict:
    compared = []

    for result in scraped_results:
        identity = result["identity"]

        if result.get("error") or not result.get("html"):
            compared.append({
                "identity": identity,
                "price": None,
                "price_gbp": None,
                "original_price": None,
                "discount_percent": None,
                "currency": CURRENCY_SYMBOLS.get(identity.get("country", "gb"), "£"),
                "scarcity": [],
                "title": None,
                "error": result.get("error") or "Not available in this region"
            })
            continue

        data = extract_data(result.get("html", ""), identity)

        # Convert to GBP for fair comparison
        rate = RATES_TO_GBP.get(data["currency"], 1.0)
        price_gbp = round(data["price"] * rate, 2) if data["price"] else None

        compared.append({
            "identity": identity,
            "price": data["price"],
            "price_gbp": price_gbp,
            "original_price": data["original_price"],
            "discount_percent": data["discount_percent"],
            "currency": data["currency"],
            "scarcity": data["scarcity"],
            "title": data["title"],
            "error": None
        })

    # Use GBP prices for comparison
    prices_in_gbp = [c["price_gbp"] for c in compared if c["price_gbp"]]
    spread = round(max(prices_in_gbp) - min(prices_in_gbp), 2) if len(prices_in_gbp) > 1 else 0
    all_scarcity = list(set(s for c in compared for s in c["scarcity"]))
    product_title = next((c["title"] for c in compared if c.get("title")), "Unknown product")
    discounts = [c["discount_percent"] for c in compared if c.get("discount_percent")]
    avg_discount = round(sum(discounts) / len(discounts), 1) if discounts else None

    return {
        "results": compared,
        "prices_found": prices_in_gbp,
        "min_price": min(prices_in_gbp) if prices_in_gbp else None,
        "max_price": max(prices_in_gbp) if prices_in_gbp else None,
        "spread": spread,
        "price_discrimination": spread > 2,
        "scarcity_signals": all_scarcity,
        "product_title": product_title,
        "avg_discount": avg_discount
    }