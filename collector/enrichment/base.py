"""Enrichment ABC and result dataclass."""

import abc
import pathlib

from dataclasses import dataclass, field

from spectatordb.models import MediaType


@dataclass
class EnrichmentResult:
    """Result of enriching a media file."""

    labels: list[str] = field(default_factory=list)
    description: str | None = None
    embedding: list[float] | None = None
    embedding_model: str | None = None


class Enricher(abc.ABC):
    """Abstract base class for media enrichment."""

    @abc.abstractmethod
    def enrich(self, file: pathlib.Path, media_type: MediaType) -> EnrichmentResult:
        """Enrich a media file with labels, description, and embedding.

        Parameters
        ----------
        file : pathlib.Path
            Path to the media file.
        media_type : MediaType
            Type of the media file.

        Returns
        -------
        EnrichmentResult
            The enrichment result.
        """
