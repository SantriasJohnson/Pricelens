import cognee
import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure Cognee to use AIML API
# so it uses the same AI you already have
os.environ["LLM_API_KEY"] = os.getenv("AIML_API_KEY", "")
os.environ["LLM_ENDPOINT"] = "https://api.aimlapi.com/v1"
os.environ["LLM_MODEL"] = "anthropic/claude-haiku-4.5"


def remember_analysis(asin: str, product_title: str, comparison: dict) -> bool:
    """
    Stores a price analysis result in Cognee memory.
    Called every time a product is analysed.
    """
    try:
        # Build a structured memory string
        # Cognee stores this as a knowledge graph node
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        prices = comparison.get("results", [])

        price_lines = []
        for r in prices:
            if r.get("price"):
                currency = r.get("currency", "£")
                price = r.get("price")
                region = r["identity"]["label"]
                price_lines.append(f"{region}: {currency}{price}")

        price_summary = ", ".join(price_lines) if price_lines else "No prices found"
        spread = comparison.get("spread", 0)
        discrimination = comparison.get("price_discrimination", False)

        memory_text = f"""
Product Analysis Record
ASIN: {asin}
Product: {product_title}
Date: {today}
Prices: {price_summary}
Price spread across regions: £{spread}
Price discrimination detected: {discrimination}
Minimum price found: £{comparison.get('min_price', 'N/A')}
Maximum price found: £{comparison.get('max_price', 'N/A')}
"""

        # Store in Cognee memory
        asyncio.run(_remember(memory_text, asin))
        return True

    except Exception as e:
        print(f"Memory storage failed: {e}")
        return False


def recall_history(asin: str, product_title: str) -> dict:
    """
    Recalls past price analyses for a product from Cognee memory.
    Returns price trend and whether price has changed.
    """
    try:
        query = f"Price history for ASIN {asin} product {product_title}"
        results = asyncio.run(_recall(query))

        if not results:
            return {
                "found": False,
                "message": "First time analysing this product",
                "history": []
            }

        # Parse recalled memories
        history = []
        for result in results:
            text = str(result)
            if asin in text or product_title[:20] in text:
                history.append(text)

        if not history:
            return {
                "found": False,
                "message": "First time analysing this product",
                "history": []
            }

        return {
            "found": True,
            "message": f"Found {len(history)} past analysis records",
            "history": history,
            "raw": results
        }

    except Exception as e:
        print(f"Memory recall failed: {e}")
        return {
            "found": False,
            "message": f"Memory unavailable: {str(e)}",
            "history": []
        }


async def _remember(text: str, dataset_name: str):
    """Internal async function to store in Cognee"""
    await cognee.add(text, node_set=[dataset_name, "pricelens"])
    await cognee.cognify()


async def _recall(query: str):
    """Internal async function to recall from Cognee"""
    results = await cognee.search(query_text=query)
    return results