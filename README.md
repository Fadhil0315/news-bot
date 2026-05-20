# 🛢️ Geo News Bot

> Automated geopolitical & oil market intelligence for Indian OMC investors — delivered to Telegram.


---

## Overview

Geo News Bot is a fully autonomous intelligence pipeline that monitors global energy and geopolitical news, filters it for relevance to **Indian Oil Marketing Companies (OMCs)**, and delivers concise investor-grade briefs directly to Telegram.

Tracked stocks: **IOC · HPCL · BPCL**

The bot watches:

- Strait of Hormuz developments
- Iran / US geopolitical escalation
- Brent crude price direction
- Oil supply disruptions & shipping events
- OPEC decisions & global energy news
- India fuel pricing signals

---

## Why This Exists

Indian OMC stocks are highly sensitive to crude oil volatility, shipping disruptions, sanctions, and fuel pricing policy. Most retail investors rely on fragmented sources — random headlines, Twitter noise, delayed YouTube summaries.

This project builds a **focused, automated, always-on intelligence layer** that:

- Filters signal from noise
- Explains *what* happened, *why* it matters, and *how* it affects OMC stocks
- Runs autonomously in the cloud — no babysitting required

---

## Pipeline Architecture

```
High-quality energy RSS feeds
        │
        ▼
 Relevance Filtering          ← domain keywords (oil, brent, hormuz, iran ...)
        │
        ▼
 Article Content Extraction   ← full article body, not just headlines
        │
        ▼
 Market Context Injection     ← live Brent price + daily trend via Yahoo Finance
        │
        ▼
 AI Synthesis (Groq / Llama)  ← analyst persona: IOC, HPCL, BPCL focus
        │
        ▼
 Duplicate Detection          ← skips repeat cycles, emits NO_SIGNAL if needed
        │
        ▼
 Telegram Delivery            ← morning brief + continuous monitoring
```

### Stage Details

| Stage | Description |
|---|---|
| **News Collection** | Ingests RSS from Reuters (Business, World, Top) and OilPrice |
| **Relevance Filtering** | Keyword-based filter drops unrelated articles before LLM ingestion |
| **Article Extraction** | Fetches full article body via `trafilatura`; removes HTML noise |
| **Market Context** | Pulls live Brent crude price and trend from Yahoo Finance (`yfinance`) |
| **AI Synthesis** | Groq-hosted Llama 3.3 70B synthesises findings as a macro/energy analyst |
| **State Memory** | Title-based deduplication prevents repeat alerts across cycles |
| **Telegram Delivery** | Sends formatted intelligence reports; suppresses low-signal cycles |

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.10+ |
| Scheduling | GitHub Actions |
| RSS Parsing | `feedparser` |
| Article Extraction | `trafilatura` |
| Market Data | `yfinance` |
| LLM | Groq API — `llama-3.3-70b-versatile` |
| Delivery | Telegram Bot API |
| Config | `python-dotenv` |

---

## Getting Started

### Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com/)
- A Telegram bot token and chat ID ([how to create a bot](https://core.telegram.org/bots#how-do-i-create-a-bot))

### 1. Clone the repository

```bash
git clone https://github.com/your-username/geo-news-bot.git
cd geo-news-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 4. Run locally

```bash
python bot.py
```

---

## Deployment (GitHub Actions)

The bot is designed to run autonomously on GitHub Actions — no server required.

### Setup

1. Fork this repository.
2. Go to **Settings → Secrets and variables → Actions**.
3. Add the following secrets:

| Secret | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |
| `TELEGRAM_CHAT_ID` | Target chat or channel ID |

4. GitHub Actions will automatically run the workflow on the configured schedule.

### Schedule

The workflow runs:

- **Morning** — strategic brief to start the trading day
- **Throughout the day** — recurring monitoring cycles
- **Duplicate suppression** — emits `NO_SIGNAL` instead of repeating known developments

To customise the schedule, edit `.github/workflows/bot.yml`:

```yaml
on:
  schedule:
    - cron: '30 3 * * 1-5'   # Morning brief (IST ~9:00 AM, weekdays)
    - cron: '0 */2 * * 1-5'  # Every 2 hours during market hours
```

---

## Configuration

### Relevance Keywords

Edit the keyword list in `bot.py` (or your config file) to tune filtering:

```python
KEYWORDS = [
    "oil", "brent", "wti", "crude",
    "hormuz", "iran", "opec", "sanctions",
    "shipping", "lpg", "petrol", "diesel",
    "india", "ioc", "bpcl", "hpcl",
    "trump", "refinery", "supply"
]
```

### RSS Sources

Current sources (configurable):

```python
RSS_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/Reuters/worldNews",
    "https://feeds.reuters.com/reuters/topNews",
    "https://oilprice.com/rss/main",
]
```

---

## Sample Output

```
📊 OMC INTELLIGENCE BRIEF — 09:15 IST

🛢️ BRENT: $83.40 (+0.8% today)

🔴 HORMUZ WATCH: Heightened vessel inspection activity reported near
the strait following escalatory rhetoric from Tehran. Transit risk
elevated. Historical precedent suggests ~$3–5 Brent premium in
sustained blockade scenarios.

⚠️ OMC IMPACT: Refinery input costs likely to face upward pressure
if disruption extends beyond 48hrs. HPCL most exposed given
import profile. IOC partially hedged via existing term contracts.

📌 SIGNAL: CAUTIOUS — monitor for confirmation before directional
positioning on OMC names.
```

---

## Project Philosophy

> **Better models are useless without better inputs.**

Early versions of this bot passed only RSS headlines to the LLM. The outputs were weak because headlines are often vague and context-free.

The key architectural insight was:

```
headline-only  →  full article extraction + market context + relevance filtering
```

Every stage of the pipeline exists to maximise **signal per token** — delivering the LLM the cleanest, most relevant context possible before synthesis.

---

## Roadmap

- [ ] Semantic duplicate detection (embedding-based)
- [ ] Sentiment scoring per article
- [ ] Urgency / severity classification
- [ ] Brent movement short-term forecasting signal
- [ ] OMC-specific impact scoring engine
- [ ] Historical event memory across sessions
- [ ] Push alert severity levels (🟢 🟡 🔴)
- [ ] Macroeconomic trend tracking

---

## Disclaimer

This project is for **educational and research purposes only**.

It is not financial advice. Always conduct your own research before making investment decisions.

---

## License

[MIT](LICENSE)
