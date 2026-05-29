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
    Scrapes a regional Amazon URL with correct headers per region.
    """
    # Set correct headers per region so Amazon doesn't redirect
    if identity["country"] == "us":
        accept_language = "en-US,en;q=0.9"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    elif identity["country"] == "in":
        accept_language = "en-IN,en;q=0.9"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    else:
        accept_language = "en-GB,en;q=0.9"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"

    headers = {
        "User-Agent": user_agent,
        "Accept-Language": accept_language,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    try:
        print(f"  → Scraping {identity['label']}...")
        session = requests.Session()

        # Set region-specific cookies to prevent redirect
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

        print(f"     ✅ Status: {response.status_code} | Final URL: {response.url}")

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