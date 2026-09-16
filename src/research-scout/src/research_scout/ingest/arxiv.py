"""
arXiv ingestion module.
"""

from __future__ import annotations

import asyncio
import re
from datetime import datetime
from typing import Optional

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from research_scout import Paper, settings


ARXIV_API = "http://export.arxiv.org/api/query"


class ArxivClient:
    """Async client for arXiv API."""

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
        category: str | None = None,
    ) -> list[Paper]:
        """Search arXiv for papers matching query."""
        all_papers = []
        start = 0
        page_size = 100  # arXiv max per request

        # Build search query
        search_query = query
        if category:
            search_query = f"cat:{category} AND ({query})"

        while len(all_papers) < max_results:
            params = {
                "search_query": search_query,
                "start": start,
                "max_results": min(page_size, max_results - len(all_papers)),
                "sortBy": "relevance",
                "sortOrder": "descending",
            }

            logger.debug(f"Fetching arXiv page start={start}")
            response = await self._rate_limited_request(ARXIV_API, params)
            papers = self._parse_atom_response(response.text)

            if not papers:
                break

            all_papers.extend(papers)

            if len(papers) < page_size:
                break

            start += page_size

        logger.info(f"Found {len(all_papers)} arXiv papers matching '{query}'")
        return all_papers

    def _parse_atom_response(self, xml_text: str) -> list[Paper]:
        """Parse arXiv Atom XML response into Paper objects."""
        import xml.etree.ElementTree as ET

        papers = []
        # arXiv uses Atom namespace
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            logger.error(f"Failed to parse arXiv XML: {e}")
            return papers

        for entry in root.findall("atom:entry", ns):
            paper = self._parse_entry(entry, ns)
            if paper:
                papers.append(paper)

        return papers

    def _parse_entry(self, entry: ET.Element, ns: dict) -> Optional[Paper]:
        """Parse a single arXiv entry."""
        try:
            # arXiv ID
            id_elem = entry.find("atom:id", ns)
            if id_elem is None or not id_elem.text:
                return None
            arxiv_url = id_elem.text.strip()
            arxiv_id = arxiv_url.split("/abs/")[-1]  # Extract ID from URL
            # Remove version suffix if present
            arxiv_id = re.sub(r"v\d+$", "", arxiv_id)

            # Title
            title_elem = entry.find("atom:title", ns)
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

            # Abstract
            summary_elem = entry.find("atom:summary", ns)
            abstract = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else None

            # Authors
            authors = []
            for author in entry.findall("atom:author", ns):
                name_elem = author.find("atom:name", ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())

            # Publication date
            pub_date = None
            published_elem = entry.find("atom:published", ns)
            if published_elem is not None and published_elem.text:
                try:
                    pub_date = datetime.fromisoformat(published_elem.text.replace("Z", "+00:00"))
                except ValueError:
                    pass

            # Categories
            categories = []
            for cat in entry.findall("atom:category", ns):
                term = cat.get("term")
                if term:
                    categories.append(term)

            # DOI
            doi = None
            for link in entry.findall("atom:link", ns):
                if link.get("title") == "doi" and link.get("href"):
                    doi = link.get("href").replace("https://doi.org/", "")
                    break

            return Paper(
                paper_id=arxiv_id,
                source="arxiv",
                title=title,
                abstract=abstract,
                authors=authors,
                journal="arXiv",
                publication_date=pub_date,
                doi=doi,
                url=f"https://arxiv.org/abs/{arxiv_id}",
                keywords=categories,
            )

        except Exception as e:
            logger.error(f"Failed to parse arXiv entry: {e}")
            return None

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


async def ingest_arxiv(
    query: str,
    max_results: int = 5000,
    category: str | None = None,
    output_path: Optional[str] = None,
) -> list[Paper]:
    """High-level function to search and fetch papers from arXiv."""
    async with ArxivClient() as client:
        papers = await client.search(query, max_results, category)

        if output_path:
            with open(output_path, "w") as f:
                for paper in papers:
                    f.write(paper.to_jsonl() + "\n")
            logger.info(f"Saved {len(papers)} papers to {output_path}")

        return papers


if __name__ == "__main__":
    import sys

    async def main():
        query = sys.argv[1] if len(sys.argv) > 1 else "molecular dynamics"
        max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        category = sys.argv[3] if len(sys.argv) > 3 else None

        papers = await ingest_arxiv(query, max_results, category, "data/arxiv_papers.jsonl")
        print(f"Fetched {len(papers)} papers")

    asyncio.run(main())