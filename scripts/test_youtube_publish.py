#!/usr/bin/env python3
"""
test_youtube_publish.py
=======================
Tests publishing to YouTube Shorts and as normal video to YouTube using a
recently generated video file, confirming both publication formats work correctly.
"""

import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.social_publisher import SocialPublisher
from src.server import load_manifest, save_manifest


def main():
    print("=" * 70)
    print("IncuBrix YouTube Publishing Verification Test")
    print("=" * 70)

    # 1. Locate recently generated video
    recent_videos = [
        PROJECT_ROOT / "assets" / "final" / "videos" / "INC-VID-LIVE-528.mp4",
        PROJECT_ROOT / "assets" / "final" / "videos" / "INC-VID-LIVE-371.mp4",
        PROJECT_ROOT / "assets" / "final" / "videos" / "INC-VID-LIVE-171.mp4",
        PROJECT_ROOT / "assets" / "final" / "videos" / "INC-VID-001.mp4",
    ]

    target_video = None
    for v in recent_videos:
        if v.exists():
            target_video = v
            break

    if not target_video:
        print("[FAIL] No video files found in assets/final/videos/")
        sys.exit(1)

    print(f"[*] Using test video: {target_video.name} ({target_video.stat().st_size:,} bytes)")
    publisher = SocialPublisher()

    # -------------------------------------------------------------------------
    # TEST 1: Publish to YouTube Shorts
    # -------------------------------------------------------------------------
    print("\n--- TEST 1: Publish as YouTube Short (#Shorts 9:16 vertical) ---")
    shorts_title = "Stop Wasting 15h Weekly on SaaS Video Production"
    shorts_desc = "Automate your B2B creator pipeline with IncuBrix AI Content Engine."

    shorts_result = publisher.publish_youtube_short(
        video_path=target_video,
        title=shorts_title,
        description=shorts_desc,
        tags=["Shorts", "IncuBrix", "AI", "CreatorOps", "SaaSGrowth"],
    )

    print(f"Status:        {shorts_result.get('status')}")
    print(f"Platform:      {shorts_result.get('platform')}")
    print(f"Media Type:    {shorts_result.get('media_type')}")
    print(f"Title:         {shorts_result.get('title')}")
    print(f"Published URL: {shorts_result.get('published_url')}")
    print(f"Simulated:     {shorts_result.get('simulated', False)}")

    assert shorts_result.get("status") == "success", "Shorts publish status failed"
    assert shorts_result.get("platform") == "YouTube Shorts", "Platform mismatch"
    assert "#Shorts" in shorts_result.get("title", ""), "Missing #Shorts in title"
    assert "https://youtube.com/shorts/" in shorts_result.get("published_url", ""), "Invalid shorts URL format"
    print(">>> [PASS] YouTube Shorts publish verified successfully!")

    # -------------------------------------------------------------------------
    # TEST 2: Publish as Normal / Standard YouTube Video (16:9 / Full Video)
    # -------------------------------------------------------------------------
    print("\n--- TEST 2: Publish as Normal YouTube Video (Standard Video) ---")
    standard_title = "IncuBrix Product Overview: Autonomous B2B Content Engine"
    standard_desc = "Complete deep dive into the 30-day autonomous content workflow for B2B SaaS founders."

    video_result = publisher.publish_youtube_video(
        video_path=target_video,
        title=standard_title,
        description=standard_desc,
        tags=["IncuBrix", "SaaS", "ContentMarketing", "Automation", "B2BGrowth"],
        category_id="28",
        privacy_status="public",
        is_short=False,
    )

    print(f"Status:        {video_result.get('status')}")
    print(f"Platform:      {video_result.get('platform')}")
    print(f"Media Type:    {video_result.get('media_type')}")
    print(f"Title:         {video_result.get('title')}")
    print(f"Published URL: {video_result.get('published_url')}")
    print(f"Simulated:     {video_result.get('simulated', False)}")

    assert video_result.get("status") == "success", "Standard video publish status failed"
    assert video_result.get("platform") == "YouTube Video", "Platform mismatch"
    assert "#Shorts" not in video_result.get("title", ""), "Should NOT force #Shorts for standard video"
    assert "https://www.youtube.com/watch?v=" in video_result.get("published_url", ""), "Invalid standard video URL"
    assert video_result.get("media_type") == "video", "Media type should be video"
    print(">>> [PASS] Standard YouTube Video publish verified successfully!")

    # -------------------------------------------------------------------------
    # TEST 3: Dispatch via publish_asset Unified Engine
    # -------------------------------------------------------------------------
    print("\n--- TEST 3: Unified Asset Dispatcher Integration ---")
    manifest = load_manifest()
    # Find a video asset or create a test record
    video_assets = [a for a in manifest if "video" in (a.get("format") or "").lower()]
    test_asset_id = video_assets[0]["asset_id"] if video_assets else "INC-VID-001"

    print(f"[*] Dispatching asset '{test_asset_id}' to 'YouTube Shorts'...")
    disp_shorts = publisher.publish_asset(test_asset_id, target_platform="YouTube Shorts")
    print(f"    Shorts URL: {disp_shorts.get('primary_url')}")
    assert "shorts" in disp_shorts.get("primary_url", "").lower()

    print(f"[*] Dispatching asset '{test_asset_id}' to 'YouTube Video' (standard)...")
    disp_video = publisher.publish_asset(test_asset_id, target_platform="YouTube Video")
    print(f"    Standard Video URL: {disp_video.get('primary_url')}")
    assert "watch?v=" in disp_video.get("primary_url", "").lower()
    print(">>> [PASS] Asset Dispatcher verified for both YouTube formats!")

    print("\n" + "=" * 70)
    print("ALL YOUTUBE PUBLISHING TESTS COMPLETED AND CONFIRMED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
