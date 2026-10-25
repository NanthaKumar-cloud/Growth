import re
from typing import Dict, Any, List, Tuple

class ValidationError(Exception):
    pass

class ContentValidator:
    FORBIDDEN_PHRASES = [
        "guaranteed viral",
        "make $10,000",
        "overnight riches",
        "100% automated fame",
        "mind reading",
        "secret hack that platforms hate",
        "get 100k followers in 7 days",
    ]

    ALLOWED_PLATFORMS = [
        "youtube",
        "youtube shorts",
        "youtube video",
        "facebook",
        "facebook pages",
        "instagram",
    ]
    ALLOWED_FORMATS = ["short_video", "carousel", "text_post", "graphic"]

    def __init__(self, ground_truth_text: str = ""):
        self.ground_truth_text = ground_truth_text.lower()

    def validate_asset(self, asset: Dict[str, Any]) -> Tuple[bool, List[str]]:
        issues = []

        # Required fields
        required_keys = ["asset_id", "platform", "format", "content_pillar", "hook", "caption", "cta"]
        for key in required_keys:
            if not asset.get(key) or not str(asset[key]).strip():
                issues.append(f"Missing required field: {key}")

        platform = str(asset.get("platform", "")).lower()
        if platform not in self.ALLOWED_PLATFORMS:
            issues.append(f"Unsupported platform '{platform}'. Allowed: {self.ALLOWED_PLATFORMS}")

        content_format = str(asset.get("format", "")).lower()
        if content_format not in self.ALLOWED_FORMATS:
            issues.append(f"Unsupported format '{content_format}'. Allowed: {self.ALLOWED_FORMATS}")

        # Check for forbidden claims
        full_content = f"{asset.get('hook', '')} {asset.get('caption', '')}".lower()
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase in full_content:
                issues.append(f"Contains prohibited marketing phrase: '{phrase}'")

        # Format-specific checks
        if content_format == "short_video":
            # Video duration check: <= 60 seconds
            # An average speaker speaks ~140-160 words per minute. Max 160 words for dialogue.
            words = len(asset.get("caption", "").split())
            if words > 180:
                issues.append(f"Short video script too long ({words} words). Exceeds 60-second limit (~160 words).")

        return len(issues) == 0, issues
