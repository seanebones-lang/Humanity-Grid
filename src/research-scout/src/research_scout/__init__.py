"""
Research Scout - Base configuration and shared utilities.
"""

from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Keys
    ncbi_api_key: str | None = Field(default=None, alias="NCBI_API_KEY")
    semantic_scholar_api_key: str | None = Field(default=None, alias="SEMANTIC_SCHOLAR_API_KEY")
    google_patents_api_key: str | None = Field(default=None, alias="GOOGLE_PATENTS_API_KEY")

    # Paths
    data_dir: Path = Field(default=Path("data"), alias="DATA_DIR")
    cache_dir: Path = Field(default=Path("cache"), alias="CACHE_DIR")
    output_dir: Path = Field(default=Path("output"), alias="OUTPUT_DIR")

    # Ingestion
    pubmed_max_results: int = Field(default=10000, alias="PUBMED_MAX_RESULTS")
    biorxiv_max_results: int = Field(default=5000, alias="BIORXIV_MAX_RESULTS")
    arxiv_max_results: int = Field(default=5000, alias="ARXIV_MAX_RESULTS")
    request_timeout: float = Field(default=30.0, alias="REQUEST_TIMEOUT")
    rate_limit_per_sec: float = Field(default=3.0, alias="RATE_LIMIT_PER_SEC")

    # ML Models
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    llm_model: str = Field(default="microsoft/phi-3-mini-4k-instruct", alias="LLM_MODEL")
    device: str = Field(default="cpu", alias="DEVICE")  # cpu, cuda, mps

    # Hypothesis Generation
    min_evidence_papers: int = Field(default=3, alias="MIN_EVIDENCE_PAPERS")
    max_hypotheses_per_run: int = Field(default=50, alias="MAX_HYPOTHESES_PER_RUN")

    # Review Queue
    review_webhook_url: str | None = Field(default=None, alias="REVIEW_WEBHOOK_URL")


settings = Settings()


def ensure_dirs() -> None:
    """Ensure all configured directories exist."""
    for dir_path in [settings.data_dir, settings.cache_dir, settings.output_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)


# Paper data model
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json


@dataclass
class Paper:
    """Represents a scientific paper with extracted metadata."""

    paper_id: str  # PMID, DOI, arXiv ID, etc.
    source: str  # "pubmed", "biorxiv", "arxiv", "patents"
    title: str
    abstract: str | None = None
    authors: list[str] = field(default_factory=list)
    journal: str | None = None
    publication_date: datetime | None = None
    doi: str | None = None
    url: str | None = None
    keywords: list[str] = field(default_factory=list)
    mesh_terms: list[str] = field(default_factory=list)
    chemicals: list[str] = field(default_factory=list)
    # Extracted entities
    proteins: list[str] = field(default_factory=list)
    genes: list[str] = field(default_factory=list)
    diseases: list[str] = field(default_factory=list)
    compounds: list[str] = field(default_factory=list)
    pathways: list[str] = field(default_factory=list)
    # Computed
    embedding: list[float] | None = None
    cited_by: list[str] = field(default_factory=list)
    cites: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat() if v else None
            elif isinstance(v, Path):
                d[k] = str(v)
            else:
                d[k] = v
        return d

    @classmethod
    def from_dict(cls, data: dict) -> Paper:
        """Create Paper from dictionary."""
        data = data.copy()
        if data.get("publication_date"):
            data["publication_date"] = datetime.fromisoformat(data["publication_date"])
        return cls(**data)

    def to_jsonl(self) -> str:
        """Serialize to JSONL line."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class CitationEdge:
    """Represents a citation relationship between papers."""

    citing_paper_id: str
    cited_paper_id: str
    citation_type: str = "cites"  # cites, cites_as_background, cites_as_method, etc.
    confidence: float = 1.0

    def to_dict(self) -> dict:
        return self.__dict__.copy()