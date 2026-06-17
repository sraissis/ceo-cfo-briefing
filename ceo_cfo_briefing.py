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
    # European Commission
    "https://ec.europa.eu/commission/presscorner/api/rss",
    # Les Echos (French Financial)
    "https://feeds.lesechos.fr/lesechos-finance",
    # Handelsblatt (German Financial)
    "https://www.handelsblatt.com/contentexport/feed/schlagzeilen",
    # El Economista (Spanish Financial)
    "https://www.eleconomista.es/rss/rss-mercados-financieros.php",
    # Börsen-Zeitung (German Markets)
    "https://www.boersen-zeitung.de/rss",
    # Private Equity International
    "https://www.privateequityinternational.com/feed/",
    # Mergermarket
    "https://www.mergermarket.com/rss",
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

def generate_briefing(articles):
    articles_text = ""
    for i, a in enumerate(articles, 1):
        articles_text += f"""
Article {i}: {a['title']}
URL: {a['link']}
Published: {a.get('published', 'N/A')}
Content: {a.get('summary', 'No content available')}
---"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a senior market analyst preparing a confidential daily briefing for the CEO and CFO of Open Gate Capital, a global private equity firm specializing in industrial corporate carve-outs across North America and Europe.

Open Gate Capital's CURRENT UNREALIZED portfolio companies are:
- Aluminium Solutions Group (France) — aluminium extrusion, building/construction/transport sectors
- Annex Cloud (USA) — SaaS customer loyalty platform
- CoreMedia AG (Germany) — digital experience and web content management software
- Duraco (USA) — specialty tapes, labels, and coated films
- Fichet Security Solutions (Europe) — security doors, safes, vaults, cash handling
- Hufcor (USA) — operable partitions for hotels, convention centers, schools
- Integrity Partners Group (USA) — specialty chemical distribution
- Jøtul (Norway) — cast iron stoves and fireplaces, consumer heating
- Kongsberg Precision Cutting Systems (Europe) — digital cutting systems for packaging and signage
- Mersive Technologies (USA) — meeting collaboration software
- Sargent and Greenleaf (USA) — high security locks and access control
- ScioTeq (Europe/USA) — visualization solutions for air traffic control and defense
- TREALITY (USA/Europe) — simulation visual display systems
- Total Safety EMEA (latest acquisition, April 2026) — industrial safety services

Open Gate Capital focuses on: chemicals and minerals, packaging, paper and specialty materials, diversified industrials, metals, building products, aerospace and defense, automotive, business and industrial services. The firm is actively expanding its European presence while maintaining a strong US portfolio. It specializes in corporate carve-outs and divestitures in the lower middle market.

Today is {datetime.now().strftime('%A, %B %d, %Y')}.

Below are {len(articles)} articles from major financial news sources gathered this morning.

{articles_text}

Please provide a concise executive briefing covering exactly these six sections. The CEO and CFO should be able to read this in under 2 minutes. Use short bullet points only — no paragraphs, no full sentences where possible.

Do not include a title, header, or date at the top. Start directly with section 1.

Do not use any Markdown formatting such as **, *, #, or ##. Do not use double asterisks around any text.

For section headers use ALL CAPS only — no special characters around them.
For sub-headers within sections use ALL CAPS followed by a colon, like this: US: or EUROPE:

Keep each section tight and scannable:
- Sections 1, 2, 4, 5 and 6: maximum 4-6 bullet points total
- Section 3 (Industrials): up to 10 bullet points, grouped by subsector

1. MACRO SNAPSHOT
- Key market moves: US and European indices, rates, FX, oil
- Fed/ECB/BoE policy signals
- Any macro data releases today

2. DEAL MARKET CONDITIONS
- M&A and PE deal flow — volume, valuations, financing conditions
- Corporate carve-out and divestiture activity
- European deal market specifically

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
- Any notable US credit market developments affecting PE financing

EUROPE:
- European leveraged finance and syndicated loan market conditions
- European private credit and direct lending activity
- ECB policy impact on credit markets
- Any notable European credit developments affecting cross-border deals

6. ACTIONABLE INTELLIGENCE FOR OPEN GATE CAPITAL
Based on this week's news, identify 3-5 specific near-term actions directly tied to OpenGate's current unrealized portfolio companies listed above. These should be things the team can act on or investigate this week — not long term strategy.

Frame each as a direct recommendation tied to a specific portfolio company or sector:
- "CHECK IN WITH [portfolio company] on..." 
- "MONITOR [portfolio company] exposure to..."
- "EXPLORE whether [portfolio company] can benefit from..."
- "REVIEW [portfolio company] position given..."
- "CONSIDER add-on acquisition for [portfolio company] given..."

Be specific — reference actual news from today's articles where possible.

At the very end of the briefing, after all six sections, include a single consolidated sources list like this:

SOURCES:
- Article Title: article url

Include every article you referenced anywhere in the briefing, but list each one only once. Do not put sources under individual sections."""
            }
        ]
    )
    return response.content[0].text

def send_email(briefing):
    html_content = f"""<html>
<body style="font-family: Georgia, serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #1a1a1a;">
<div style="background-color: #0C1C3E; padding: 30px;">
<h1 style="color: #ffffff; margin: 0; font-size: 24px;">EXECUTIVE MARKET BRIEFING</h1>
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
        "subject": f"Executive Market Briefing — {datetime.now().strftime('%B %d, %Y')}"
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
    print(f"\n{'='*60}")
    print(f"  CEO/CFO Briefing — {datetime.now().strftime('%B %d, %Y %I:%M %p')}")
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

schedule.every().day.at("08:30").do(run_morning_briefing)

if __name__ == "__main__":
    print("CEO/CFO briefing agent started.")
    run_morning_briefing()
    while True:
        schedule.run_pending()
        time.sleep(60)