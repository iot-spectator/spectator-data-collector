"""Tests for collector.enrichment."""

from spectatordb.models import MediaType

from collector.enrichment.local import LocalEnricher


def test_local_enricher_returns_empty(tmp_path):
    file = tmp_path / "test.jpg"
    file.write_bytes(b"\xff\xd8\xff\xe0")
    enricher = LocalEnricher()
    result = enricher.enrich(file, MediaType.IMAGE)
    assert result.labels == []
    assert result.description is None
    assert result.embedding is None
