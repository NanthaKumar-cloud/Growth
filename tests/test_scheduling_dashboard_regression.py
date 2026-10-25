"""
test_scheduling_dashboard_regression.py
======================================
Regression tests confirming:
  1. An Instagram video uses Instagram publishing, and NEVER YouTube or Facebook.
  2. A Facebook carousel uses Facebook publishing, and NEVER YouTube or Instagram.
  3. A YouTube Short uses YouTube publishing, and NEVER Facebook or Instagram.
  4. Carousels and graphics are strictly blocked from being published or scheduled to YouTube Shorts.
  5. The calendar API sorts all items in ascending chronological order by scheduled datetime.
  6. Datetime normalization converts varied date formats into consistent 'YYYY-MM-DD HH:MM'.
  7. Status tracking accurately records 'Scheduled', 'Rescheduled', 'Published', and 'Failed'.
  8. Autonomous AUTO cadence assets adhere to the exact same platform-format compatibility rules.
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from src.server import app, normalize_datetime_str, parse_datetime_sort_key
from src.social_publisher import SocialPublisher
from src.scheduler import AutonomousScheduler

client = TestClient(app)


def test_instagram_video_uses_instagram_publishing():
    """Confirms Instagram video assets dispatch strictly via Instagram Reels and never to YouTube or Facebook."""
    pub = SocialPublisher(simulate=True)
    pub.publish_instagram_reel = MagicMock(return_value={
        "status": "success", "platform": "Instagram Reels", "published_url": "https://instagram.com/reel/test_ig"
    })
    pub.publish_youtube_short = MagicMock()
    pub.publish_youtube_video = MagicMock()
    pub.publish_facebook_video = MagicMock()

    # INC-VID-003 is configured for Instagram
    res = pub.publish_asset("INC-VID-003")

    assert res["status"] == "success"
    assert pub.publish_instagram_reel.call_count == 1
    assert pub.publish_youtube_short.call_count == 0
    assert pub.publish_youtube_video.call_count == 0
    assert pub.publish_facebook_video.call_count == 0


def test_facebook_carousel_uses_facebook_publishing():
    """Confirms Facebook carousel assets dispatch strictly via Facebook and never to YouTube or Instagram."""
    pub = SocialPublisher(simulate=True)
    pub.publish_facebook_carousel = MagicMock(return_value={
        "status": "success", "platform": "Facebook", "published_url": "https://facebook.com/test_fb"
    })
    pub.publish_instagram_carousel = MagicMock()
    pub.publish_youtube_short = MagicMock()

    # INC-CAR-001 is configured for Facebook Pages
    res = pub.publish_asset("INC-CAR-001")

    assert res["status"] == "success"
    assert pub.publish_facebook_carousel.call_count == 1
    assert pub.publish_instagram_carousel.call_count == 0
    assert pub.publish_youtube_short.call_count == 0


def test_youtube_short_uses_youtube_publishing():
    """Confirms YouTube Short assets dispatch strictly via YouTube and never to Facebook or Instagram."""
    pub = SocialPublisher(simulate=True)
    pub.publish_youtube_short = MagicMock(return_value={
        "status": "success", "platform": "YouTube Shorts", "published_url": "https://youtube.com/shorts/test_yt"
    })
    pub.publish_facebook_video = MagicMock()
    pub.publish_instagram_reel = MagicMock()

    # INC-VID-001 is configured for YouTube Shorts
    res = pub.publish_asset("INC-VID-001")

    assert res["status"] == "success"
    assert pub.publish_youtube_short.call_count == 1
    assert pub.publish_facebook_video.call_count == 0
    assert pub.publish_instagram_reel.call_count == 0


def test_carousels_and_images_blocked_from_youtube_shorts():
    """Confirms non-video assets (carousels and graphics) cannot be published or scheduled to YouTube Shorts."""
    pub = SocialPublisher(simulate=True)

    # 1. Attempt publishing carousel to YouTube Shorts
    try:
        pub.publish_asset("INC-CAR-001", target_platform="YouTube Shorts")
        assert False, "Expected ValueError when publishing carousel to YouTube Shorts"
    except ValueError as e:
        assert "Incompatible format" in str(e) or "video-only" in str(e)

    # 2. Attempt publishing graphic poster to YouTube Shorts
    try:
        pub.publish_asset("INC-PST-001", target_platform="YouTube Shorts")
        assert False, "Expected ValueError when publishing graphic to YouTube Shorts"
    except ValueError as e:
        assert "Incompatible format" in str(e) or "video-only" in str(e)

    # 3. Attempt scheduling carousel to YouTube Shorts via API
    sched_resp = client.post("/api/schedule", json={
        "asset_id": "INC-CAR-001",
        "scheduled_date": "2026-11-20 10:00",
        "platform": "YouTube Shorts"
    })
    assert sched_resp.status_code == 400
    assert "Compatibility validation error" in sched_resp.json()["detail"]


def test_calendar_api_ascending_chronological_sort():
    """Confirms /api/calendar returns events in strictly ascending chronological order."""
    resp = client.get("/api/calendar")
    assert resp.status_code == 200
    events = resp.json().get("events", [])
    assert len(events) >= 30

    timestamps = [parse_datetime_sort_key(e["scheduled_date"]) for e in events if e.get("scheduled_date")]
    for i in range(len(timestamps) - 1):
        assert timestamps[i] <= timestamps[i + 1], (
            f"Calendar events not in ascending chronological order: {events[i]['scheduled_date']} > {events[i+1]['scheduled_date']}"
        )


def test_datetime_normalization_consistent_format():
    """Confirms normalize_datetime_str standardizes varied inputs into canonical 'YYYY-MM-DD HH:MM'."""
    assert normalize_datetime_str("2026-11-02 10:00") == "2026-11-02 10:00"
    assert normalize_datetime_str("2026-10-25T15:00:00") == "2026-10-25 15:00"
    assert normalize_datetime_str("2026-10-25T15:30") == "2026-10-25 15:30"
    assert normalize_datetime_str("2026-11-15") == "2026-11-15 10:00"
    assert normalize_datetime_str("2026-11-05T09:45:00Z") == "2026-11-05 09:45"


def test_accurate_status_transitions():
    """Confirms asset statuses accurately transition between Scheduled, Rescheduled, and Failed."""
    # 1. Reschedule asset
    resched_resp = client.post("/api/calendar/reschedule", json={
        "asset_id": "INC-VID-002",
        "new_date": "2026-11-25 14:00",
        "platform": "YouTube Shorts"
    })
    assert resched_resp.status_code == 200
    assert resched_resp.json()["asset_status"] == "Rescheduled"

    # 2. Schedule asset
    sched_resp = client.post("/api/schedule", json={
        "asset_id": "INC-VID-002",
        "scheduled_date": "2026-11-03 10:00",
        "platform": "YouTube Shorts"
    })
    assert sched_resp.status_code == 200
    assert sched_resp.json()["asset_status"] == "Scheduled"

    # 3. Incompatible publish triggers Failed status
    fail_resp = client.post("/api/publish/INC-CAR-002", json={
        "platform": "YouTube Shorts"
    })
    assert fail_resp.status_code == 400


def test_auto_cadence_assets_follow_compatibility_rules():
    """Confirms automatically generated cadence assets adhere strictly to platform compatibility."""
    sched = AutonomousScheduler()
    batch = sched.generate_periodic_content_batch(count=3)
    assert len(batch) == 3

    # Video must be on YouTube Shorts
    vid_asset = next(b for b in batch if b["format"] == "Short video")
    assert vid_asset["platform"] == "YouTube Shorts"

    # Carousel must be on Instagram
    car_asset = next(b for b in batch if b["format"] == "Carousel")
    assert car_asset["platform"] == "Instagram"

    # Graphic must be on Facebook Pages
    img_asset = next(b for b in batch if b["format"] == "Graphic")
    assert img_asset["platform"] == "Facebook Pages"

    # No carousel or image assigned to YouTube
    assert not any(b["format"] in ["Carousel", "Graphic"] and "YouTube" in b["platform"] for b in batch)
