"""
Regression and Integration Tests for Content Engine Studio Orchestration.
Verifies that Content Engine delegates to Video Studio, Carousel Studio, and Image Studio.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from pathlib import Path

from src.server import app, GenerateRequest, run_generation_job, active_jobs

client = TestClient(app)


def test_content_engine_empty_input_rejected():
    resp = client.post("/api/generate", json={"input_text": ""})
    assert resp.status_code == 400
    assert "Source text or transcript cannot be empty" in resp.json()["detail"]


def test_content_engine_too_short_input_rejected():
    resp = client.post("/api/generate", json={"input_text": "One two three"})
    assert resp.status_code == 400
    assert "Source text is too short" in resp.json()["detail"]


@patch("src.server.call_ai_repurposing_model")
@patch("src.ad_video_maker.generate_animated_ad_video")
@patch("src.animated_svg_carousel.generate_and_render_animated_carousel")
@patch("src.ad_image.generate_poster")
def test_content_engine_studio_orchestration_flow(mock_poster, mock_carousel, mock_video, mock_gemini_call):
    # Mock AI repurposing model output
    mock_gemini_call.return_value = [
        {"format": "Short video", "hook": "Stop wasting creator time", "caption": "Streamline editing with AI", "script": "Stop wasting creator time. Use AI.", "content_pillar": "CreatorOps & Tool Consolidation", "hashtags": "#CreatorOps #Growth"},
        {"format": "Short video", "hook": "How 1 hour becomes 10 assets", "caption": "Turn 1 recording into 10 formats", "script": "Turn 1 recording into 10 formats seamlessly.", "content_pillar": "Repurposing Recipes", "hashtags": "#AI #Content"},
        {"format": "Short video", "hook": "The automated video pipeline", "caption": "Fast video production workflow", "script": "High quality video workflow with subtitles.", "content_pillar": "Prompt-to-Motion Video", "hashtags": "#Shorts"},
        {"format": "Carousel", "hook": "The 5-Step Creator Framework", "caption": "Swipe to master modern CreatorOps", "content_pillar": "CreatorOps & Tool Consolidation", "slides": [{"title": "Step 1", "body": "Ingest"}, {"title": "Step 2", "body": "Cut"}]},
        {"format": "Carousel", "hook": "Repurposing Breakdown", "caption": "1 podcast into 10 assets", "content_pillar": "Repurposing Recipes", "slides": [{"title": "A", "body": "Record"}, {"title": "B", "body": "Distribute"}]},
        {"format": "Graphic", "hook": "Why Creators Burn Out", "caption": "Too many disconnected SaaS tools", "content_pillar": "CreatorOps & Tool Consolidation", "graphic_headline": "Why Creators Burn Out", "graphic_subtitle": "Too many disconnected SaaS tools"},
        {"format": "Graphic", "hook": "Consolidated Distribution", "caption": "Reach YouTube, IG, and FB simultaneously", "content_pillar": "Multi-Platform Syndication", "graphic_headline": "Consolidated Distribution", "graphic_subtitle": "Reach 3 platforms at once"},
        {"format": "Graphic", "hook": "Automated Subtitles", "caption": "Chirp 3 HD voice with synced captions", "content_pillar": "Voice & Audio Intelligence", "graphic_headline": "Automated Subtitles", "graphic_subtitle": "High fidelity audio & captions"},
        {"format": "Graphic", "hook": "Growth Velocity", "caption": "Publish 30 days of content in 1 afternoon", "content_pillar": "Growth Analytics", "graphic_headline": "Growth Velocity", "graphic_subtitle": "30 days in 1 afternoon"},
        {"format": "Graphic", "hook": "Next Gen CreatorOps", "caption": "Try IncuBrix for free today", "content_pillar": "CreatorOps & Tool Consolidation", "graphic_headline": "Next Gen CreatorOps", "graphic_subtitle": "Start free today"},
    ]

    # Mock studio generators
    mock_video.return_value = {
        "video_path": "assets/final/videos/INC-VID-010.mp4",
        "voice": "Puck",
        "director_model": "Gemini Director",
        "duration": 14.5,
        "scenes_count": 2
    }
    mock_carousel.return_value = {
        "status": "success",
        "pdf_path": "assets/final/carousels/INC-CAR-001/INC-CAR-001.pdf",
        "slides": 5
    }
    mock_poster.return_value = {
        "posters": [{
            "svg": "assets/final/graphics/INC-PST-001.svg",
            "png": "assets/final/graphics/INC-PST-001.png",
            "brief": "assets/final/graphics/INC-PST-001.brief.json"
        }]
    }

    job_id = "test_job_studio_orchestration"
    active_jobs[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "progress": 0,
        "stage": "Starting",
        "generated_assets": []
    }

    req = GenerateRequest(
        title="Testing Studio Integration Pipeline",
        source_type="transcript",
        tone="Energetic, Technical",
        input_text="The 2026 Solo Creator Bottleneck: Why solo creators are burning out in 2026 is not because they lack brilliant ideas. It is because for every 1 hour of recording, they spend 14 hours wrestling with formatting, transcription, audio sync, thumbnail creation, and context switching across Descript, Opus Clip, and Buffer.",
        platforms=["YouTube Shorts", "Facebook Pages", "Instagram"]
    )

    run_generation_job(job_id, req)

    job_res = active_jobs[job_id]
    assert job_res["status"] == "completed"
    assert job_res["progress"] == 100
    assets = job_res["generated_assets"]
    assert len(assets) == 10

    # Verify that Video Studio, Carousel Studio, and Image Studio were each called
    assert mock_video.call_count == 3
    assert mock_carousel.call_count == 2
    assert mock_poster.call_count == 5

    # Check videos
    for v in assets[:3]:
        assert v["media_type"] == "video"
        assert "Video Studio" in v["tools_used"]
        assert "Chirp 3 HD" in v["tools_used"]
        assert v["final_file_url"].endswith(".mp4")

    # Check carousels
    for c in assets[3:5]:
        assert c["media_type"] == "carousel"
        assert "Carousel Studio" in c["tools_used"]
        assert c["final_file_url"].endswith(".pdf")

    # Check graphics
    for g in assets[5:]:
        assert g["media_type"] == "graphic"
        assert "Image Studio" in g["tools_used"]
        assert g["final_file_url"].endswith(".png")
