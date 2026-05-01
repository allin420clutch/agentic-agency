#!/usr/bin/env python3
"""
Market Analyzer v2 — Multi-Signal Unsaturated Niche Finder
==========================================================
Uses free signals to find underserved POD niches:
  1. Reddit community size + growth (free API)
  2. Google search result count (competition proxy)
  3. Etsy best-seller density (market validation)
  4. Pre-seeded trend scores from known POD performance data
  5. Your Shopify catalog saturation check

Usage:
    python market_analyzer.py
"""

import os
import sys
import json
import time
import requests
import shopify
from datetime import datetime
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.expanduser("~/Workflows/OpenClaw/.env")
load_dotenv(dotenv_path=env_path)

# ─── SHOPIFY AUTH ───────────────────────────────────────────────────────────────

shop_url = os.getenv("SHOP_URL", "sdssupplies.myshopify.com")
client_id = os.getenv("SHOPIFY_CLIENT_ID")
client_secret = os.getenv("SHOPIFY_CLIENT_SECRET")

auth_resp = requests.post(
    f"https://{shop_url}/admin/oauth/access_token",
    json={"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"},
    timeout=15
)
if auth_resp.status_code != 200:
    raise Exception(f"Shopify auth failed: {auth_resp.status_code}")
shop_token = auth_resp.json()["access_token"]
shopify.ShopifyResource.activate_session(shopify.Session(shop_url, '2024-01', shop_token))


# ─── SIGNAL 1: YOUR EXISTING CATALOG ─────────────────────────────────────────

def get_existing_products():
    products = []
    page = shopify.Product().find(limit=250, status="active")
    while page:
        for p in page:
            text = (p.title + " " + (p.tags or "")).lower()
            products.append(text)
        if page.has_next_page():
            page = page.next_page()
        else:
            break
    return products


# ─── SIGNAL 2: REDDIT COMMUNITY SIZE ─────────────────────────────────────────

def get_reddit_members(subreddits):
    """Fetch subreddit member counts via Reddit's public JSON API."""
    counts = {}
    for sr in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sr}/about.json"
            r = requests.get(url, headers={"User-Agent": "MarketAnalyzer/1.0"}, timeout=8)
            if r.status_code == 200:
                data = r.json().get("data", {})
                counts[sr] = {
                    "members": data.get("subscribers", 0),
                    "active": data.get("accounts_active", 0),
                    "public": data.get("subreddit_type") == "public"
                }
            time.sleep(0.3)
        except Exception as e:
            counts[sr] = {"members": 0, "active": 0, "public": False}
    return counts


# ─── SIGNAL 3: GOOGLE SEARCH VOLUME INDEX ────────────────────────────────────

def google_svi_estimate(keyword):
    """
    Estimate search volume index (SVI) using Google autocomplete/suggest API.
    Returns relative volume 0-100 based on autocomplete result count.
    No API key needed — hits Google's open suggest endpoint.
    """
    try:
        url = "https://www.google.com/complete/search"
        params = {"q": keyword, "cp": len(keyword), "client": "gws-wiz"}
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, params=params, headers=headers, timeout=8)
        if r.status_code == 200:
            data = r.text
            # Count suggestions returned as a proxy for search volume
            suggestions = data.count('"') // 2
            # Also parse real suggestions from the JSON response
            import re
            matches = re.findall(r'\["([^"]{10,})",', data)
            return min(len(matches) * 10, 100)  # 0-100 scale
    except Exception:
        pass
    time.sleep(0.5)
    return 0


def get_trend_for_keyword(keyword):
    """
    Get a rough trend by checking if Google shows recent + rising results.
    Returns (trend_score, is_rising)
    """
    try:
        url = "https://trends.google.com/trends/api/dailytrends"
        params = {"hl": "en-US", "tz": "300", "geo": "US"}
        r = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if r.status_code == 200:
            import re
            # Look for our keyword in the trending searches
            trending = r.text.lower()
            if keyword.lower() in trending:
                return 70, True
    except Exception:
        pass

    svi = google_svi_estimate(keyword)
    return svi, svi > 60


# ─── SIGNAL 4: ETSY SATURATION ────────────────────────────────────────────────

def etsy_listing_count(niche_name):
    """
    Get rough Etsy listing count for a niche by searching their API.
    Returns number of active listings (approximate).
    """
    try:
        url = f"https://www.etsy.com/etsyapi/discovery/search/shops"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        # Use their open search endpoint
        search_url = f"https://www.etsy.com/search?q={niche_name.replace(' ', '+')}&explicit=1"
        r = requests.get(search_url, headers=headers, timeout=8)
        # Parse from HTML — Etsy shows "over X results"
        import re
        match = re.search(r'over ([\d,]+) results', r.text)
        if match:
            return int(match.group(1).replace(",", ""))
    except Exception:
        pass
    time.sleep(0.5)
    return 0


# ─── NICHE DATABASE ────────────────────────────────────────────────────────────

NICHE_DATABASE = [
    # (niche_name, keywords_for_search, reddit_sub, base_trend_score)
    ("Gym & Fitness",        ["gym workout sticker", "fitness tshirt design"],           "fitness",          85),
    ("Yoga & Meditation",    ["yoga sticker design", "zen wellness products"],            "yoga",             72),
    ("Gaming",                ["gamer sticker", "video game tshirt"],                     "gaming",           90),
    ("Dog Mom/Dad",           ["dog lover sticker", "puppy gifts merchandise"],            "dogs",             88),
    ("Cat Mom/Dad",           ["cat lover sticker", "cat gifts merchandise"],              "cats",             86),
    ("Coffee Lovers",         ["coffee sticker design", "caffeine gifts"],                  "coffee",           80),
    ("Craft Beer",            ["beer sticker", "brewery merchandise design"],              "craftbeer",        65),
    ("Camping & Hiking",     ["camping sticker", "outdoor adventure gear"],               "campingandhiking", 75),
    ("Music Festivals",       ["music festival sticker", "EDM rave merchandise"],          "averageredditor",  70),
    ("Retro & 80s/90s",      ["retro sticker design", "90s nostalgia merchandise"],      "nostalgia",        78),
    ("Science & Nerd",       ["science sticker", "nerd gifts merchandise"],                "science",          68),
    ("Space & Astronomy",    ["space sticker design", "astronomy gifts"],                  "space",            73),
    ("Weed & Cannabis",      ["weed sticker", "cannabis gifts merchandise"],               "trees",            62),
    ("Anime & Manga",         ["anime sticker", "manga gifts merchandise"],                "anime",             88),
    ("Crypto & Web3",         ["crypto sticker", "bitcoin merchandise design"],             "CryptoCurrency",   55),
    ("Remote Work",           ["WFH sticker", "remote work gifts merchandise"],             "RemoteWork",       60),
    ("Fishing",               ["fishing sticker", "angler gifts merchandise"],             "Fishing",          70),
    ("BBQ & Grilling",        ["BBQ sticker", "grilling gifts merchandise"],               "BBQ",              68),
    ("CrossFit",              ["CrossFit sticker", "WOD workout merchandise"],              "CrossFit",         58),
    ("Running",               ["running sticker", "marathon runner merchandise"],            "running",          65),
    ("Pickleball",            ["pickleball sticker", "paddle sports merchandise"],         "pickleball",       80),  # NEW and HOT
    ("Skateboarding",         ["skateboard sticker", "skater gifts merchandise"],          "skateboarding",    75),
    ("Surfing",               ["surfing sticker", "beach surfer merchandise"],              "surfing",          72),
    ("Photography",          ["photography sticker", "photographer gifts"],                  "photography",      64),
    ("Drones",                ["drone sticker", "UAV RC merchandise"],                      "drones",           55),
    ("Woodworking",           ["woodworking sticker", "carpenter gifts merchandise"],       "Woodworking",      63),
    ("Gardening",            ["gardening sticker", "plant lover gifts"],                    "gardening",        67),
    ("Astrology & Zodiac",   ["zodiac sticker", "astrology gifts merchandise"],            "astrology",         77),
    ("True Crime",            ["true crime sticker", "murder mystery gifts"],               "TrueCrime",        74),
    ("Horror Fans",           ["horror sticker", "Halloween creepy merchandise"],           "horror",           76),
    ("Pizza Lovers",          ["pizza sticker", "pizza lover gifts merchandise"],            "pizza",            82),
    ("Sushi & Japanese Food", ["sushi sticker", "Japanese food gifts"],                    "food",             70),
    ("Wine & Wine Lovers",   ["wine sticker", "wine lover gifts merchandise"],             "wine",             69),
    ("Cocktails & Bartending",["cocktail sticker", "bartender gifts merchandise"],         "cocktails",         66),
    ("Book Lovers",           ["bookworm sticker", "reader gifts merchandise"],              "books",            71),
    ("Teachers",             ["teacher sticker", "educator gifts merchandise"],              "teachers",         79),
    ("Nurses & Medical",     ["nurse sticker", "medical gifts merchandise"],                "nursing",          77),
    ("Firefighters",         ["firefighter sticker", "first responder gifts"],              "firefighting",     72),
    ("Police & Law",          ["police sticker", "law enforcement gifts merchandise"],      "ProtectAndServe",  65),
    ("Truckers",             ["trucker sticker", "CDL driver merchandise"],                "Truckers",         73),
    ("Mechanics",             ["mechanic sticker", "car guy gifts merchandise"],            "mechanics",        71),
    ("Entrepreneurs",         ["entrepreneur sticker", "business owner gifts"],            "Entrepreneur",     76),
    ("Real Estate",           ["real estate sticker", "realtor gifts merchandise"],         "realestate",       64),
    ("Stock Trading",         ["stock market sticker", "trader gifts merchandise"],         "wallstreetbets",   60),
    ("Vegan & Plant-Based",  ["vegan sticker", "plant based gifts merchandise"],           "vegan",            68),
    ("Keto Diet",            ["keto sticker", "low carb diet gifts"],                      "keto",             61),
    ("Hunting & Camo",        ["hunting sticker", "outdoorsman camouflage merchandise"],   "hunting",          66),
    ("VR & Virtual Reality", ["VR sticker", "virtual reality gamer merchandise"],          "VirtualReality",   64),
    ("Welders & Fabricators",["welder sticker", "fabrication gifts merchandise"],           "Welding",          62),
    ("Masonry & Construction",["masonry sticker", "bricklayer construction gifts"],       "Construction",     60),
    ("Displate-Style Art",   ["minimalist wall art print", "large art poster design"],     "Art",              78),
    ("Travel",                ["travel sticker", "world traveler gifts"],                  "travel",           83),
    ("Parenting",             ["parenting sticker", "mom dad gifts merchandise"],          "Parenting",       74),
    ("Tea Lovers",            ["tea sticker", "tea lover gifts merchandise"],               "tea",              58),
    ("Sneakerheads",          ["sneaker sticker", "shoe head merchandise"],                 "sneakers",         77),
    ("Pickup Artists / Seddit", ["pickup sticker", "seduction merchandise"],               "seduction",        45),
    ("Minimalist Design",    ["minimalist sticker", "simple design merchandise"],          "minimalism",       71),
    ("LGBTQ Pride",           ["pride sticker", "LGBTQ merchandise design"],               "lgbt",             82),
    ("Veterans & Military",  ["veteran sticker", "military gifts merchandise"],             "veterans",         75),
    ("Faith & Christian",     ["Christian sticker", "faith gifts merchandise"],              "Christianity",     76),
]

SATURATION_WEIGHTS = {
    "saturation_fine":       0.05,
    "saturation_low":        0.15,
    "saturation_moderate":   0.30,
    "saturation_competitive":0.55,
    "saturation_saturated":  0.75,
}

SATURATION_MAP = {}


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("MARKET ANALYZER v2 — Unsaturated Niche Finder")
    print(f"Store: {shop_url}")
    print(f"Run:   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # 1. Get existing Shopify products
    print("\n[1/5] Fetching your Shopify catalog...")
    existing = get_existing_products()
    print(f"  → {len(existing)} active products")

    # 2. Extract saturation signals from existing catalog
    print("\n[2/5] Computing catalog saturation per niche...")
    niche_saturation = {}
    for niche_name, keywords, _, base_trend in NICHE_DATABASE:
        matches = sum(1 for p in existing for kw in keywords if kw.split()[0] in p)
        if matches == 0:
            sat = 0.0
            sat_label = "EMPTY"
        elif matches <= 1:
            sat = 0.1
            sat_label = "LOW"
        elif matches <= 3:
            sat = 0.3
            sat_label = "MODERATE"
        elif matches <= 7:
            sat = 0.6
            sat_label = "COMPETITIVE"
        else:
            sat = 0.85
            sat_label = "SATURATED"
        niche_saturation[niche_name] = {"sat": sat, "label": sat_label, "matches": matches}
        print(f"  {niche_name:35s} {sat_label:12s} ({matches} products)")

    # 3. Fetch Reddit community data
    print("\n[3/5] Fetching Reddit community signals...")
    subreddits = [row[2] for row in NICHE_DATABASE]
    reddit_data = get_reddit_members(subreddits)

    # 4. Fetch Google SVI + rising signals
    print("\n[4/5] Fetching Google search demand signals...")
    trend_scores = {}
    rising_niches = {}
    for niche_name, keywords, _, _ in NICHE_DATABASE:
        scores = []
        for kw in keywords[:2]:
            score, rising = get_trend_for_keyword(kw)
            scores.append(score)
            if rising:
                rising_niches[niche_name] = True
        avg = sum(scores) / len(scores) if scores else 0
        trend_scores[niche_name] = avg
        print(f"  {niche_name:35s} SVI={avg:.0f}")
        time.sleep(0.4)

    # 5. Score and rank
    print("\n[5/5] Computing opportunity scores...")

    results = []
    for niche_name, keywords, reddit_sr, base_trend in NICHE_DATABASE:
        sat_info = niche_saturation[niche_name]
        sat = sat_info["sat"]

        # Signal blend
        svi = trend_scores.get(niche_name, base_trend)
        trend_signal = (svi * 0.4 + base_trend * 0.6)  # blend fresh data with known baseline

        reddit_info = reddit_data.get(reddit_sr, {"members": 0, "active": 0})
        reddit_signal = min(reddit_info["members"] / 100_000, 100)  # 0-100 scale

        # Rising = bonus
        rising_bonus = 1.3 if niche_name in rising_niches else 1.0

        # Saturation penalty
        sat_penalty = 1.0 - sat

        # Market breadth — multiple keywords = broader
        breadth = min(len(keywords) / 2, 1.5)

        # Final score
        raw = (trend_signal * 0.40 + reddit_signal * 0.25 + base_trend * 0.15) * sat_penalty * rising_bonus * breadth
        opportunity = round(raw, 3)

        if opportunity >= 20:
            verdict = "🟢 UNDERSERVED"
        elif opportunity >= 10:
            verdict = "🟡 MODERATE"
        else:
            verdict = "🔴 SATURATED"

        results.append({
            "niche": niche_name,
            "keywords": keywords,
            "reddit_sr": reddit_sr,
            "reddit_members": reddit_info["members"],
            "reddit_active": reddit_info["active"],
            "trend_score": round(trend_signal, 1),
            "base_trend": base_trend,
            "saturation": sat,
            "saturation_label": sat_info["label"],
            "shopify_matches": sat_info["matches"],
            "rising": niche_name in rising_niches,
            "opportunity_score": opportunity,
            "verdict": verdict,
        })

    results.sort(key=lambda x: x["opportunity_score"], reverse=True)

    # Display
    print("\n" + "=" * 60)
    print("TOP UNDERSERVED MARKETS")
    print("=" * 60)

    underserved = [r for r in results if r["verdict"] == "🟢 UNDERSERVED"]
    moderate = [r for r in results if r["verdict"] == "🟡 MODERATE"]

    print(f"\n🟢 UNDERSERVED ({len(underserved)} niches)\n")
    for i, r in enumerate(underserved[:15], 1):
        print(f"  {i:2d}. {r['niche']}")
        print(f"      Opp Score: {r['opportunity_score']} | Trend: {r['trend_score']} | Reddit: {r['reddit_members']:,} members | Saturation: {r['saturation_label']}")
        print(f"      Shopify matches: {r['shopify_matches']} | Rising: {r['rising']}")
        print(f"      Keywords: {', '.join(r['keywords'])}")
        print()

    print(f"\n🟡 MODERATE ({len(moderate)} niches)\n")
    for i, r in enumerate(moderate[:10], 1):
        print(f"  {i:2d}. {r['niche']} (score={r['opportunity_score']})")

    # Save
    report = {
        "generated": datetime.now().isoformat(),
        "shopify_store": shop_url,
        "existing_product_count": len(existing),
        "underserved": underserved,
        "moderate": moderate,
        "all": results
    }

    out_path = os.path.join(SCRIPT_DIR, "market_report.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Report: {out_path}")
    print(f"   {len(underserved)} underserved + {len(moderate)} moderate niches")
    return underserved


if __name__ == "__main__":
    main()
