"""
Unit Tests for Animated SVG Carousel Engine
"""

import pytest
from src.animated_svg_carousel import (
    format_use_case,
    parse_expected_slide_count,
    extract_svg_slides,
    build_interactive_preview_player
)


def test_format_use_case_dict():
    use_case = {
        "brand": "Dosa House",
        "goal": "drive weekend orders",
        "audience": "young professionals",
        "tone": "warm, bold",
        "offer": "dosa + chutney for $8.99",
        "num_slides": 7
    }
    formatted = format_use_case(use_case)
    assert "Brand: Dosa House." in formatted
    assert "Goal: drive weekend orders." in formatted
    assert "Number of slides: 7." in formatted


def test_format_use_case_str():
    raw_str = "Brand: Test Brand. Goal: Awareness. Number of slides: 5."
    formatted = format_use_case(raw_str)
    assert formatted == raw_str


def test_parse_expected_slide_count():
    assert parse_expected_slide_count("Number of slides: 7.") == 7
    assert parse_expected_slide_count("Number of slides: 5.") == 5
    assert parse_expected_slide_count("No count mentioned here") == 7


def test_extract_svg_slides_valid():
    sample_response = """
### Slide 1 of 2 - Hook
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1350" width="100%" height="100%">
  <rect width="1080" height="1350" fill="#000"/>
  <text x="540" y="675" fill="#fff" font-size="80" text-anchor="middle">Slide 1</text>
</svg>
```

### Slide 2 of 2 - Call to Action
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1350" width="100%" height="100%">
  <rect width="1080" height="1350" fill="#111"/>
  <text x="540" y="675" fill="#00ffaa" font-size="80" text-anchor="middle">Slide 2</text>
</svg>
```
"""
    slides = extract_svg_slides(sample_response, expected_n=2)
    assert len(slides) == 2
    assert slides[0]["slide_index"] == 1
    assert slides[0]["role"] == "Hook"
    assert slides[0]["is_valid"] is True
    assert slides[1]["slide_index"] == 2
    assert slides[1]["role"] == "Call to Action"
    assert slides[1]["is_valid"] is True


def test_build_interactive_preview_player():
    sample_slides = [
        {
            "slide_index": 1,
            "role": "Hook",
            "svg_code": '<svg viewBox="0 0 1080 1350"><rect fill="#000"/></svg>'
        }
    ]
    html = build_interactive_preview_player(sample_slides, asset_id="TEST-001", title="Test")
    assert "<!DOCTYPE html>" in html
    assert "IncuBrix Live Carousel Viewer" in html
    assert "TEST-001" in html
    assert "Seamless Seam View" in html
