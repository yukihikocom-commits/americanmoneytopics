import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def fetch_rss_articles(rss_feeds):
    articles = []
    for url in rss_feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                article = {
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:300],
                    "published": entry.get("published", ""),
                    "source": feed.feed.get("title", url),
                    "type": "rss",
                }
                if article["title"] and article["url"]:
                    articles.append(article)
        except Exception as e:
            logger.warning(f"RSSフィード取得失敗: {url} — {e}")
    logger.info(f"RSS収集完了: {len(articles)}件")
    return articles


def fetch_official_updates(official_urls):
    articles = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; OkaneNewsBot/1.0)"}
    for url in official_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            seen = set()
            for tag in soup.find_all(["h2", "h3", "h4"])[:15]:
                link = tag.find("a")
                title = tag.get_text(strip=True)
                href = link["href"] if link and link.get("href") else ""
                if not title or title in seen:
                    continue
                seen.add(title)
                if href and href.startswith("/"):
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    href = f"{parsed.scheme}://{parsed.netloc}{href}"
                articles.append({
                    "title": title,
                    "url": href or url,
                    "summary": "",
                    "published": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "source": url,
                    "type": "official",
                })
        except Exception as e:
            logger.warning(f"公式サイト取得失敗: {url} — {e}")
    logger.info(f"公式サイト収集完了: {len(articles)}件")
    return articles


def fetch_all(rss_feeds, official_urls):
    rss_articles = fetch_rss_articles(rss_feeds)
    official_articles = fetch_official_updates(official_urls)
    all_articles = rss_articles + official_articles
    logger.info(f"合計収集件数: {len(all_articles)}件")
    return all_articles
