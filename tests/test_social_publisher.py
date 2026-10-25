"""
Unit tests for IncuBrix Social Publisher and Autonomous Scheduler.
"""

import pytest
from pathlib import Path
from src.social_publisher import SocialPublisher
from src.scheduler import AutonomousScheduler
from src.server import load_manifest, save_manifest


def test_publisher_initialization():
    pub = SocialPublisher(
        fb_page_id="1387253494470730",
        fb_token="test_token",
        ig_user_id="28816582671333644",
        ig_token="test_ig_token",
        yt_client_id="test_yt_id",
    )
    assert pub.fb_page_id == "1387253494470730"
    assert pub.ig_user_id == "28816582671333644"
    assert pub.yt_client_id == "test_yt_id"


def test_publish_youtube_short_metadata(tmp_path):
    pub = SocialPublisher(simulate=True)
    video_file = tmp_path / "test_short.mp4"
    video_file.write_bytes(b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41")

    res = pub.publish_youtube_short(
        video_path=video_file,
        title="Automate Your Creator Workflow",
        description="Save 12 hours a week with IncuBrix",
    )
    assert res["status"] == "success"
    assert res["platform"] == "YouTube Shorts"
    assert "#Shorts" in res["title"]
    assert "https://youtube.com/shorts/" in res["published_url"]


def test_publish_youtube_video_standard(tmp_path):
    pub = SocialPublisher(simulate=True)
    video_file = tmp_path / "test_standard.mp4"
    video_file.write_bytes(b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41")

    res = pub.publish_youtube_video(
        video_path=video_file,
        title="Full IncuBrix AI Content Engine Walkthrough",
        description="Comprehensive architecture and automation guide",
        is_short=False,
    )
    assert res["status"] == "success"
    assert res["platform"] == "YouTube Video"
    assert "#Shorts" not in res["title"]
    assert "https://www.youtube.com/watch?v=" in res["published_url"]
    assert res["is_short"] is False


def test_publish_instagram_carousel_simulation():
    pub = SocialPublisher(simulate=True)
    res = pub.publish_instagram_carousel(
        slide_urls=["https://example.com/s1.png", "https://example.com/s2.png"],
        caption="Swipe through the growth guide",
    )
    assert res["status"] == "success"
    assert res["platform"] == "Instagram"
    assert res["slides_count"] == 2
    assert "https://www.instagram.com/p/" in res["published_url"]


def test_publish_facebook_carousel_simulation(tmp_path):
    pub = SocialPublisher(simulate=True)
    f1 = tmp_path / "slide1.png"
    f2 = tmp_path / "slide2.png"
    f1.write_bytes(b"\x89PNG\r\n\x1a\n")
    f2.write_bytes(b"\x89PNG\r\n\x1a\n")

    res = pub.publish_facebook_carousel(
        image_paths=[f1, f2],
        message="5 Growth Pillars for B2B SaaS",
    )
    assert res["status"] == "success"
    assert res["platform"] == "Facebook"
    assert res["slides_count"] == 2


def test_publish_asset_dispatcher(monkeypatch):
    pub = SocialPublisher(simulate=True)
    assets = load_manifest()
    assert len(assets) > 0
    test_asset = assets[0]
    aid = test_asset["asset_id"]

    res = pub.publish_asset(aid, target_platform="Facebook")
    assert res["status"] == "success"
    assert res["asset_id"] == aid
    assert res["primary_url"] != ""


    # Verify manifest was updated
    updated_assets = load_manifest()
    matching = [a for a in updated_assets if a["asset_id"] == aid][0]
    assert matching["status"] == "Published"
    assert matching["test_published_url"] != ""


def test_autonomous_scheduler_cadence():
    sched = AutonomousScheduler(check_interval_seconds=10)
    batch = sched.generate_periodic_content_batch(count=3)
    assert len(batch) == 3
    assert any(b["format"] == "Short video" for b in batch)
    assert any(b["format"] == "Carousel" for b in batch)
    assert any("Graphic" in b["format"] for b in batch)

    status = sched.get_status()
    assert status["queued_scheduled_count"] >= 3
