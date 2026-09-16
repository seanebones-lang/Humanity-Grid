"""
bioRxiv ingestion module.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Optional

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from research_scout import Paper, settings


BIORXIV_API = "https://api.biorxiv.org"
DETAILS_ENDPOINT = f"{BIORXIV_API}/details/biorxiv"
SEARCH_ENDPOINT = f"{BIORXIV_API}/details/biorxiv"


class BioRxivClient:
    """Async client for bioRxiv API."""

    def __init__(self, rate_limit: float = 3.0):
        self.rate_limit = rate_limit
        self._semaphore = asyncio.Semaphore(int(rate_limit))
        self._last_request = 0.0
        self.client = httpx.AsyncClient(timeout=settings.request_timeout)

    async def _rate_limited_request(self, url: str, params: dict = None) -> httpx.Response:
        """Make a rate-limited request."""
        async with self._semaphore:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_request
            min_interval = 1.0 / self.rate_limit
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)

            response = await self._request_with_retry(url, params or {})
            self._last_request = asyncio.get_event_loop().time()
            return response

    @retry(
        wait=wait_exponential_jitter(initial=1, max=30),
        stop=stop_after_attempt(3),
    )
    async def _request_with_retry(self, url: str, params: dict) -> httpx.Response:
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response

    async def search(
        self,
        query: str,
        max_results: int = 5000,
        date_from: str = "2020-01-01",
        date_to: str | None = None,
    ) -> list[Paper]:
        """Search bioRxiv for papers matching query."""
        # bioRxiv API uses date range + cursor pagination
        # For simplicity, we'll fetch recent papers and filter locally
        # In production, use their advanced search

        all_papers = []
        cursor = 0
        page_size = 100

        while len(all_papers) < max_results:
            params = {
                "format": "json",
                "limit": page_size,
                "cursor": cursor,
            }

            if date_to:
                url = f"{DETAILS_ENDPOINT}/{date_from}/{date_to}"
            else:
                url = f"{DETAILS_ENDPOINT}/{date_from}"

            logger.debug(f"Fetching bioRxiv page cursor={cursor}")
            response = await self._rate_limited_request(url, params)
            data = response.json()

            collection = data.get("collection", [])
            if not collection:
                break

            for item in collection:
                paper = self._parse_biorxiv_item(item)
                if paper and self._matches_query(paper, query):
                    all_papers.append(paper)
                    if len(all_papers) >= max_results:
                        break

            # Check if there are more pages
            if len(collection) < page_size:
                break

            cursor += page_size

        logger.info(f"Found {len(all_papers)} bioRxiv papers matching '{query}'")
        return all_papers

    def _parse_biorxiv_item(self, item: dict) -> Optional[Paper]:
        """Parse bioRxiv API item into Paper."""
        try:
            doi = item.get("doi", "")
            if not doi:
                return None

            title = item.get("title", "").strip()
            abstract = item.get("abstract", "").strip() or None

            authors = []
            for author in item.get("authors", "").split("; "):
                if author.strip():
                    authors.append(author.strip())

            # Parse date
            pub_date = None
            date_str = item.get("date", "")
            if date_str:
                try:
                    pub_date = datetime.fromisoformat(date_str.split("T")[0])
                except ValueError:
                    pass

            # Category/subject
            category = item.get("category", "")
            keywords = [category] if category else []

            return Paper(
                paper_id=doi,
                source="biorxiv",
                title=title,
                abstract=abstract,
                authors=authors,
                journal="bioRxiv",
                publication_date=pub_date,
                doi=doi,
                url=f"https://www.biorxiv.org/content/{doi}v1",
                keywords=keywords,
            )

        except Exception as e:
            logger.error(f"Failed to parse bioRxiv item: {e}")
            return None

    def _matches_query(self, paper: Paper, query: str) -> bool:
        """Simple text matching against title and abstract."""
        query_lower = query.lower()
        search_text = f"{paper.title} {paper.abstract or ''}".lower()
        return query_lower in search_text

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


async def ingest_biorxiv(
    query: str,
    max_results: int = 5000,
    output_path: Optional[str] = None,
) -> list[Paper]:
    """High-level function to search and fetch papers from bioRxiv."""
    async with BioRxivClient() as client:
        papers = await client.search(query, max_results)

        if output_path:
            with open(output_path, "w") as f:
                for paper in papers:
                    f.write(paper.to_jsonl() + "\n")
            logger.info(f"Saved {len(papers)} papers to {output_path}")

        return papers


if __name__ == "__main__":
    import sys

    async def main():
        query = sys.argv[1] if len(sys.argv) > 1 else "cancer"
        max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 100

        papers = await ingest_biorxiv(query, max_results, "data/biorxiv_papers.jsonl")
        print(f"Fetched {len(papers)} papers")

    asyncio.run(main())