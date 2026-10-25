import pytest
import xml.etree.ElementTree as ET
from src.ad_image import (
    slugify,
    clean_text,
    lum,
    contrast,
    color_roles,
    text_w,
    fit_text,
    detect_script,
    normalize_brief,
    build_plan,
    fallback_svg,
    check_svg,
    ASPECTS,
    FONT_CATALOG
)
from src.server import ImageGenerateRequest


def test_slugify():
    assert slugify("Sunrise Yoga Studio, first class free") == "sunrise-yoga-studio-first-class-free"
    assert slugify("") == "poster"


def test_clean_text():
    raw = "Crispy **Dosa** with #Chutneys and `Sambar`!"
    assert clean_text(raw) == "Crispy Dosa with Chutneys and Sambar!"
    assert clean_text("One two three four five", max_words=3) == "One two three"
    assert len(clean_text("A very long sentence that needs truncating", max_chars=15)) <= 15


def test_color_math_and_contrast():
    # White on black contrast must be 21:1
    assert contrast("#FFFFFF", "#000000") == pytest.approx(21.0, 0.5)
    # Identical colors must have contrast 1:1
    assert contrast("#FF6B1A", "#FF6B1A") == pytest.approx(1.0, 0.05)

    pal = {
        "bg": "#1A0C06",
        "bg_alt": "#3A1A0C",
        "primary": "#FF6B1A",
        "secondary": "#FFC93C",
        "accent": "#E63946",
        "ink": "#1A0C06",
        "paper": "#FFF8E7"
    }
    roles = color_roles(pal)
    assert roles["dark_background"] is True
    # Guaranteed readable text roles
    assert "text_main" in roles
    assert "cta_fill" in roles
    assert "cta_text" in roles


def test_fit_text():
    fs, lines = fit_text("Stop Fragmented Tool Bloat", box_w=400, box_h=120, factor=0.6, caps=False, max_lines=2, max_fs=48, min_fs=24)
    assert fs >= 24
    assert len(lines) <= 2
    assert "Tool" in " ".join(lines)


def test_detect_script():
    latin = "IncuBrix Growth Engine"
    assert detect_script(latin) is None

    tamil = "தோசை கார்னர்: மொறுமொறு தோசை"
    script = detect_script(tamil)
    assert script is not None
    assert script[0] == "Noto Sans Tamil"

    hindi = "स्वादिष्ट डोसा और चटनी"
    script_hi = detect_script(hindi)
    assert script_hi is not None
    assert script_hi[0] == "Noto Sans Devanagari"


def test_normalize_brief():
    raw = {
        "brand": {"name": "IncuBrix"},
        "copy": {
            "headline": "One Studio. Ten Platforms.",
            "support": "Autonomous CreatorOps that repurposes everything."
        }
    }
    brief = normalize_brief(raw)
    assert brief["brand"]["name"] == "IncuBrix"
    assert brief["copy"]["headline"] == "One Studio. Ten Platforms."
    assert "design_system" in brief
    assert "fonts" in brief["design_system"]
    assert "palette" in brief["design_system"]


def test_fallback_svg_and_check():
    brief = normalize_brief({
        "brand": {"name": "IncuBrix"},
        "copy": {
            "eyebrow": "CREATOROPS",
            "headline": "Transform One Video Into Ten",
            "support": "Save 15 hours every week with automated repurposing.",
            "cta": "Start Free"
        }
    })
    plan = build_plan(brief, 1080, 1350)
    svg = fallback_svg(brief, plan)
    assert svg.startswith("<svg")
    assert "</svg>" in svg
    assert "VIDEO INTO TEN" in svg

    # Validate with check_svg
    repaired, hard, soft = check_svg(svg, plan)
    assert repaired is not None
    assert len(hard) == 0


def test_image_generate_request_schema():
    req = ImageGenerateRequest(
        use_case="Crispy dosa corner shop",
        aspect="4:5",
        direction="warm, premium and elegant"
    )
    assert req.aspect == "4:5"
    assert req.variants == 1
    assert req.language == "English"
    assert req.direction == "warm, premium and elegant"
