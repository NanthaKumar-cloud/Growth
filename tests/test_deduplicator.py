import pytest
from src.deduplicator import DuplicateDetector

def test_deduplicator_exact_duplicate():
    detector = DuplicateDetector()
    asset1 = {
        "asset_id": "INC-001",
        "hook": "Why you should stop paying $100/mo for 4 creator tools",
        "caption": "IncuBrix brings transcription, video clipping, and publishing into 1 dashboard."
    }
    asset2 = {
        "asset_id": "INC-002",
        "hook": "Why you should stop paying $100/mo for 4 creator tools",
        "caption": "IncuBrix brings transcription, video clipping, and publishing into 1 dashboard."
    }

    assert detector.is_duplicate(asset1) is False
    detector.register_asset(asset1)
    assert detector.is_duplicate(asset2) is True

def test_deduplicator_near_duplicate():
    detector = DuplicateDetector(similarity_threshold=0.80)
    asset1 = {
        "asset_id": "INC-001",
        "hook": "Why you should stop paying $100 every single month for four creator tools",
        "caption": "IncuBrix brings transcription, video clipping, and social publishing into one dashboard."
    }
    # Near duplicate with minor punctuation and word change
    asset2 = {
        "asset_id": "INC-002",
        "hook": "Why you should stop paying $100 every single month for 4 creator tools!",
        "caption": "IncuBrix brings transcription, video clipping, and social publishing into one single dashboard."
    }

    assert detector.is_duplicate(asset1) is False
    detector.register_asset(asset1)
    assert detector.is_duplicate(asset2) is True

def test_deduplicator_distinct_content():
    detector = DuplicateDetector()
    asset1 = {
        "asset_id": "INC-001",
        "hook": "Why you should stop paying $100/mo for 4 creator tools",
        "caption": "IncuBrix brings transcription and video clipping into one dashboard."
    }
    asset2 = {
        "asset_id": "INC-002",
        "hook": "How AI voice cloning turns text into natural podcast narration",
        "caption": "Train your voice model in 60 seconds and create multilingual audio clips."
    }

    assert detector.is_duplicate(asset1) is False
    detector.register_asset(asset1)
    assert detector.is_duplicate(asset2) is False
