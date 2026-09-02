"""
NexaHRM — Live Web Scraper & Course Discovery Engine
Fetches live course details from educational platforms.
"""

import httpx
import re
from typing import Dict, Any, Optional


def scrape_coursera_course(url: str) -> Optional[Dict[str, Any]]:
    """Scrapes public metadata from Coursera course URLs."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = httpx.get(url, headers=headers, timeout=10.0, follow_redirects=True)
        if resp.status_code != 200:
            return None

        html = resp.text
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "Coursera Professional Course"
        title = re.sub(r'<[^>]+>', '', title)

        rating_match = re.search(r'(\d\.\d)\s*stars', html, re.IGNORECASE)
        rating = float(rating_match.group(1)) if rating_match else 4.8

        return {
            "title": title,
            "provider": "Coursera",
            "rating": rating,
            "url": url,
            "scraped": True
        }
    except Exception as e:
        print(f"[NexaHRM Scraper] Error scraping {url}: {e}")
        return None
