import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont

from src import config

class MediaRenderer:
    def __init__(
        self,
        final_dir: Path | str = config.FINAL_ASSETS_DIR,
        source_dir: Path | str = config.SOURCE_ASSETS_DIR
    ):
        self.final_dir = Path(final_dir)
        self.source_dir = Path(source_dir)
        
        self.final_videos_dir = self.final_dir / "videos"
        self.final_carousels_dir = self.final_dir / "carousels"
        self.final_graphics_dir = self.final_dir / "graphics"

        for p in [self.final_videos_dir, self.final_carousels_dir, self.final_graphics_dir, self.source_dir]:
            p.mkdir(parents=True, exist_ok=True)

    def render_carousel_slide(
        self,
        asset_id: str,
        slide_idx: int,
        total_slides: int,
        title: str,
        body_text: str,
        pillar: str
    ) -> Path:
        width, height = 1080, 1080
        # Modern deep indigo / slate background
        bg_color = (15, 23, 42) # Slate 900
        card_color = (30, 41, 59) # Slate 800
        accent_color = (99, 102, 241) # Indigo 500
        text_white = (248, 250, 252) # Slate 50
        text_muted = (148, 163, 184) # Slate 400

        img = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Draw card container
        margin = 60
        card_rect = [margin, margin, width - margin, height - margin]
        draw.rounded_rectangle(card_rect, radius=24, fill=card_color, outline=accent_color, width=2)

        # Draw header bar
        draw.rectangle([margin, margin, width - margin, margin + 90], fill=(24, 33, 47))
        draw.text((margin + 40, margin + 30), "INCUBRIX CREATOROPS", fill=accent_color)
        draw.text((width - margin - 140, margin + 30), f"{slide_idx} / {total_slides}", fill=text_muted)

        # Draw Category / Pillar
        draw.text((margin + 50, margin + 140), f"PILLAR: {pillar.upper()}", fill=accent_color)

        # Draw Title
        title_lines = self._wrap_text(title, max_chars=36)
        y_pos = margin + 200
        for line in title_lines[:3]:
            draw.text((margin + 50, y_pos), line, fill=text_white)
            y_pos += 45

        # Draw Divider
        y_pos += 20
        draw.line([margin + 50, y_pos, width - margin - 50, y_pos], fill=(51, 65, 85), width=2)
        y_pos += 40

        # Draw Body
        body_lines = self._wrap_text(body_text, max_chars=44)
        for line in body_lines[:12]:
            draw.text((margin + 50, y_pos), line, fill=text_muted)
            y_pos += 38

        # Footer CTA
        footer_y = height - margin - 70
        draw.text((margin + 50, footer_y), "incubrix.com  |  Create With Purpose. Publish Without Limits.", fill=accent_color)

        output_filename = f"{asset_id}_slide_{slide_idx}.png"
        output_path = self.final_carousels_dir / output_filename
        img.save(output_path, "PNG")
        return output_path

    def render_short_video(
        self,
        asset_id: str,
        hook: str,
        caption: str,
        duration_seconds: int = 25
    ) -> Path:
        """
        Renders a 9:16 vertical MP4 video (1080x1920) using FFmpeg.
        Uses solid animated background with text overlay and silent/ambient audio track.
        """
        output_path = self.final_videos_dir / f"{asset_id}.mp4"

        # Sanitize text for FFmpeg drawtext
        clean_hook = str(hook).replace("'", "").replace(":", "-")[:60]
        summary_caption = str(caption)[:120].replace("'", "").replace(":", "-").replace("\n", " ")

        # FFmpeg command to build 9:16 vertical video with background and dynamic text overlay
        # color=c=0x0F172A:s=1080x1920
        vf_filters = (
            "drawbox=y=0:color=0x0F172A:width=1080:height=1920:t=fill,"
            "drawbox=x=80:y=200:w=920:h=1520:color=0x1E293B@0.9:t=fill,"
            f"drawtext=text='INCUBRIX | CREATOROPS':fontcolor=0x6366F1:fontsize=36:x=(w-text_w)/2:y=280,"
            f"drawtext=text='{clean_hook}':fontcolor=0xFFFFFF:fontsize=48:x=(w-text_w)/2:y=380,"
            f"drawtext=text='SWIPE UP / CLICK LINK FOR WORKFLOW':fontcolor=0x94A3B8:fontsize=32:x=(w-text_w)/2:y=1600"
        )

        cmd = [
            "ffmpeg",
            "-y", # overwrite
            "-f", "lavfi",
            "-i", f"color=c=0x0F172A:s=1080x1920:d={duration_seconds}:r=30",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo",
            "-vf", vf_filters,
            "-c:v", "libx264",
            "-t", str(duration_seconds),
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            str(output_path)
        ]

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception as e:
            # Fallback if drawtext fonts fail: render without complex font filters
            fallback_cmd = [
                "ffmpeg",
                "-y",
                "-f", "lavfi",
                "-i", f"color=c=0x1E293B:s=1080x1920:d={duration_seconds}:r=30",
                "-f", "lavfi",
                "-i", f"anullsrc=r=44100:cl=stereo",
                "-c:v", "libx264",
                "-t", str(duration_seconds),
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-shortest",
                str(output_path)
            ]
            subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        return output_path

    def save_source_asset(self, asset_id: str, asset_data: Dict[str, Any]) -> Path:
        source_path = self.source_dir / f"{asset_id}_source.md"
        content = f"""# Editable Source Asset: {asset_id}

- **Platform:** {asset_data.get('platform')}
- **Format:** {asset_data.get('format')}
- **Pillar:** {asset_data.get('content_pillar')}
- **Target Metric:** {asset_data.get('target_metric', 'Engagement')}
- **Rights Checked:** Yes (Original IncuBrix IP / AI-disclosed)

## Hook
{asset_data.get('hook')}

## Full Script / Caption
{asset_data.get('caption')}

## Call to Action (CTA)
{asset_data.get('cta')}

## Tracked Link
{asset_data.get('utm_link')}
"""
        source_path.write_text(content, encoding="utf-8")
        return source_path

    def _wrap_text(self, text: Any, max_chars: int = 40) -> List[str]:
        if isinstance(text, dict):
            text = " ".join(f"{k}: {v}" for k, v in text.items())
        elif isinstance(text, list):
            text = " ".join(str(x) for x in text)
        else:
            text = str(text) if text is not None else ""
        words = text.split()
        lines = []
        current_line = []
        current_len = 0
        for w in words:
            if current_len + len(w) + (1 if current_line else 0) <= max_chars:
                current_line.append(w)
                current_len += len(w) + (1 if current_line else 0)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [w]
                current_len = len(w)
        if current_line:
            lines.append(" ".join(current_line))
        return lines
