import pytest
from src.validator import ContentValidator

def test_validate_valid_asset():
    validator = ContentValidator()
    asset = {
        "asset_id": "INC-LI-001",
        "platform": "linkedin",
        "format": "text_post",
        "content_pillar": "CreatorOps & Tool Consolidation",
        "hook": "Stop wasting 12 hours every week switching between 4 editing tools.",
        "caption": "IncuBrix unifies text editing, vertical clipping, and scheduling in one screen.",
        "cta": "Check out the link below to try the CreatorOps engine."
    }
    is_valid, issues = validator.validate_asset(asset)
    assert is_valid is True
    assert len(issues) == 0

def test_validate_missing_field():
    validator = ContentValidator()
    asset = {
        "asset_id": "INC-LI-002",
        "platform": "linkedin",
        # Missing format, hook, caption, cta
    }
    is_valid, issues = validator.validate_asset(asset)
    assert is_valid is False
    assert any("Missing required field" in err for err in issues)

def test_validate_forbidden_claims():
    validator = ContentValidator()
    asset = {
        "asset_id": "INC-LI-003",
        "platform": "linkedin",
        "format": "text_post",
        "content_pillar": "CreatorOps",
        "hook": "How to make $10,000 with overnight riches and guaranteed viral posts!",
        "caption": "This 100% automated fame method will get 100k followers in 7 days.",
        "cta": "Sign up now"
    }
    is_valid, issues = validator.validate_asset(asset)
    assert is_valid is False
    assert any("prohibited marketing phrase" in err for err in issues)

def test_validate_short_video_duration_limit():
    validator = ContentValidator()
    # Script with over 180 words (too long for 60s)
    long_script = " ".join(["word"] * 200)
    asset = {
        "asset_id": "INC-YT-001",
        "platform": "youtube",
        "format": "short_video",
        "content_pillar": "Repurposing Recipes",
        "hook": "Check this 60 second video out",
        "caption": long_script,
        "cta": "Try IncuBrix"
    }
    is_valid, issues = validator.validate_asset(asset)
    assert is_valid is False
    assert any("Exceeds 60-second limit" in err for err in issues)
