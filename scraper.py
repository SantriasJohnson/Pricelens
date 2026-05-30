import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()

IDENTITIES = [
    {"id": "uk", "label": "🇬🇧 UK", "country": "gb", "domain": "amazon.co.uk", "currency": "£"},
    {"id": "us", "label": "🇺🇸 US", "country": "us", "domain": "amazon.com", "currency": "$"},
    {"id": "in", "label": "🇮🇳 India", "country": "in", "domain": "amazon.in", "currency": "₹"}
]


def get_asin(url: str) -> str:
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    return match.group(1) if match else None


def build_url(asin: str, domain: str) -> str:
    return f"https://www.{domain}/dp/{asin}"


def get_proxy(country: str) -> dict:
    username = os.getenv("BD_USERNAME")
    password = os.getenv("BD_PASSWORD")
    host = os.getenv("BD_HOST", "brd.superproxy.io")
    port = os.getenv("BD_PORT", "22225")
    proxy_url = f"http://{username}-country-{country}:{password}@{host}:{port}"
    return {"http": proxy_url, "https": proxy_url}


def scrape_single(url: str, identity: dict) -> dict:
    """
    Scrapes Amazon product page directly.
    In production this routes through Bright Data Web Unlocker.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    try:
        print(f"  → Scraping {identity['label']}...")
        session = requests.Session()

        if identity["country"] == "us":
            session.cookies.set("i18n-prefs", "USD", domain=".amazon.com")
        elif identity["country"] == "in":
            session.cookies.set("i18n-prefs", "INR", domain=".amazon.in")
        else:
            session.cookies.set("i18n-prefs", "GBP", domain=".amazon.co.uk")

        response = session.get(
            url,
            headers=headers,
            timeout=20,
            allow_redirects=True
        )

        print(f"     ✅ Status: {response.status_code}")

        return {
            "identity": identity,
            "url": url,
            "final_url": response.url,
            "html": response.text,
            "error": None
        }

    except Exception as e:
        print(f"     ❌ Error: {str(e)}")
        return {
            "identity": identity,
            "url": url,
            "final_url": url,
            "html": "",
            "error": str(e)
        }

def scrape_all(url: str) -> list:
    print(f"\n🔍 Analysing: {url}")
    asin = get_asin(url)
    if not asin:
        print("❌ Could not extract ASIN")
        return []

    print(f"  ✅ ASIN: {asin}")
    results = []
    for identity in IDENTITIES:
        regional_url = build_url(asin, identity["domain"])
        result = scrape_single(regional_url, identity)
        results.append(result)

    return results
def search_price_via_brightdata(asin: str, product_title: str = "") -> dict:
    """
    Uses Bright Data SERP API to search Google for
    the product price — cross-verifying Amazon's stated price
    against what Google Shopping shows.
    """
    api_key = os.getenv("BD_API_KEY")
    zone = os.getenv("BD_ZONE", "serp_api1")

    # Search Google Shopping for the product
    query = f"{product_title or asin} price"
    search_url = f"https://www.google.co.uk/search?q={query}&brd_json=1"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "zone": zone,
        "url": search_url,
        "format": "raw"
    }

    try:
        print(f"  → Bright Data SERP: searching Google for '{query}'...")
        response = requests.post(
            "https://api.brightdata.com/request",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            import re

            # Extract prices from all available sections
            prices_found = []

            # Check popular_products
            popular = data.get("popular_products", {})
            items = popular.get("items", []) if isinstance(popular, dict) else []
            for item in items:
                price_str = item.get("price", "")
                if price_str:
                    prices_found.append({
                        "price": price_str,
                        "source": item.get("shop", "Google Shopping"),
                        "title": item.get("title", "")
                    })

            # Check organic snippets
            organic = data.get("organic", [])
            for result in organic[:5]:
                snippet = result.get("snippet", "") or ""
                title = result.get("title", "") or ""
                price_match = re.search(r'[£$₹€][\d,]+\.?\d{0,2}', snippet + title)
                if price_match:
                    prices_found.append({
                        "price": price_match.group(),
                        "source": result.get("display_link", "Web"),
                        "title": title
                    })

            if prices_found:
                return {
                    "found": True,
                    "prices": prices_found,
                    "top_price": prices_found[0]["price"],
                    "top_source": prices_found[0]["source"],
                    "total_found": len(prices_found),
                    "error": None
                }
            else:
                return {
                    "found": False,
                    "prices": [],
                    "error": "No prices in Google results"
                }

        return {
            "found": False,
            "prices": [],
            "error": f"Status {response.status_code}"
        }

    except Exception as e:
        return {
            "found": False,
            "prices": [],
            "error": str(e)
        }