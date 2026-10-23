import json
import os
import time
from typing import Dict, Any, List
from google import genai
from google.genai import types

from src import config
from src.telemetry import TelemetryTracker

class GenerationError(Exception):
    pass

class ContentGenerator:
    def __init__(self, telemetry: TelemetryTracker | None = None):
        self.telemetry = telemetry or TelemetryTracker()
        self.client = self._init_client()

    def _init_client(self) -> genai.Client:
        # Check if Vertex AI is configured or if API key is provided
        if config.USE_VERTEX_AI:
            return genai.Client(
                vertexai=True,
                project=config.GCP_PROJECT_ID,
                location=config.GCP_LOCATION
            )
        elif config.GEMINI_API_KEY:
            return genai.Client(api_key=config.GEMINI_API_KEY)
        else:
            # Fallback to default credentials
            return genai.Client()

    def generate_campaign_assets(
        self,
        ingested_input: Dict[str, Any],
        count: int = 10,
        max_retries: int = 3
    ) -> List[Dict[str, Any]]:
        prompt = self._build_prompt(ingested_input, count)
        
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=config.GEMINI_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        response_mime_type="application/json",
                    )
                )

                # Record token telemetry if available
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    prompt_tokens = response.usage_metadata.prompt_token_count or 0
                    comp_tokens = response.usage_metadata.candidates_token_count or 0
                    self.telemetry.record_usage(prompt_tokens, comp_tokens)

                raw_text = response.text.strip()
                parsed = json.loads(raw_text)
                if isinstance(parsed, dict) and "assets" in parsed:
                    assets = parsed["assets"]
                elif isinstance(parsed, list):
                    assets = parsed
                else:
                    raise GenerationError(f"Unexpected JSON structure from model: {type(parsed)}")

                return assets

            except Exception as e:
                last_error = e
                time.sleep(attempt * 2)

        raise GenerationError(f"Failed to generate assets after {max_retries} attempts: {last_error}")

    def _build_prompt(self, input_data: Dict[str, Any], count: int) -> str:
        return f"""You are the Lead Growth Engineer and Content Strategist for IncuBrix (incubrix.com).
IncuBrix is an all-in-one CreatorOps platform that unifies ideation (/thought-inbox), prompt-based video editing (/editor), voice cloning (/voice-hub), and multi-destination publishing (/publishing) into a single workspace.

Transform the following long-form source text into exactly {count} publication-ready, multi-platform social media assets.

SOURCE TITLE: {input_data.get('title')}
SOURCE CONTENT:
\"\"\"
{input_data.get('cleaned_text')}
\"\"\"

MANDATORY ASSET MIX REQUIREMENTS:
1. Minimum 3 Short-form Videos (<= 60 seconds duration, ~120-150 spoken words max). Format: "short_video". Platforms: "youtube" or "instagram".
2. Minimum 2 Multi-slide Carousels (5 to 7 slides breakdown). Format: "carousel". Platforms: "linkedin" or "instagram".
3. Remaining assets distributed across "text_post" on "linkedin" or "graphic" on "instagram".
4. Every short_video script must include clear Visual Cues [Visual: ...], Audio notes, and Spoken dialogue that can be voiced in under 60 seconds.
5. Every carousel must have a slide-by-slide structure with Slide 1 (Cover Hook) to Slide 7 (CTA).
6. Target Audience Geos: US, UK, CA, IE, AU, NZ, SG.
7. Content Pillars must be chosen from:
   - "CreatorOps & Tool Consolidation"
   - "Repurposing Recipes"
   - "AI Video & Voice Engineering"
   - "Growth Analytics & Algorithm Benchmarks"
   - "Behind-the-Studio & Product Spotlights"
8. Prohibited Claims: Never promise guaranteed follower counts, fake earnings, or overnight fame. Base all claims strictly on the source input and IncuBrix features.

Return a JSON object with this exact structure:
{{
  "assets": [
    {{
      "asset_id_suffix": "001",
      "platform": "linkedin" | "youtube" | "instagram",
      "format": "short_video" | "carousel" | "text_post" | "graphic",
      "content_pillar": "CreatorOps & Tool Consolidation",
      "hook": "Opening hook text (first 3 seconds or line 1)",
      "caption": "Full caption, script with visual cues, or slide-by-slide carousel copy",
      "hashtags": "#creatorops #contentcreation #videoediting",
      "cta": "Clear call to action pointing to try IncuBrix",
      "target_metric": "Impressions / Retention / Saves / CTR",
      "rights_licensing": "Original script generated with licensed IncuBrix assets. AI disclosure applied.",
      "claim_evidence": "Ground-truth fact from input supporting this claim"
    }}
  ]
}}
"""
