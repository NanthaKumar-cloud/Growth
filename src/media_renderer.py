import os
import math
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from src import config

def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Helper to safely load crisp TrueType fonts across Windows and POSIX."""
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\calibrib.ttf",
    ] if bold else [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

class MediaRenderer:
    # 5 Vibrant Color Themes matching the 5 Content Pillars
    THEMES = {
        "creatorops": {
            "name": "CreatorOps",
            "accent": (99, 102, 241),      # Electric Indigo
            "cyan": (56, 189, 248),        # Sky Cyan
            "highlight": (244, 63, 94),    # Rose Pink
            "bg_dark": (11, 15, 25),       # Deep Midnight
            "card_bg": (22, 30, 49),       # Frosted Slate
            "card_border": (79, 70, 229),  # Indigo Glow
            "orb1": (79, 70, 229, 140),    # Indigo
            "orb2": (6, 182, 212, 120),    # Cyan
        },
        "repurposing": {
            "name": "Repurposing Recipes",
            "accent": (244, 63, 94),       # Vivid Rose / Sunset Coral
            "cyan": (251, 191, 36),        # Amber Gold
            "highlight": (16, 185, 129),   # Emerald
            "bg_dark": (15, 12, 25),       # Deep Plum
            "card_bg": (32, 23, 48),       # Frosted Purple
            "card_border": (225, 29, 72),  # Coral Glow
            "orb1": (225, 29, 72, 140),    # Rose
            "orb2": (245, 158, 11, 120),   # Amber
        },
        "voice": {
            "name": "AI Video & Voice Engineering",
            "accent": (139, 92, 246),      # Vivid Violet
            "cyan": (56, 189, 248),        # Cyan
            "highlight": (236, 72, 153),   # Neon Magenta
            "bg_dark": (10, 14, 28),       # Deep Tech Navy
            "card_bg": (25, 28, 52),       # Frosted Violet
            "card_border": (124, 58, 237), # Violet Glow
            "orb1": (124, 58, 237, 140),   # Purple
            "orb2": (217, 70, 239, 120),   # Magenta
        },
        "analytics": {
            "name": "Growth Analytics & Benchmarks",
            "accent": (16, 185, 129),      # Neon Emerald
            "cyan": (56, 189, 248),        # Sky Blue
            "highlight": (251, 191, 36),   # Amber
            "bg_dark": (6, 20, 24),        # Deep Emerald Slate
            "card_bg": (15, 38, 44),       # Frosted Teal
            "card_border": (5, 150, 105),  # Emerald Glow
            "orb1": (5, 150, 105, 140),    # Emerald
            "orb2": (37, 99, 235, 120),    # Royal Blue
        },
        "spotlight": {
            "name": "Product Spotlights",
            "accent": (245, 158, 11),      # Electric Amber
            "cyan": (56, 189, 248),        # Cyan
            "highlight": (244, 63, 94),    # Coral
            "bg_dark": (17, 18, 28),       # Deep Charcoal
            "card_bg": (33, 31, 49),       # Frosted Slate
            "card_border": (234, 88, 12),  # Amber Glow
            "orb1": (234, 88, 12, 140),    # Orange
            "orb2": (99, 102, 241, 120),   # Indigo
        }
    }

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
        self.templates_dir = config.TEMPLATES_DIR

        for p in [self.final_videos_dir, self.final_carousels_dir, self.final_graphics_dir, self.source_dir, self.templates_dir]:
            p.mkdir(parents=True, exist_ok=True)

        self.bg_music_path = self.templates_dir / "bg_music.wav"
        if not self.bg_music_path.exists():
            self._generate_background_music(self.bg_music_path)

    def _get_theme(self, pillar: str) -> Dict[str, Any]:
        p = str(pillar).lower()
        if "repurpos" in p:
            return self.THEMES["repurposing"]
        elif "voice" in p or "video" in p:
            return self.THEMES["voice"]
        elif "analytic" in p or "benchmark" in p:
            return self.THEMES["analytics"]
        elif "studio" in p or "spotlight" in p:
            return self.THEMES["spotlight"]
        return self.THEMES["creatorops"]

    def _create_vibrant_background(self, width: int, height: int, theme: Dict[str, Any]) -> Image.Image:
        """Renders an Apple/Linear-style dark mesh gradient with dual glowing color orbs and grid dots."""
        base = Image.new("RGB", (width, height), color=theme["bg_dark"])
        
        # Overlay with glowing orbs
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_o = ImageDraw.Draw(overlay)
        
        # Orb 1 (Top Left)
        orb1_r = int(min(width, height) * 0.45)
        draw_o.ellipse([-orb1_r//2, -orb1_r//2, orb1_r, orb1_r], fill=theme["orb1"])
        
        # Orb 2 (Bottom Right)
        orb2_r = int(min(width, height) * 0.5)
        draw_o.ellipse([width - orb2_r, height - orb2_r, width + orb2_r//3, height + orb2_r//3], fill=theme["orb2"])
        
        # Orb 3 (Subtle Center Accent)
        cx, cy = width // 2, height // 2
        draw_o.ellipse([cx - 200, cy - 200, cx + 200, cy + 200], fill=(theme["highlight"][0], theme["highlight"][1], theme["highlight"][2], 50))
        
        blurred = overlay.filter(ImageFilter.GaussianBlur(110))
        base.paste(blurred, (0, 0), blurred)
        
        # Draw subtle tech matrix grid
        draw = ImageDraw.Draw(base)
        step = 60
        for x in range(step, width - step, step):
            for y in range(step, height - step, step):
                draw.point((x, y), fill=(255, 255, 255, 35))
                
        return base

    def _draw_browser_mockup(self, draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, route_text: str, theme: Dict[str, Any]):
        """Draws a clean modern browser / app window mockup with macOS dots and URL bar."""
        # Main window container
        draw.rounded_rectangle([x, y, x + w, y + h], radius=24, fill=theme["card_bg"], outline=theme["card_border"], width=3)
        # Window header bar
        header_h = 55
        draw.rounded_rectangle([x, y, x + w, y + header_h], radius=24, fill=(15, 23, 42))
        draw.rectangle([x, y + 25, x + w, y + header_h], fill=(15, 23, 42))
        # MacOS control dots
        draw.ellipse([x + 24, y + 20, x + 38, y + 34], fill=(239, 68, 68)) # Red
        draw.ellipse([x + 46, y + 20, x + 60, y + 34], fill=(245, 158, 11)) # Yellow
        draw.ellipse([x + 68, y + 20, x + 82, y + 34], fill=(16, 185, 129)) # Green
        # URL pill
        font_url = get_font(20, bold=False)
        url_w = w - 240
        draw.rounded_rectangle([x + 120, y + 12, x + 120 + url_w, y + 43], radius=12, fill=(30, 41, 59))
        draw.text((x + 140, y + 16), f"🔒 {route_text}", font=font_url, fill=(148, 163, 184))

    def _draw_audio_waveform(self, draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, theme: Dict[str, Any], bars_count: int = 24):
        """Draws glowing neon audio spectrum bars to visualize Voice Hub and audio synthesis."""
        bar_w = max(6, int((w - (bars_count * 8)) / bars_count))
        cur_x = x
        for i in range(bars_count):
            bar_h = int(20 + (h - 40) * abs(math.sin(i * 0.45 + 0.3)))
            color = theme["cyan"] if i % 2 == 0 else theme["accent"]
            draw.rounded_rectangle([cur_x, y + h//2 - bar_h//2, cur_x + bar_w, y + h//2 + bar_h//2], radius=bar_w//2, fill=color)
            cur_x += bar_w + 8

    # -------------------------------------------------------------------------
    # 1. STANDALONE MARKETING GRAPHIC POSTER
    # -------------------------------------------------------------------------
    def render_graphic(
        self,
        asset_id: str,
        title: str,
        body_text: str,
        pillar: str,
        cta: str = "Visit incubrix.com"
    ) -> Path:
        """Renders an attractive, high-contrast, modern SaaS marketing poster (1080x1080)."""
        width, height = 1080, 1080
        theme = self._get_theme(pillar)
        img = self._create_vibrant_background(width, height, theme)
        draw = ImageDraw.Draw(img)

        # Fonts
        font_brand = get_font(26, bold=True)
        font_pill = get_font(22, bold=True)
        font_title = get_font(48, bold=True)
        font_body = get_font(30, bold=False)
        font_card_title = get_font(28, bold=True)
        font_cta = get_font(26, bold=True)

        margin = 55

        # 1. Top Brand Bar & Pillar Badge
        draw.rounded_rectangle([margin, margin, margin + 340, margin + 55], radius=20, fill=(15, 23, 42, 230), outline=theme["accent"], width=2)
        draw.text((margin + 25, margin + 14), "INCUBRIX  ✦  CREATOROPS", font=font_brand, fill=(255, 255, 255))

        clean_pillar = f"⚡ {str(pillar).upper()}"
        pill_w = len(clean_pillar) * 14 + 30
        draw.rounded_rectangle([width - margin - pill_w, margin, width - margin, margin + 55], radius=20, fill=(15, 23, 42, 230), outline=theme["cyan"], width=2)
        draw.text((width - margin - pill_w + 18, margin + 14), clean_pillar, font=font_pill, fill=theme["cyan"])

        # 2. Main Hook Headline
        y_pos = margin + 95
        title_lines = self._wrap_text(str(title), max_chars=32)
        for line in title_lines[:3]:
            draw.text((margin, y_pos), line, font=font_title, fill=(255, 255, 255))
            y_pos += 60

        # 3. Center Graphic Showcase: Realistic Browser Window Mockup
        mockup_y = y_pos + 25
        mockup_h = 390
        mockup_w = width - (margin * 2)
        self._draw_browser_mockup(draw, margin, mockup_y, mockup_w, mockup_h, "app.incubrix.com/studio/pipeline", theme)

        # Content inside browser mockup
        inside_y = mockup_y + 80
        # Draw workflow status card
        draw.rounded_rectangle([margin + 30, inside_y, width - margin - 30, inside_y + 80], radius=16, fill=(15, 23, 42), outline=theme["accent"], width=2)
        draw.text((margin + 50, inside_y + 25), "✦ WORKFLOW ENGINE ACTIVE", font=font_card_title, fill=theme["cyan"])
        draw.text((width - margin - 260, inside_y + 26), "LATENCY: 110s  |  COST: <$0.01", font=font_pill, fill=(203, 213, 225))

        # Waveform visualizer
        self._draw_audio_waveform(draw, margin + 50, inside_y + 110, mockup_w - 100, 70, theme, bars_count=26)

        # Key Insight / Bullet text inside mockup
        body_y = inside_y + 205
        clean_lines = [l.strip() for l in str(body_text).split("\n") if l.strip()]
        for line in clean_lines[:3]:
            # Draw checkmark bullet
            draw.text((margin + 50, body_y), "✓", font=font_card_title, fill=theme["accent"])
            wrapped = self._wrap_text(line, max_chars=40)
            for wl in wrapped[:1]:
                draw.text((margin + 90, body_y), wl, font=font_body, fill=(241, 245, 249))
                body_y += 38

        # 4. Bottom Highlight Box & CTA Button
        footer_y = height - margin - 90
        btn_w = width - (margin * 2)
        # Gradient look CTA button
        draw.rounded_rectangle([margin, footer_y, margin + btn_w, footer_y + 85], radius=24, fill=theme["accent"], outline=(255, 255, 255), width=2)
        draw.text((margin + 40, footer_y + 26), f"➔  {cta}   |   incubrix.com", font=font_cta, fill=(255, 255, 255))

        output_path = self.final_graphics_dir / f"{asset_id}.png"
        img.save(output_path, "PNG")
        return output_path

    # -------------------------------------------------------------------------
    # 2. MULTI-SLIDE CAROUSEL ENGINE (5 Slides + Combined PDF)
    # -------------------------------------------------------------------------
    def render_carousel_slide(
        self,
        asset_id: str,
        slide_idx: int,
        total_slides: int,
        title: str,
        body_text: str,
        pillar: str
    ) -> Path:
        """Renders an individual 1080x1080 carousel slide with consistent, elegant visual hierarchy."""
        width, height = 1080, 1080
        theme = self._get_theme(pillar)
        img = self._create_vibrant_background(width, height, theme)
        draw = ImageDraw.Draw(img)

        # Fonts
        font_brand = get_font(26, bold=True)
        font_pill = get_font(22, bold=True)
        font_title = get_font(52 if slide_idx == 1 else 46, bold=True)
        font_body = get_font(32, bold=False)
        font_card_title = get_font(28, bold=True)
        font_footer = get_font(24, bold=True)

        margin = 55

        # 1. Header Bar
        draw.rounded_rectangle([margin, margin, margin + 340, margin + 55], radius=20, fill=(15, 23, 42, 230), outline=theme["accent"], width=2)
        draw.text((margin + 25, margin + 14), "INCUBRIX  ✦  CREATOROPS", font=font_brand, fill=(255, 255, 255))

        counter_text = f"SLIDE {slide_idx} OF {total_slides}"
        draw.rounded_rectangle([width - margin - 200, margin, width - margin, margin + 55], radius=20, fill=(15, 23, 42, 230), outline=(71, 85, 105), width=2)
        draw.text((width - margin - 180, margin + 14), counter_text, font=font_pill, fill=theme["cyan"])

        # 2. Category Pill
        y_pos = margin + 90
        clean_pillar = f"⚡ {str(pillar).upper()}"
        pill_w = len(clean_pillar) * 14 + 30
        draw.rounded_rectangle([margin, y_pos, margin + pill_w, y_pos + 42], radius=16, fill=(15, 23, 42, 230), outline=theme["cyan"], width=2)
        draw.text((margin + 18, y_pos + 9), clean_pillar, font=font_pill, fill=theme["cyan"])

        # 3. Slide Title / Hook
        y_pos += 65
        title_lines = self._wrap_text(str(title), max_chars=30 if slide_idx == 1 else 34)
        for line in title_lines[:3]:
            draw.text((margin, y_pos), line, font=font_title, fill=(255, 255, 255))
            y_pos += 62

        # 4. Slide-Specific Rich Visual Cards
        card_y = y_pos + 20
        card_w = width - (margin * 2)
        card_h = height - card_y - margin - 90

        if slide_idx == 1:
            # --- COVER SLIDE ---
            # Large hero teaser box with glowing accent
            draw.rounded_rectangle([margin, card_y, margin + card_w, card_y + card_h], radius=28, fill=theme["card_bg"], outline=theme["accent"], width=3)
            
            # Browser preview banner
            self._draw_browser_mockup(draw, margin + 30, card_y + 30, card_w - 60, 220, "app.incubrix.com/studio", theme)
            
            # Subtitle / Hook teaser
            teaser_y = card_y + 280
            draw.text((margin + 50, teaser_y), "SWIPE THROUGH TO DISCOVER:", font=font_card_title, fill=theme["cyan"])
            draw.text((margin + 50, teaser_y + 40), "• The 14-Hour Content Bottleneck Solved", font=font_body, fill=(241, 245, 249))
            draw.text((margin + 50, teaser_y + 80), "• Full Architecture & Repurposing Blueprint", font=font_body, fill=(241, 245, 249))
            draw.text((margin + 50, teaser_y + 120), "• Measured 85% Efficiency Gains", font=font_body, fill=(241, 245, 249))

            # Swipe Indicator Pill
            draw.rounded_rectangle([width - margin - 320, card_y + card_h - 75, width - margin - 30, card_y + card_h - 25], radius=20, fill=theme["accent"])
            draw.text((width - margin - 295, card_y + card_h - 62), "SWIPE TO UNLOCK ➔", font=font_pill, fill=(255, 255, 255))

        elif slide_idx == 2:
            # --- PROBLEM BREAKDOWN SLIDE ---
            draw.rounded_rectangle([margin, card_y, margin + card_w, card_y + card_h], radius=28, fill=theme["card_bg"], outline=(239, 68, 68), width=3)
            # Red alert banner
            draw.rounded_rectangle([margin + 30, card_y + 30, width - margin - 30, card_y + 90], radius=16, fill=(15, 23, 42), outline=(239, 68, 68), width=2)
            draw.text((margin + 50, card_y + 44), "⚠  THE TRADITIONAL FRAGMENTED TOOL TRAP", font=font_card_title, fill=(239, 68, 68))
            
            # Body items
            item_y = card_y + 120
            clean_lines = [l.strip() for l in str(body_text).split("\n") if l.strip()]
            for l in clean_lines[:6]:
                draw.rounded_rectangle([margin + 30, item_y, width - margin - 30, item_y + 55], radius=14, fill=(15, 23, 42))
                draw.text((margin + 50, item_y + 12), f"✗  {l}", font=font_body, fill=(241, 245, 249))
                item_y += 65

        elif slide_idx == 3:
            # --- SOLUTION & UI MOCKUP SLIDE ---
            self._draw_browser_mockup(draw, margin, card_y, card_w, card_h, "app.incubrix.com/editor", theme)
            inside_y = card_y + 80
            draw.rounded_rectangle([margin + 30, inside_y, width - margin - 30, inside_y + 70], radius=16, fill=(15, 23, 42), outline=theme["accent"], width=2)
            draw.text((margin + 50, inside_y + 20), "✦  THE INCUBRIX UNIFIED CREATOROPS ENGINE", font=font_card_title, fill=theme["cyan"])
            
            # Waveform visualizer
            self._draw_audio_waveform(draw, margin + 40, inside_y + 90, card_w - 80, 70, theme, bars_count=24)
            
            # Feature pills
            feat_y = inside_y + 180
            clean_lines = [l.strip() for l in str(body_text).split("\n") if l.strip()]
            for l in clean_lines[:4]:
                draw.text((margin + 50, feat_y), "✓", font=font_card_title, fill=theme["accent"])
                draw.text((margin + 90, feat_y), l, font=font_body, fill=(241, 245, 249))
                feat_y += 48

        elif slide_idx == 4:
            # --- DATA & BENCHMARKS SLIDE ---
            draw.rounded_rectangle([margin, card_y, margin + card_w, card_y + card_h], radius=28, fill=theme["card_bg"], outline=theme["cyan"], width=3)
            
            # Big Glowing Stat Cards
            draw.rounded_rectangle([margin + 30, card_y + 30, margin + card_w//2 - 15, card_y + 190], radius=20, fill=(15, 23, 42), outline=theme["accent"], width=2)
            font_stat = get_font(54, bold=True)
            draw.text((margin + 50, card_y + 50), "85%", font=font_stat, fill=theme["accent"])
            draw.text((margin + 50, card_y + 120), "TIME SLASHED", font=font_pill, fill=(255, 255, 255))
            draw.text((margin + 50, card_y + 148), "14.2h down to 2.1h", font=font_pill, fill=(148, 163, 184))

            draw.rounded_rectangle([margin + card_w//2 + 15, card_y + 30, width - margin - 30, card_y + 190], radius=20, fill=(15, 23, 42), outline=theme["cyan"], width=2)
            draw.text((margin + card_w//2 + 35, card_y + 50), "+312%", font=font_stat, fill=theme["cyan"])
            draw.text((margin + card_w//2 + 35, card_y + 120), "ORGANIC REACH", font=font_pill, fill=(255, 255, 255))
            draw.text((margin + card_w//2 + 35, card_y + 148), "Multi-platform lift", font=font_pill, fill=(148, 163, 184))

            # Details
            detail_y = card_y + 220
            clean_lines = [l.strip() for l in str(body_text).split("\n") if l.strip()]
            for l in clean_lines[:4]:
                draw.text((margin + 50, detail_y), "▲", font=font_card_title, fill=theme["cyan"])
                draw.text((margin + 90, detail_y), l, font=font_body, fill=(241, 245, 249))
                detail_y += 46

        else:
            # --- ACTION CHECKLIST & FINAL CTA SLIDE ---
            draw.rounded_rectangle([margin, card_y, margin + card_w, card_y + card_h], radius=28, fill=theme["card_bg"], outline=theme["accent"], width=3)
            draw.text((margin + 40, card_y + 35), "YOUR 4-STEP ACTION CHECKLIST:", font=font_card_title, fill=theme["cyan"])
            
            check_y = card_y + 85
            checklist = [
                "Audit your monthly creator subscriptions (stop tool bloat)",
                "Capture voice ideas into IncuBrix Thought Inbox",
                "Edit video transcripts with 1-click prompt directives",
                "Syndicate across LinkedIn, Shorts & Reels from 1 screen"
            ]
            for item in checklist:
                draw.rounded_rectangle([margin + 30, check_y, width - margin - 30, check_y + 60], radius=14, fill=(15, 23, 42))
                draw.text((margin + 50, check_y + 14), "✓", font=font_card_title, fill=theme["accent"])
                draw.text((margin + 90, check_y + 16), item, font=get_font(26, bold=False), fill=(241, 245, 249))
                check_y += 72

            # Bottom CTA button
            draw.rounded_rectangle([margin + 30, card_y + card_h - 90, width - margin - 30, card_y + card_h - 20], radius=20, fill=theme["accent"])
            draw.text((margin + 60, card_y + card_h - 66), "START FREE AT INCUBRIX.COM  |  SAVE FOR LATER 🔖", font=font_pill, fill=(255, 255, 255))

        # 5. Bottom Brand Footer
        footer_y = height - margin - 50
        draw.line([margin, footer_y, width - margin, footer_y], fill=(51, 65, 85), width=2)
        draw.text((margin, footer_y + 16), "incubrix.com  ✦  Create With Purpose. Publish Without Limits.", font=font_footer, fill=(148, 163, 184))

        output_filename = f"{asset_id}_slide_{slide_idx}.png"
        output_path = self.final_carousels_dir / output_filename
        img.save(output_path, "PNG")
        return output_path

    def render_carousel_package(
        self,
        asset_id: str,
        pillar: str,
        slides_content: List[Dict[str, str]]
    ) -> List[Path]:
        """Renders all 5 slides, saves individual PNGs, multi-page LinkedIn PDF, and cover."""
        carousel_folder = self.final_carousels_dir / asset_id
        carousel_folder.mkdir(parents=True, exist_ok=True)

        rendered_paths = []
        pil_images = []
        total_slides = len(slides_content)

        for idx, slide_data in enumerate(slides_content, start=1):
            title = slide_data.get("title", f"Slide {idx}")
            body = slide_data.get("body", "")
            slide_path = self.render_carousel_slide(
                asset_id=f"{asset_id}",
                slide_idx=idx,
                total_slides=total_slides,
                title=title,
                body_text=body,
                pillar=pillar
            )
            # Copy to carousel subfolder
            subfolder_path = carousel_folder / f"slide_{idx}.png"
            img = Image.open(slide_path)
            img.save(subfolder_path, "PNG")
            rendered_paths.append(subfolder_path)
            pil_images.append(img.convert("RGB"))

        # Compile multi-page LinkedIn PDF
        pdf_path = self.final_carousels_dir / f"{asset_id}.pdf"
        if pil_images:
            pil_images[0].save(pdf_path, "PDF", save_all=True, append_images=pil_images[1:])

        # Save cover image
        cover_path = self.final_carousels_dir / f"{asset_id}_cover.png"
        if pil_images:
            pil_images[0].save(cover_path, "PNG")

        return rendered_paths

    # -------------------------------------------------------------------------
    # 3. HIGH-RETENTION MULTI-SCENE VIDEO REEL ENGINE (9:16 MP4 with Music)
    # -------------------------------------------------------------------------
    def render_short_video(
        self,
        asset_id: str,
        hook: str,
        caption: str,
        pillar: str = "CreatorOps",
        duration_seconds: int = 15
    ) -> Path:
        """
        Renders a dynamic, polished 9:16 vertical MP4 video (1080x1920) across 3 visual scenes:
        Scene 1 (Hook) -> Scene 2 (Workflow & Mockup) -> Scene 3 (Measured Results & CTA)
        Encodes with custom electronic synthwave background music and smooth progress bar!
        """
        width, height = 1080, 1920
        theme = self._get_theme(pillar)
        output_path = self.final_videos_dir / f"{asset_id}.mp4"

        # Fonts
        font_brand = get_font(34, bold=True)
        font_pill = get_font(24, bold=True)
        font_hook = get_font(56, bold=True)
        font_body = get_font(36, bold=False)
        font_card_title = get_font(32, bold=True)
        font_cta = get_font(34, bold=True)

        margin = 60

        def build_scene_frame(scene_idx: int, progress_pct: float) -> Image.Image:
            img = self._create_vibrant_background(width, height, theme)
            draw = ImageDraw.Draw(img)

            # 1. Top Brand Header Bar
            header_y = 120
            draw.rounded_rectangle([margin, header_y, margin + 420, header_y + 70], radius=24, fill=(15, 23, 42, 230), outline=theme["accent"], width=3)
            draw.text((margin + 30, header_y + 18), "INCUBRIX  ✦  CREATOROPS", font=font_brand, fill=(255, 255, 255))

            # Pillar tag
            clean_pillar = f"⚡ {str(pillar).upper()}"
            pill_w = len(clean_pillar) * 15 + 40
            draw.rounded_rectangle([width - margin - pill_w, header_y, width - margin, header_y + 70], radius=24, fill=(15, 23, 42, 230), outline=theme["cyan"], width=3)
            draw.text((width - margin - pill_w + 20, header_y + 20), clean_pillar, font=font_pill, fill=theme["cyan"])

            # 2. Main Title / Hook Headline
            y_pos = header_y + 110
            hook_lines = self._wrap_text(str(hook), max_chars=26)
            for line in hook_lines[:4]:
                draw.text((margin, y_pos), line, font=font_hook, fill=(255, 255, 255))
                y_pos += 72

            # 3. Dynamic Center Card depending on Scene
            center_y = y_pos + 40
            center_w = width - (margin * 2)
            center_h = 750

            if scene_idx == 1:
                # --- SCENE 1: THE HIGH-IMPACT HOOK & PAIN POINT ---
                draw.rounded_rectangle([margin, center_y, margin + center_w, center_y + center_h], radius=32, fill=theme["card_bg"], outline=(239, 68, 68), width=3)
                
                # Warning banner
                draw.rounded_rectangle([margin + 30, center_y + 40, width - margin - 30, center_y + 120], radius=20, fill=(15, 23, 42), outline=(239, 68, 68), width=2)
                draw.text((margin + 60, center_y + 58), "⚠  THE 14-HOUR CREATOR BOTTLENECK", font=font_card_title, fill=(239, 68, 68))

                # Dialogue box
                dia_y = center_y + 160
                draw.text((margin + 50, dia_y), "WHAT CREATORS ARE JUGGLING:", font=font_card_title, fill=theme["cyan"])
                dia_lines = self._wrap_text(str(caption), max_chars=32)
                cur_y = dia_y + 60
                for dl in dia_lines[:7]:
                    draw.text((margin + 50, cur_y), dl, font=font_body, fill=(241, 245, 249))
                    cur_y += 50

                # Badge
                draw.rounded_rectangle([margin + 50, center_y + center_h - 110, width - margin - 50, center_y + center_h - 40], radius=20, fill=(15, 23, 42), outline=theme["accent"], width=2)
                draw.text((margin + 80, center_y + center_h - 88), "✦  WATCH THE REPURPOSING SPEEDRUN ➔", font=font_card_title, fill=theme["cyan"])

            elif scene_idx == 2:
                # --- SCENE 2: THE PRODUCT WORKFLOW & BROWSER MOCKUP ---
                self._draw_browser_mockup(draw, margin, center_y, center_w, center_h, "app.incubrix.com/editor", theme)
                
                inside_y = center_y + 90
                draw.rounded_rectangle([margin + 30, inside_y, width - margin - 30, inside_y + 90], radius=20, fill=(15, 23, 42), outline=theme["accent"], width=2)
                draw.text((margin + 60, inside_y + 30), "⚡  PROMPT VIDEO EDITOR & VOICE HUB", font=font_card_title, fill=theme["cyan"])

                # Waveform animation
                self._draw_audio_waveform(draw, margin + 40, inside_y + 120, center_w - 80, 110, theme, bars_count=24)

                # 3-step workflow pills
                step_y = inside_y + 260
                steps = [
                    "1. Ingest raw 15-min podcast or transcript",
                    "2. Prompt editor auto-cuts pauses & trims",
                    "3. 1-to-10 multi-platform clips extracted"
                ]
                for s in steps:
                    draw.rounded_rectangle([margin + 40, step_y, width - margin - 40, step_y + 65], radius=16, fill=(15, 23, 42), outline=(71, 85, 105), width=2)
                    draw.text((margin + 70, step_y + 16), s, font=font_body, fill=(241, 245, 249))
                    step_y += 82

            else:
                # --- SCENE 3: THE MEASURED RESULTS & VIRAL CTA ---
                draw.rounded_rectangle([margin, center_y, margin + center_w, center_y + center_h], radius=32, fill=theme["card_bg"], outline=theme["cyan"], width=3)
                
                # Stat Box 1
                draw.rounded_rectangle([margin + 40, center_y + 40, width - margin - 40, center_y + 190], radius=24, fill=(15, 23, 42), outline=theme["accent"], width=3)
                font_stat = get_font(68, bold=True)
                draw.text((margin + 70, center_y + 55), "85% TIME SAVED", font=font_stat, fill=theme["accent"])
                draw.text((margin + 70, center_y + 135), "Weekly production dropped from 14h to 2h", font=font_pill, fill=(203, 213, 225))

                # Stat Box 2
                draw.rounded_rectangle([margin + 40, center_y + 220, width - margin - 40, center_y + 370], radius=24, fill=(15, 23, 42), outline=theme["cyan"], width=3)
                draw.text((margin + 70, center_y + 235), "+312% REACH SPIKE", font=font_stat, fill=theme["cyan"])
                draw.text((margin + 70, center_y + 315), "Compounding distribution across Shorts & Reels", font=font_pill, fill=(203, 213, 225))

                # CTA button inside card
                cta_y = center_y + 420
                draw.rounded_rectangle([margin + 40, cta_y, width - margin - 40, cta_y + 100], radius=24, fill=theme["accent"], outline=(255, 255, 255), width=3)
                draw.text((margin + 80, cta_y + 30), "➔  CLAIM YOUR STUDIO AT INCUBRIX.COM", font=font_cta, fill=(255, 255, 255))

                # Social tags
                draw.text((margin + 80, cta_y + 130), "YouTube Shorts  •  Instagram Reels  •  LinkedIn", font=font_pill, fill=(148, 163, 184))

            # 4. Animated Scene Progress Bar at Bottom
            progress_y = height - 140
            draw.rounded_rectangle([margin, progress_y, width - margin, progress_y + 12], radius=6, fill=(51, 65, 85))
            cur_p_w = int((width - margin * 2) * progress_pct)
            draw.rounded_rectangle([margin, progress_y, margin + cur_p_w, progress_y + 12], radius=6, fill=theme["accent"])

            # 5. Bottom Swipe Up Indicator
            draw.text((margin + 40, height - 100), "SWIPE UP  |  TRY FREE AT INCUBRIX.COM  |  LINK IN BIO", font=font_pill, fill=(203, 213, 225))

            return img

        # Build 3 keyframe scene images
        s1 = build_scene_frame(1, 0.33)
        s2 = build_scene_frame(2, 0.66)
        s3 = build_scene_frame(3, 1.00)

        f1_path = self.final_videos_dir / f"{asset_id}_f1.png"
        f2_path = self.final_videos_dir / f"{asset_id}_f2.png"
        f3_path = self.final_videos_dir / f"{asset_id}_f3.png"

        s1.save(f1_path, "PNG")
        s2.save(f2_path, "PNG")
        s3.save(f3_path, "PNG")

        # Encode multi-scene video with background audio track
        # Scene 1: 5s, Scene 2: 5s, Scene 3: 5s = 15 seconds
        concat_txt_path = self.final_videos_dir / f"{asset_id}_concat.txt"
        with open(concat_txt_path, "w", encoding="utf-8") as f:
            f.write(f"file '{f1_path.name}'\nduration 5.0\n")
            f.write(f"file '{f2_path.name}'\nduration 5.0\n")
            f.write(f"file '{f3_path.name}'\nduration 5.0\n")
            f.write(f"file '{f3_path.name}'\n")

        # Run FFmpeg concat with background music
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_txt_path),
            "-i", str(self.bg_music_path),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(duration_seconds),
            "-shortest",
            str(output_path)
        ]

        subprocess.run(cmd, cwd=str(self.final_videos_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Clean temporary scene files
        for p in [f1_path, f2_path, f3_path, concat_txt_path]:
            if p.exists():
                p.unlink()

        return output_path

    def _generate_background_music(self, out_path: Path):
        """Generates a pleasant 15-second electronic synthwave background audio track."""
        import wave, struct
        sample_rate = 44100
        duration = 15.0
        n_samples = int(sample_rate * duration)

        chords = [
            [65.41, 130.81, 196.00, 261.63, 311.13, 392.00],
            [51.91, 103.83, 155.56, 207.65, 261.63, 311.13],
            [77.78, 155.56, 233.08, 311.13, 392.00, 466.16],
            [58.27, 116.54, 174.61, 233.08, 293.66, 349.23],
        ]
        chord_duration = duration / len(chords)

        with wave.open(str(out_path), "w") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            data = []
            for i in range(n_samples):
                t = i / sample_rate
                c_idx = min(int(t / chord_duration), len(chords) - 1)
                chord = chords[c_idx]
                c_t = t % chord_duration
                envelope = math.sin(math.pi * (c_t / chord_duration)) ** 0.4
                val_l, val_r = 0.0, 0.0
                for f_idx, freq in enumerate(chord):
                    pan = f_idx / len(chord)
                    vol = 0.12 / len(chord)
                    osc = math.sin(2 * math.pi * freq * t) + 0.25 * math.sin(4 * math.pi * freq * t)
                    val_l += osc * vol * (1.0 - pan * 0.4)
                    val_r += osc * vol * (0.6 + pan * 0.4)
                
                beat_t = (t * 2.0) % 1.0
                kick = math.exp(-beat_t * 18.0) * 0.07 * math.sin(2 * math.pi * 65.0 * math.exp(-beat_t * 10.0) * beat_t)
                hihat = math.exp(-((t * 4.0) % 1.0) * 30.0) * 0.02 * ((math.sin(2 * math.pi * 3200 * t) > 0) * 2 - 1)
                pulse = kick + hihat
                out_l = max(-0.95, min(0.95, (val_l * envelope + pulse)))
                out_r = max(-0.95, min(0.95, (val_r * envelope + pulse)))
                data.append(struct.pack("<hh", int(out_l * 32767), int(out_r * 32767)))
            wf.writeframes(b"".join(data))

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
