"""Local on-device enricher stub."""

import logging
import pathlib

from spectatordb.models import MediaType

from collector.enrichment.base import Enricher, EnrichmentResult

logger = logging.getLogger(__name__)


class LocalEnricher(Enricher):
    """On-device enricher using a local model.

    This is a stub awaiting a chosen model backend (e.g. CLIP for
    embeddings, a small VLM for descriptions).
    """

    def enrich(self, file: pathlib.Path, media_type: MediaType) -> EnrichmentResult:
        """Return an empty result; stub pending a real model backend."""
        logger.warning("LocalEnricher is a stub; returning empty result.")
        return EnrichmentResult()
