"""
PubMed/NCBI E-utilities ingestion module.
"""

from __future__ import annotations

import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import AsyncIterator, Optional
from urllib.parse import urlencode

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from research_scout import Paper, settings


BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ESEARCH = f"{BASE_URL}/esearch.fcgi"
EFETCH = f"{BASE_URL}/efetch.fcgi"
ELINK = f"{BASE_URL}/elink.fcgi"


class PubMedClient:
    """Async client for NCBI E-utilities API."""

    def __init__(self, api_key: Optional[str] = None, rate_limit: float = 3.0):
        self.api_key = api_key or settings.ncbi_api_key
        self.rate_limit = rate_limit
        self._semaphore = asyncio.Semaphore(int(rate_limit))
        self._last_request = 0.0
        self.client = httpx.AsyncClient(timeout=settings.request_timeout)

    async def _rate_limited_request(self, url: str, params: dict) -> httpx.Response:
        """Make a rate-limited request."""
        async with self._semaphore:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_request
            min_interval = 1.0 / self.rate_limit
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)

            params = params.copy()
            if self.api_key:
                params["api_key"] = self.api_key

            response = await self._request_with_retry(url, params)
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
        max_results: int = 10000,
        database: str = "pubmed",
        sort: str = "relevance",
    ) -> list[str]:
        """Search PubMed and return list of PMIDs."""
        params = {
            "db": database,
            "term": query,
            "retmax": min(max_results, 10000),
            "retmode": "json",
            "sort": sort,
            "usehistory": "y",
        }

        logger.info(f"Searching PubMed: {query} (max={max_results})")
        response = await self._rate_limited_request(ESEARCH, params)
        data = response.json()

        id_list = data.get("esearchresult", {}).get("idlist", [])
        logger.info(f"Found {len(id_list)} PMIDs")
        return id_list

    async def fetch_details(self, pmids: list[str], database: str = "pubmed") -> list[Paper]:
        """Fetch full paper details for a list of PMIDs."""
        if not pmids:
            return []

        # Process in chunks of 200 (NCBI limit)
        chunk_size = 200
        all_papers = []

        for i in range(0, len(pmids), chunk_size):
            chunk = pmids[i : i + chunk_size]
            params = {
                "db": database,
                "id": ",".join(chunk),
                "retmode": "xml",
                "rettype": "abstract",
            }

            logger.debug(f"Fetching details for {len(chunk)} PMIDs")
            response = await self._rate_limited_request(EFETCH, params)
            papers = self._parse_efetch_xml(response.text)
            all_papers.extend(papers)

        return all_papers

    async def fetch_citations(self, pmids: list[str], database: str = "pubmed") -> dict[str, list[str]]:
        """Fetch citation relationships (cited by / cites)."""
        if not pmids:
            return {}

        params = {
            "db": database,
            "id": ",".join(pmids),
            "cmd": "neighbor",
            "linkname": f"{database}_{database}_citedin",  # cited by
            "retmode": "json",
        }

        response = await self._rate_limited_request(ELINK, params)
        data = response.json()

        cited_by = {}
        for linkset in data.get("linksets", []):
            pmid = linkset.get("ids", [None])[0]
            if pmid:
                cited_by[pmid] = [str(l) for l in linkset.get("linksetdbs", [{}])[0].get("links", [])]

        return cited_by

    def _parse_efetch_xml(self, xml_text: str) -> list[Paper]:
        """Parse EFetch XML response into Paper objects."""
        papers = []

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            logger.error(f"Failed to parse EFetch XML: {e}")
            return papers

        for article in root.findall(".//PubmedArticle"):
            paper = self._parse_article(article)
            if paper:
                papers.append(paper)

        return papers

    def _parse_article(self, article_elem: ET.Element) -> Optional[Paper]:
        """Parse a single PubmedArticle element."""
        try:
            # PMID
            pmid_elem = article_elem.find(".//PMID")
            if pmid_elem is None or not pmid_elem.text:
                return None
            pmid = pmid_elem.text.strip()

            # Title
            title_elem = article_elem.find(".//ArticleTitle")
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

            # Abstract
            abstract_text = ""
            for abstract_elem in article_elem.findall(".//Abstract/AbstractText"):
                label = abstract_elem.get("Label", "")
                text = abstract_elem.text or ""
                if label:
                    abstract_text += f"{label}: {text}\n"
                else:
                    abstract_text += f"{text}\n"
            abstract = abstract_text.strip() or None

            # Authors
            authors = []
            for author in article_elem.findall(".//Author"):
                last = author.find("LastName")
                fore = author.find("ForeName")
                initials = author.find("Initials")
                if last is not None and last.text:
                    name = last.text.strip()
                    if fore is not None and fore.text:
                        name = f"{fore.text.strip()} {name}"
                    elif initials is not None and initials.text:
                        name = f"{initials.text.strip()} {name}"
                    authors.append(name)

            # Journal
            journal_elem = article_elem.find(".//Journal/Title")
            journal = journal_elem.text.strip() if journal_elem is not None and journal_elem.text else None

            # Publication date
            pub_date = None
            pub_date_elem = article_elem.find(".//PubDate")
            if pub_date_elem is not None:
                year = pub_date_elem.find("Year")
                month = pub_date_elem.find("Month")
                day = pub_date_elem.find("Day")
                try:
                    y = int(year.text) if year is not None and year.text else 1900
                    m = self._parse_month(month.text) if month is not None and month.text else 1
                    d = int(day.text) if day is not None and day.text else 1
                    pub_date = datetime(y, m, d)
                except (ValueError, TypeError):
                    pass

            # DOI
            doi = None
            for id_elem in article_elem.findall(".//ArticleId"):
                if id_elem.get("IdType") == "doi" and id_elem.text:
                    doi = id_elem.text.strip()
                    break

            # Keywords
            keywords = []
            for kw in article_elem.findall(".//Keyword"):
                if kw.text:
                    keywords.append(kw.text.strip())

            # MeSH terms
            mesh_terms = []
            for mesh in article_elem.findall(".//MeshHeading/DescriptorName"):
                if mesh.text:
                    mesh_terms.append(mesh.text.strip())

            # Chemicals/Substances
            chemicals = []
            for chem in article_elem.findall(".//Chemical/NameOfSubstance"):
                if chem.text:
                    chemicals.append(chem.text.strip())

            # URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            return Paper(
                paper_id=pmid,
                source="pubmed",
                title=title,
                abstract=abstract,
                authors=authors,
                journal=journal,
                publication_date=pub_date,
                doi=doi,
                url=url,
                keywords=keywords,
                mesh_terms=mesh_terms,
                chemicals=chemicals,
            )

        except Exception as e:
            logger.error(f"Failed to parse article: {e}")
            return None

    def _parse_month(self, month_str: str) -> int:
        """Parse month string to integer."""
        month_map = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        }
        return month_map.get(month_str[:3].lower(), 1)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


async def ingest_pubmed(
    query: str,
    max_results: int = 10000,
    output_path: Optional[str] = None,
) -> list[Paper]:
    """High-level function to search and fetch papers from PubMed."""
    async with PubMedClient() as client:
        pmids = await client.search(query, max_results)
        papers = await client.fetch_details(pmids)

        if output_path:
            import json
            with open(output_path, "w") as f:
                for paper in papers:
                    f.write(paper.to_jsonl() + "\n")
            logger.info(f"Saved {len(papers)} papers to {output_path}")

        return papers


if __name__ == "__main__":
    import sys

    async def main():
        query = sys.argv[1] if len(sys.argv) > 1 else "KRAS G12C"
        max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 100

        papers = await ingest_pubmed(query, max_results, "data/papers.jsonl")
        print(f"Fetched {len(papers)} papers")

    asyncio.run(main())