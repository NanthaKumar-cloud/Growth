import urllib.parse
from typing import Dict, Any

class UTMBuilder:
    def __init__(self, base_url: str = "https://incubrix.com", campaign: str = "growth_engine_q1"):
        self.base_url = base_url.rstrip("/")
        self.campaign = campaign

    def generate_link(
        self,
        platform: str,
        content_format: str,
        asset_id: str,
        content_pillar: str,
        custom_base_url: str | None = None
    ) -> str:
        base = (custom_base_url or self.base_url).rstrip("/")
        
        # Clean slug formatting
        source = platform.lower().replace(" ", "_")
        medium = content_format.lower().replace(" ", "_")
        content = asset_id.upper()
        term = content_pillar.lower().replace(" ", "_").replace("&", "and")

        params = {
            "utm_source": source,
            "utm_medium": medium,
            "utm_campaign": self.campaign,
            "utm_content": content,
            "utm_term": term,
        }

        query_string = urllib.parse.urlencode(params)
        return f"{base}/?{query_string}"

    def validate_utm(self, utm_url: str) -> bool:
        try:
            parsed = urllib.parse.urlparse(utm_url)
            query = urllib.parse.parse_qs(parsed.query)
            required_keys = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"]
            return all(k in query and len(query[k][0]) > 0 for k in required_keys)
        except Exception:
            return False
