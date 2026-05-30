# 🔍 PriceLens

> See through price manipulation before you buy.

PriceLens is an AI-powered price manipulation detector built for the **Web Data UNLOCKED Hackathon** by Bright Data x Lablab.ai.

## What It Does

Paste any Amazon product URL and PriceLens will:

- 🌍 **Compare prices across UK, US and India** in real time
- 🤖 **Detect price manipulation** using AI analysis
- 🚩 **Expose fake scarcity tactics** like manufactured urgency
- 💰 **Show how much you could save** by buying from a different region
- 🧠 **Remember past analyses** using Cognee memory — building price history over time

## Demo

![PriceLens Demo](demo.png)

## Tech Stack

| Layer | Technology |
|---|---|
| Web Scraping | Bright Data Web Unlocker API |
| AI Analysis | Claude Haiku via AIML API |
| Memory | Cognee (knowledge graph) |
| Frontend | Streamlit |
| Backend | Python |

## How It Works

User pastes Amazon URL
↓
Bright Data scrapes UK + US + India simultaneously
↓
BeautifulSoup extracts prices + scarcity signals
↓
Claude AI analyses manipulation patterns
↓
Cognee stores result in memory for price history
↓
PriceLens shows verdict, flags, savings and recommendation

## Questions It Answers

1. ✅ Is this price manipulated?
2. ✅ Am I paying more than people in other regions?
3. ✅ Is this fake scarcity?
4. ✅ Is this a real discount or a marketing trick?
5. ✅ What's the cheapest way to buy this?
6. ✅ Has this product been analysed before?

## Setup

```bash
# Clone the repo
git clone https://github.com/SantriasJohnson/Pricelens.git
cd Pricelens

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install streamlit requests beautifulsoup4 anthropic python-dotenv cognee

# Add your API keys
cp .env.example .env
# Edit .env with your keys

# Run the app
streamlit run app.py
```

## Environment Variables

Create a `.env` file with:

BD_API_KEY=your_bright_data_api_key
AIML_API_KEY=your_aiml_api_key
LLM_API_KEY=your_aiml_api_key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_ENDPOINT=https://api.aimlapi.com
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=your_aiml_api_key
EMBEDDING_ENDPOINT=https://api.aimlapi.com
COGNEE_SKIP_CONNECTION_TEST=true

## Built With

- [Bright Data](https://brightdata.com) — Web scraping infrastructure
- [AIML API](https://aimlapi.com) — Claude AI access
- [Cognee](https://cognee.ai) — Agent memory
- [Streamlit](https://streamlit.io) — Frontend

## Hackathon

Built for **Web Data UNLOCKED** — Bright Data x Lablab.ai Hackathon, May 2026.