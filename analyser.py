import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def analyse(comparison: dict, url: str) -> dict:
    """
    Sends price comparison data to Claude via AIML API
    and gets back a full manipulation analysis.
    AIML API is the official lablab hackathon AI provider.
    """

    prompt = f"""You are a consumer protection AI analyst.
Answer these 6 questions a shopper needs to know:
1. Is this price manipulated?
2. Am I paying more than people in other regions?
3. Was this cheaper before?
4. Is this actually a good deal?
5. Is this fake scarcity?
6. Is this a real discount or a marketing trick?

Product URL: {url}
Product title: {comparison.get('product_title', 'Unknown')}

Price across regions:
{json.dumps(comparison['results'], indent=2)}

Price spread across regions: {comparison['spread']}
Average discount shown: {comparison.get('avg_discount')}%
Scarcity signals found: {comparison['scarcity_signals']}

Return ONLY valid JSON, no markdown, no explanation outside JSON:
{{
  "manipulation_score": <integer 0-100>,
  "verdict": "<CLEAN or SUSPICIOUS or MANIPULATED>",
  "price_discrimination": <true or false>,
  "fake_scarcity": <true or false>,
  "real_discount": <true if discount is genuine, false if marketing trick>,
  "good_deal": <true or false based on price vs original and region comparison>,
  "cheapest_option": "<which region is cheapest and by how much>",
  "you_could_save": "<specific saving amount if applicable>",
  "was_cheaper_before": "<yes/no/unknown based on original price data>",
  "explanation": "<3 sentences plain English covering all 6 questions>",
  "recommendation": "<BUY NOW or WAIT or CHECK COMPETITOR or AVOID>",
  "red_flags": ["<flag1>", "<flag2>"],
  "green_flags": ["<flag1>"]
}}"""

    headers = {
        "Authorization": f"Bearer {os.getenv('AIML_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "anthropic/claude-haiku-4.5",# Claude via AIML API
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800
    }

    try:
        response = requests.post(
            "https://api.aimlapi.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        raw = response.json()["choices"][0]["message"]["content"].strip()
        clean = raw.replace("```json", "").replace("```", "").strip()

        return json.loads(clean)

    except Exception as e:
        print(f"Analysis error: {e}")
        return {
            "manipulation_score": 50,
            "verdict": "SUSPICIOUS",
            "price_discrimination": False,
            "fake_scarcity": False,
            "cheapest_option": "Could not determine",
            "you_could_save": "Analysis incomplete",
            "explanation": "Could not fully analyse this page. Try again.",
            "recommendation": "CHECK COMPETITOR",
            "red_flags": ["Analysis could not be completed"],
            "green_flags": []
        }