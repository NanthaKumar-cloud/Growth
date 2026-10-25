import csv
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.pipeline import ContentEnginePipeline
from src.generator import ContentGenerator, GenerationError
from src.exporter import OFFICIAL_COLUMNS

def test_pipeline_export_structure(tmp_path):
    pipeline = ContentEnginePipeline()
    sample_text = """# Test Title
IncuBrix is an AI-powered CreatorOps platform that unifies ideation, video editing, voice cloning, and social publishing into a single dashboard.
It cuts weekly production time from 14 hours down to 2 hours by automating repurposing.
Creators can schedule directly to Facebook Pages, Instagram, and YouTube Shorts from one screen.
With unified analytics, creators can track their Creator Growth Score without switching tabs.
This comprehensive case study demonstrates that engineering-driven creator workflows consistently outperform fragmented tool subscriptions.
"""

    mock_assets = [
        {
            "platform": "facebook",
            "format": "text_post",
            "content_pillar": "CreatorOps & Tool Consolidation",
            "hook": "Stop wasting 12 hours on video editing.",
            "caption": "IncuBrix cuts production from 14h to 2h.",
            "cta": "Try IncuBrix free today.",
            "target_metric": "Impressions",
        },
        {
            "platform": "youtube",
            "format": "short_video",
            "content_pillar": "Repurposing Recipes",
            "hook": "How to edit video in 60 seconds with text",
            "caption": "[Visual: screen recording of prompt editor] Just edit text and the video updates automatically.",
            "cta": "Link in description.",
            "target_metric": "Retention",
        }
    ]

    with patch.object(pipeline.generator, "generate_campaign_assets", return_value=mock_assets):
        results = pipeline.run(input_source=sample_text, asset_count=2, render_media=False)
        assert results["assets_generated"] == 2
        assert Path(results["calendar_csv_path"]).exists()

        # Verify all 23 official columns are in the CSV
        with open(results["calendar_csv_path"], mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            assert header == OFFICIAL_COLUMNS

def test_pipeline_failure_recovery():
    generator = ContentGenerator()
    input_data = {
        "title": "Failure Recovery Test Case",
        "cleaned_text": "IncuBrix is an AI-powered CreatorOps platform that unifies ideation, video editing, voice cloning, and social publishing into a single dashboard. It cuts weekly production time from 14 hours down to 2 hours by automating repurposing." * 3
    }

    mock_success_response = MagicMock()
    mock_success_response.text = '{"assets": [{"platform": "facebook", "format": "text_post", "content_pillar": "CreatorOps", "hook": "Recovered hook", "caption": "Recovered caption", "cta": "Try IncuBrix"}]}'
    mock_success_response.usage_metadata = MagicMock(prompt_token_count=100, candidates_token_count=50)

    # Simulate attempt 1 throwing a 503 Network Timeout, then attempt 2 succeeding
    with patch.object(
        generator.client.models,
        "generate_content",
        side_effect=[Exception("503 Service Unavailable Transient Network Timeout"), mock_success_response]
    ):
        assets = generator.generate_campaign_assets(input_data, count=1, max_retries=2)
        assert len(assets) == 1
        assert assets[0]["hook"] == "Recovered hook"
