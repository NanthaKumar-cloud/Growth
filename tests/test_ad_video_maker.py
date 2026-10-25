import pytest
import xml.etree.ElementTree as ET
from pathlib import Path
from src.ad_video_maker import (
    normalize_storyboard,
    make_cues,
    voice_candidates,
    check_svg,
    fallback_svg,
    clean_spoken,
    slugify,
    fill,
    ASPECTS,
    VOICES
)

def test_slugify():
    assert slugify("Dosa corner shop with tasty chutneys") == "dosa-corner-shop-with-tasty-chutneys"
    assert slugify("") == "ad-video"

def test_fill_template():
    tpl = "Hello <<NAME>>, welcome to <<PLACE>>!"
    out = fill(tpl, NAME="Athish", PLACE="IncuBrix")
    assert out == "Hello Athish, welcome to IncuBrix!"

def test_clean_spoken():
    raw = "Here is **bold** text with #hashtags and `code`!"
    assert clean_spoken(raw) == "Here is bold text with hashtags and code!"

def test_voice_candidates():
    cands = voice_candidates("en-IN", "Puck", None)
    names = [c[1] for c in cands]
    assert "en-IN-Chirp3-HD-Puck" in names
    assert "en-US-Chirp3-HD-Puck" in names
    assert "en-US-Neural2-D" in names  # Puck is Male

    cands_f = voice_candidates("en-US", "Aoede", None)
    names_f = [c[1] for c in cands_f]
    assert "en-US-Chirp3-HD-Aoede" in names_f
    assert "en-US-Neural2-F" in names_f  # Aoede is Female

def test_make_cues_timing():
    text = "IncuBrix turns one recording into ten social clips. Stop wrestling with video editors."
    cues = make_cues(text, audio_dur=6.0, lead=0.7, max_line=30)
    assert len(cues) >= 2
    assert cues[0]["s"] == pytest.approx(0.7, 0.05)
    assert cues[-1]["e"] <= 0.7 + 6.0 + 0.1
    for cue in cues:
        assert "lines" in cue
        assert "text" in cue

def test_normalize_storyboard():
    raw_sb = {
        "title": "Solo Creator Bottleneck",
        "scenes": [
            {
                "narration": "Why creators burn out in 2026.",
                "on_screen_headline": "Stop The Tool Bloat"
            },
            {
                "narration": "IncuBrix unifies your workflow.",
                "on_screen_headline": "One Unified Studio"
            }
        ]
    }
    sb = normalize_storyboard(raw_sb)
    assert sb["brand"]["name"] == "IncuBrix"
    assert len(sb["scenes"]) == 2
    assert sb["scenes"][0]["role"] == "STORY"
    assert sb["scenes"][1]["transition_out"] == "fade"  # Last scene must fade
    assert "palette" in sb["design_system"]
    assert "ribbon" in sb["design_system"]

def test_check_svg_valid():
    valid_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920">
    <style>
      .a { opacity: 0; animation-fill-mode: forwards; }
      .a1 { animation: pop 1s forwards; }
      @keyframes pop { from { opacity: 0; } to { opacity: 1; } }
    </style>
    <rect width="1080" height="1920" fill="#0B0F19"/>
    <g class="a a1"><text x="540" y="300" text-anchor="middle" fill="#FFFFFF">Hook Headline</text></g>
    </svg>"""
    svg, hard, soft = check_svg(valid_svg, 1080, 1920)
    assert svg is not None
    assert len(hard) == 0

def test_check_svg_autofix_transform_conflict():
    # Element has both transform attribute and animated class
    conflicted_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920">
    <style>
      .a { opacity: 0; animation-fill-mode: forwards; }
      .a1 { animation: rise 1s forwards; }
      @keyframes rise { from { opacity: 0; } to { opacity: 1; } }
    </style>
    <g class="a a1" transform="translate(100, 200)">
        <text x="0" y="0">Test</text>
    </g>
    </svg>"""
    svg, hard, soft = check_svg(conflicted_svg, 1080, 1920)
    assert svg is not None
    assert len(hard) == 0
    # Verify auto-fix nested the transform into a parent <g>
    root = ET.fromstring(svg)
    # The inner element with class "a a1" should not have a transform attribute directly
    for el in root.iter():
        if "a1" in el.get("class", ""):
            assert el.get("transform") is None

def test_fallback_svg_generation():
    raw_sb = {
        "title": "Test Fallback",
        "scenes": [
            {
                "narration": "First scene narration.",
                "on_screen_headline": "Headline One",
                "on_screen_support": "Supporting subtext here"
            }
        ]
    }
    sb = normalize_storyboard(raw_sb)
    svg = fallback_svg(sb, 0, 1080, 1920, 1080, 280)
    assert svg.startswith("<svg")
    assert "Headline One" in svg
    assert "Supporting subtext here" in svg
    # Must be valid XML
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")

def test_make_storyboard_autonomous_rules():
    from src.ad_video_maker import DIRECTOR_USER, fill, VOICES
    voices = "; ".join(f"{k} ({g}, {d})" for k, (g, d) in VOICES.items())
    
    # Autonomous scenes (scenes_count = 0) and duration (seconds = 0)
    scene_rule_auto = (
        "Number of scenes: YOU decide, between 3 and 8. Use as many scenes as the story needs: one clear idea per scene, "
        "each scene about 3-6 seconds of narration. A crisp ad needs 3-5 scenes. "
        "Never pad with filler scenes and never cram two ideas into one scene."
    )
    length_rule_auto = (
        "Total length: YOU decide from the content, normally 15-45 seconds of narration "
        "(~2.4 spoken words per second). If the brief states a duration, follow it."
    )
    user_prompt = fill(
        DIRECTOR_USER,
        USE_CASE="Tasty dosa corner",
        SCENE_RULE=scene_rule_auto,
        LENGTH_RULE=length_rule_auto,
        ASPECT="9:16",
        W=1080,
        H=1920,
        LANG="en-IN",
        VOICES=voices
    )
    assert "YOU decide, between 3 and 8" in user_prompt
    assert "YOU decide from the content" in user_prompt
    assert "Puck" in user_prompt
    assert "Aoede" in user_prompt

def test_video_generate_request_auto_fields():
    from src.server import VideoGenerateRequest
    # Test scene count input with autonomous voice
    req = VideoGenerateRequest(use_case="Quick product tour", scenes_count=4)
    assert req.scenes_count == 4
    assert req.seconds == 0
    assert req.voice is None

