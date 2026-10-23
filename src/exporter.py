import csv
import json
from pathlib import Path
from typing import List, Dict, Any

OFFICIAL_COLUMNS = [
    "asset_id",
    "platform",
    "format",
    "content_pillar",
    "hook",
    "caption",
    "cta",
    "utm_link",
    "final_file_url",
    "source_file_url",
    "source_input",
    "tools_used",
    "rights_checked",
    "ai_label_needed",
    "scheduled_date",
    "test_published_url",
    "impressions_or_views",
    "engagement_rate",
    "clicks",
    "status",
    "notes",
    "duplicate_check",
    "completeness_check",
]

class AssetExporter:
    def __init__(self, output_dir: Path | str = "data/outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_to_csv(self, assets: List[Dict[str, Any]], filename: str = "calendar.csv") -> Path:
        target_path = self.output_dir / filename
        with open(target_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=OFFICIAL_COLUMNS)
            writer.writeheader()
            for asset in assets:
                # Guarantee all columns exist
                row = {col: asset.get(col, "") for col in OFFICIAL_COLUMNS}
                writer.writerow(row)
        return target_path

    def export_to_json(self, assets: List[Dict[str, Any]], filename: str = "assets_manifest.json") -> Path:
        target_path = self.output_dir / filename
        with open(target_path, mode="w", encoding="utf-8") as f:
            json.dump(assets, f, indent=2, ensure_ascii=False)
        return target_path
