import pytest
from pathlib import Path
from src.ingest import InputIngester, IngestionError

def test_ingest_valid_text():
    ingester = InputIngester(min_word_count=10)
    sample = "IncuBrix is an AI-powered CreatorOps platform that unifies ideation, video editing, voice cloning, and social publishing into a single dashboard."
    res = ingester.ingest_text(sample, source_name="test_text")
    assert res["word_count"] > 10
    assert res["title"] != ""
    assert "IncuBrix" in res["cleaned_text"]

def test_ingest_empty_text():
    ingester = InputIngester()
    with pytest.raises(IngestionError, match="empty"):
        ingester.ingest_text("   \n\t  ")

def test_ingest_too_short_text():
    ingester = InputIngester(min_word_count=50)
    with pytest.raises(IngestionError, match="Minimum required"):
        ingester.ingest_text("Too short sample.")

def test_ingest_missing_file():
    ingester = InputIngester()
    with pytest.raises(IngestionError, match="not found"):
        ingester.ingest_file("non_existent_file_path.md")
