import anthropic
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import schedule
import time
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
POWER_AUTOMATE_URL = "https://default0339ce75a7334289a58d95cd1c02b3.e6.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/f61cbe6b70b04ccbacb80384812d5594/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=d189pf6KyyxwljkS9aZjBqv-v0CxzfbZSz4cYvQ9YMw"

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ── News Sources ───────────────────────────────────────────────────────────────
RSS_FEEDS = [
    # Reuters
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/europeanFinancialNews",
    "https://feeds.reuters.com/reuters/mergersNews",
    "https://feeds.reuters.com/reuters/economy",
    # Wall Street Journal
    "https://feeds.wsj.com/wsj/xml/rss/3_7085.xml",
    # CNBC
    "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "https://www.cnbc.com/id/20910258/device/rss/rss.html",
    # Financial Times
    "https://www.ft.com/rss/home/uk",
    "https://www.ft.com/rss/home/europe",
    # MarketWatch
    "https://feeds.marketwatch.com/marketwatch/topstories",
    "https://feeds.marketwatch.com/marketwatch/marketpulse",
    # Seeking Alpha
    "https://seekingalpha.com/market_currents.xml",
    # Investing.com
    "https://www.investing.com/rss/news.rss",
    # Bloomberg
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://feeds.bloomberg.com/politics/news.rss",
    # The Economist
    "https://www.economist.com/finance-and-economics/rss.xml",
    "https://www.economist.com/business/rss.xml",
    "https://www.economist.com/europe/rss.xml",
    # Fortune
    "https://fortune.com/feed/fortune-feeds/?id=3230629",
    # Barron's
    "https://www.barrons.com/xml/rss/3_7510.xml",
    # Yahoo Finance
    "https://finance.yahoo.com/rss/",
    "https://finance.yahoo.com/news/rssindex",
    # Washington Post
    "https://feeds.washingtonpost.com/rss/business",
    # New York Times
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
    # ZeroHedge
    "https://feeds.feedburner.com/zerohedge/feed",
    # Axios
    "https://api.axios.com/feed/",
    # Nikkei Asia
    "https://asia.nikkei.com/rss/feed/nar",
    # Federal Reserve
    "https://www.federalreserve.gov/feeds/press_all.xml",
    # IMF
    "https://www.imf.org/en/News/rss?language=eng",
    # European Central Bank
    "https://www.ecb.europa.eu/rss/press.html",
    # Euronews Business
    "https://www.euronews.com/rss?format=mrss&level=theme&name=business",
    # Les Echos (French Financial)
    "https://feeds.lesechos.fr/lesechos-finance",
    # Handelsblatt (German Financial)
    "https://www.handelsblatt.com/contentexport/feed/schlagzeilen",
    # Private Equity International
    "https://www.privateequityinternational.com/feed/",
]

def fetch_articles(feeds, max_per_feed=5):
    articles = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                article = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                }
                articles.append(article)
        except Exception:
            continue
    return articles

def is_friday():
    return datetime.now().weekday() == 4

def generate_briefing(articles):
    articles_text = ""
    for i, a in enumerate(articles, 1):
        articles_text += f"""
Article {i}: {a['title']}
URL: {a['link']}
Published: {a.get('published', 'N/A')}
Content: {a.get('summary', 'No content available')}
---"""

    portfolio_context = """
IMPORTANT: The following is the COMPLETE and ACCURATE list of Open Gate Capital's CURRENT unrealized portfolio companies as of 2026. Do NOT reference any companies outside of this list when discussing portfolio holdings or actionable intelligence:

- Aluminium Solutions Group (France) — aluminium extrusion, building/construction/transport sectors. Formed from merger of Extol and Aluminium France Extrusion in 2022
- Annex Cloud (USA) — SaaS customer loyalty and retention platform
- CoreMedia AG (Germany) — digital experience and web content management software, headquartered in Hamburg
- Duraco (USA) — specialty tapes, labels, and coated films, headquartered in Forest Park, Illinois
- Fichet Security Solutions (Europe) — security doors, safes, vaults, cash handling, France/Belgium/Luxembourg
- Hufcor (USA) — operable partitions for hotels, convention centers, schools, global manufacturing
- Integrity Partners Group (USA) — specialty chemical distribution, headquartered in Roanoke, Virginia
- Kongsberg Precision Cutting Systems (Europe) — digital cutting systems for packaging and signage, global operations
- Mersive Technologies (USA) — meeting collaboration software, headquartered in Denver, Colorado
- Sargent and Greenleaf (USA) — high security locks and access control (note: security locking division sold to ASSA ABLOY December 2025, remaining business still held)
- TREALITY (USA/Europe) — simulation visual display systems, headquartered in Ohio
- Total Safety/Apex (acquired April 2026) — industrial safety services in Europe, Middle East and Africa

Open Gate Capital focuses on: chemicals and minerals, packaging, paper and specialty materials, diversified industrials, metals, building products, aerospace and defense, automotive, business and industrial services. The firm is actively expanding its European presence while maintaining a strong US portfolio. It specializes in corporate carve-outs and divestitures in the lower middle market."""

    if is_friday():
        prompt = f"""You are a senior market analyst preparing a confidential WEEKLY WRAP-UP briefing for the CEO and CFO of Open Gate Capital, a global private equity firm specializing in industrial corporate carve-outs across North America and Europe.

{portfolio_context}

Today is {datetime.now().strftime('%A, %B %d, %Y')} — end of week summary.

Below are {len(articles)} articles from major financial news sources gathered this week.

{articles_text}

Please provide a concise WEEKLY WRAP-UP covering these five sections. Use short bullet points only — no paragraphs, no full sentences where possible.

Do not include a title, header, or date at the top. Start directly with section 1.
Do not use any Markdown formatting such as **, *, #, or ##.
For section headers use ALL CAPS only.

TOP 3 HEADLINES THIS WEEK
- [Single line — most important story of the week]
- [Single line — second most important story]
- [Single line — third most important story]

1. MACRO RECAP — WEEK IN REVIEW
- Key market moves for the week: US and European indices, rates, FX, oil
- Most significant macro events or data releases this week
- Week-over-week change in sentiment vs last week

2. DEAL MARKET — WEEK IN REVIEW
- Notable M&A and PE transactions announced this week
- Corporate carve-out and divestiture activity this week
- Credit market conditions heading into next week

3. INDUSTRIALS — WEEK IN REVIEW
- Most important sector developments this week across OpenGate's sectors
- Supply chain, input cost, and demand signals
- Any major earnings or corporate events relevant to OpenGate's sectors

4. EUROPEAN MARKET — WEEK IN REVIEW
- Key European macro and political developments this week
- European industrial and M&A activity this week
- Currency movements and cross-border deal implications

5. LOOKING AHEAD — NEXT WEEK
- Key events, data releases, and catalysts to watch next week
- Any specific risks or opportunities OpenGate should prepare for
- 2-3 actionable items for the team to focus on next week tied to current portfolio companies

At the very end, include a single consolidated sources list:
SOURCES:
- Article Title: article url

Include every article referenced, listed once only."""

    else:
        prompt = f"""You are a senior market analyst preparing a confidential daily briefing for the CEO and CFO of Open Gate Capital, a global private equity firm specializing in industrial corporate carve-outs across North America and Europe.

{portfolio_context}

Today is {datetime.now().strftime('%A, %B %d, %Y')}.

Below are {len(articles)} articles from major financial news sources gathered this morning.

{articles_text}

Please provide a concise executive briefing covering exactly these six sections. The CEO and CFO should be able to read this in under 2 minutes. Use short bullet points only — no paragraphs, no full sentences where possible.

Do not include a title, header, or date at the top. Start directly with the Top 3 Headlines.
Do not use any Markdown formatting such as **, *, #, or ##.
For section headers use ALL CAPS only — no special characters around them.
For sub-headers within sections use ALL CAPS followed by a colon, like this: US: or EUROPE:

Keep each section tight and scannable:
- Sections 1, 2, 4, 5 and 6: maximum 4-6 bullet points total
- Section 3 (Industrials): up to 10 bullet points, grouped by subsector

TOP 3 HEADLINES
- [Single line — most critical thing to know today]
- [Single line — second most critical thing]
- [Single line — third most critical thing]

1. MACRO SNAPSHOT
- Key market moves: US and European indices, rates, FX, oil
- Fed/ECB/BoE policy signals
- Any macro data releases today
- WEEK-OVER-WEEK: note one key change in macro conditions vs last week

2. DEAL MARKET CONDITIONS
- M&A and PE deal flow — volume, valuations, financing conditions
- Corporate carve-out and divestiture activity
- European deal market specifically
- WEEK-OVER-WEEK: note one key change in deal conditions vs last week

3. INDUSTRIALS SECTOR WATCH
- News directly relevant to OpenGate's sectors: chemicals, specialty materials, building products, aerospace/defense, industrial technology, automotive
- Supply chain, input cost, and demand signals
- Group bullets by subsector where relevant

4. EUROPEAN MARKET FOCUS
- Key European macro and political developments
- European industrial and M&A activity
- Currency and cross-border deal implications
- Any news relevant to OpenGate's European portfolio companies

5. BANK CREDIT AND PRIVATE CREDIT
US:
- US leveraged lending conditions, spreads, issuance volumes
- US direct lending and private credit fund activity

EUROPE:
- European leveraged finance and syndicated loan market conditions
- European private credit and direct lending activity
- ECB policy impact on credit markets

6. ACTIONABLE INTELLIGENCE FOR OPEN GATE CAPITAL
Based on this week's news, identify 3-5 specific near-term actions directly tied to OpenGate's current unrealized portfolio companies listed above. These should be things the team can act on or investigate this week — not long term strategy.

Only reference companies from the current portfolio list above. Do not mention any realized or exited companies.

Frame each as a direct recommendation tied to a specific portfolio company:
- "CHECK IN WITH [portfolio company] on..."
- "MONITOR [portfolio company] exposure to..."
- "EXPLORE whether [portfolio company] can benefit from..."
- "REVIEW [portfolio company] position given..."
- "CONSIDER add-on acquisition for [portfolio company] given..."

At the very end of the briefing, after all six sections, include a single consolidated sources list:

SOURCES:
- Article Title: article url

Include every article you referenced anywhere in the briefing, but list each one only once. Do not put sources under individual sections."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.content[0].text

def send_email(briefing):
    is_friday_today = is_friday()
    subject_prefix = "Weekly Wrap-Up" if is_friday_today else "Executive Market Briefing"
    header_title = "WEEKLY MARKET WRAP-UP" if is_friday_today else "EXECUTIVE MARKET BRIEFING"

    html_content = f"""<html>
<body style="font-family: Georgia, serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #1a1a1a;">
<div style="background-color: #0C1C3E; padding: 30px;">
<h1 style="color: #ffffff; margin: 0; font-size: 24px;">{header_title}</h1>
<p style="color: #a8b8d8; margin: 8px 0 0 0; font-size: 16px;">{datetime.now().strftime('%A, %B %d, %Y')}</p>
<p style="color: #a8b8d8; margin: 4px 0 0 0; font-size: 13px;">Prepared for Open Gate Capital</p>
</div>
<div style="background-color: #ffffff; padding: 30px; border: 1px solid #e0d9d0;">
<pre style="white-space: pre-wrap; font-family: Georgia, serif; font-size: 15px; line-height: 1.8;">{briefing}</pre>
</div>
<p style="color: #888; font-size: 12px; text-align: center; margin-top: 20px;">Confidential — Generated by Open Gate Capital Market Intelligence Agent</p>
</body>
</html>"""

    payload = {
        "briefing": html_content,
        "subject": f"{subject_prefix} — {datetime.now().strftime('%B %d, %Y')}"
    }

    try:
        response = requests.post(
            POWER_AUTOMATE_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"CEO/CFO briefing sent! Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending briefing: {e}")

def run_morning_briefing():
    day_type = "Weekly Wrap-Up" if is_friday() else "Daily Briefing"
    print(f"\n{'='*60}")
    print(f"  CEO/CFO {day_type} — {datetime.now().strftime('%B %d, %Y %I:%M %p')}")
    print(f"{'='*60}\n")

    print("Fetching articles...")
    articles = fetch_articles(RSS_FEEDS, max_per_feed=4)
    print(f"Fetched {len(articles)} articles. Generating briefing...\n")

    briefing = generate_briefing(articles)
    print(briefing)

    filename = f"ceo_cfo_briefing_{datetime.now().strftime('%Y-%m-%d')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(briefing)
    print(f"\n[Saved to {filename}]")

    print("Sending to Power Automate...")
    send_email(briefing)

schedule.every().day.at("11:30").do(run_morning_briefing)

if __name__ == "__main__":
    print("CEO/CFO briefing agent started.")
    run_morning_briefing()
    while True:
        schedule.run_pending()
        time.sleep(60)