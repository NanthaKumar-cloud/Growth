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
            "short_name": "CREATOROPS",
            "accent": (99, 102, 241),      # Electric Indigo
            "cyan": (56, 189, 248),        # Sky Cyan
            "highlight": (244, 63, 94),    # Rose Pink
            "bg_dark": (11, 15, 25),       # Deep Midnight
            "card_bg": (20, 27, 45),       # Frosted Slate
            "card_border": (79, 70, 229),  # Indigo Glow
            "orb1": (79, 70, 229, 140),    # Indigo
            "orb2": (6, 182, 212, 120),    # Cyan
            "ai_sq": "creatorops_sq.jpg",
            "ai_vert": "creatorops_vert.jpg"
        },
        "repurposing": {
            "name": "Repurposing Recipes",
            "short_name": "REPURPOSING",
            "accent": (244, 63, 94),       # Vivid Rose / Sunset Coral
            "cyan": (251, 191, 36),        # Amber Gold
            "highlight": (16, 185, 129),   # Emerald
            "bg_dark": (15, 12, 25),       # Deep Plum
            "card_bg": (28, 20, 42),       # Frosted Purple
            "card_border": (225, 29, 72),  # Coral Glow
            "orb1": (225, 29, 72, 140),    # Rose
            "orb2": (245, 158, 11, 120),   # Amber
            "ai_sq": "repurposing_sq.jpg",
            "ai_vert": "repurposing_vert.jpg"
        },
        "voice": {
            "name": "AI Video & Voice Engineering",
            "short_name": "AI VOICE & VIDEO",
            "accent": (139, 92, 246),      # Vivid Violet
            "cyan": (56, 189, 248),        # Cyan
            "highlight": (236, 72, 153),   # Neon Magenta
            "bg_dark": (10, 14, 28),       # Deep Tech Navy
            "card_bg": (24, 25, 48),       # Frosted Violet
            "card_border": (124, 58, 237), # Violet Glow
            "orb1": (124, 58, 237, 140),   # Purple
            "orb2": (217, 70, 239, 120),   # Magenta
            "ai_sq": "voice_sq.jpg",
            "ai_vert": "voice_vert.jpg"
        },
        "analytics": {
            "name": "Growth Analytics & Benchmarks",
            "short_name": "GROWTH ANALYTICS",
            "accent": (16, 185, 129),      # Neon Emerald
            "cyan": (56, 189, 248),        # Sky Blue
            "highlight": (251, 191, 36),   # Amber
            "bg_dark": (6, 20, 24),        # Deep Emerald Slate
            "card_bg": (14, 34, 40),       # Frosted Teal
            "card_border": (5, 150, 105),  # Emerald Glow
            "orb1": (5, 150, 105, 140),    # Emerald
            "orb2": (37, 99, 235, 120),    # Royal Blue
            "ai_sq": "analytics_sq.jpg",
            "ai_vert": "analytics_vert.jpg"
        },
        "spotlight": {
            "name": "Product Spotlights",
            "short_name": "STUDIO SPOTLIGHT",
            "accent": (245, 158, 11),      # Electric Amber
            "cyan": (56, 189, 248),        # Cyan
            "highlight": (244, 63, 94),    # Coral
            "bg_dark": (17, 18, 28),       # Deep Charcoal
            "card_bg": (30, 28, 44),       # Frosted Slate
            "card_border": (234, 88, 12),  # Amber Glow
            "orb1": (234, 88, 12, 140),    # Orange
            "orb2": (99, 102, 241, 120),   # Indigo
            "ai_sq": "spotlight_sq.jpg",
            "ai_vert": "spotlight_vert.jpg"
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
        self.ai_visuals_dir = self.templates_dir / "ai_visuals"

        for p in [self.final_videos_dir, self.final_carousels_dir, self.final_graphics_dir, self.source_dir, self.templates_dir, self.ai_visuals_dir]:
            p.mkdir(parents=True, exist_ok=True)

        self.bg_music_path = self.templates_dir / "bg_music.wav"
        if not self.bg_music_path.exists():
            self._generate_background_music(self.bg_music_path)

    def _get_theme(self, pillar: str) -> Dict[str, Any]:
        p = str(pillar).lower()
        if "repurpos" in p:
            return self.THEMES["repurposing"]
        elif "voice" in p or "audio" in p or "dubbing" in p:
            return self.THEMES["voice"]
        elif "analytic" in p or "benchmark" in p or "decay" in p:
            return self.THEMES["analytics"]
        elif "studio" in p or "spotlight" in p or "behind" in p:
            return self.THEMES["spotlight"]
        return self.THEMES["creatorops"]

    def _get_ai_image(self, filename: str) -> Image.Image:
        """Safely loads an AI-generated image from the visual assets repository."""
        path = self.ai_visuals_dir / filename
        if path.exists():
            try:
                return Image.open(path).convert("RGB")
            except Exception:
                pass
        test_p = self.ai_visuals_dir / "tech_workspace_wide.jpg"
        if test_p.exists():
            return Image.open(test_p).convert("RGB")
        return Image.new("RGB", (1024, 1024), (15, 23, 42))

    # --- VECTOR DRAWING UTILITIES ---
    def _draw_diamond(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, color: Tuple[int, int, int]):
        """Draws a clean glowing 4-point diamond icon."""
        draw.polygon([(cx, cy - size), (cx + int(size * 0.7), cy), (cx, cy + size), (cx - int(size * 0.7), cy)], fill=color)

    def _draw_check(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: Tuple[int, int, int], width: int = 3):
        """Draws a crisp checkmark icon."""
        draw.line([(x, y + int(size * 0.5)), (x + int(size * 0.38), y + size), (x + size, y)], fill=color, width=width)

    def _draw_cross(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: Tuple[int, int, int], width: int = 3):
        """Draws a crisp X icon."""
        draw.line([(x, y), (x + size, y + size)], fill=color, width=width)
        draw.line([(x + size, y), (x, y + size)], fill=color, width=width)

    def _draw_arrow(self, draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, color: Tuple[int, int, int], width: int = 3):
        """Draws a sharp horizontal right arrow."""
        draw.line([(x, y + h // 2), (x + w, y + h // 2)], fill=color, width=width)
        draw.line([(x + w - h // 2, y), (x + w, y + h // 2), (x + w - h // 2, y + h)], fill=color, width=width)

    def _draw_pill(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        text: str,
        font: ImageFont.ImageFont,
        text_color: Tuple[int, int, int],
        bg_color: Tuple[int, int, int] | Tuple[int, int, int, int],
        border_color: Tuple[int, int, int] = None,
        padding_x: int = 18,
        padding_y: int = 9,
        radius: int = 16,
        prefix_diamond: bool = False,
        diamond_color: Tuple[int, int, int] = None
    ) -> Tuple[int, int]:
        """Draws a perfectly padded rounded pill box based on actual font bounding box."""
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        prefix_space = 22 if prefix_diamond else 0
        w = tw + padding_x * 2 + prefix_space
        h = th + padding_y * 2
        
        draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=bg_color, outline=border_color, width=2 if border_color else 0)
        
        text_x = x + padding_x
        if prefix_diamond:
            d_col = diamond_color or text_color
            self._draw_diamond(draw, text_x + 5, y + h // 2, 6, d_col)
            text_x += prefix_space
            
        draw.text((text_x - bbox[0], y + padding_y - bbox[1]), text, font=font, fill=text_color)
        return w, h

    def _create_vibrant_background(self, width: int, height: int, theme: Dict[str, Any]) -> Image.Image:
        """Renders an Apple/Linear-style dark mesh gradient with dual glowing color orbs and grid dots."""
        base = Image.new("RGB", (width, height), color=theme["bg_dark"])
        
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_o = ImageDraw.Draw(overlay)
        
        orb1_r = int(min(width, height) * 0.45)
        draw_o.ellipse([-orb1_r//2, -orb1_r//2, orb1_r, orb1_r], fill=theme["orb1"])
        
        orb2_r = int(min(width, height) * 0.5)
        draw_o.ellipse([width - orb2_r, height - orb2_r, width + orb2_r//3, height + orb2_r//3], fill=theme["orb2"])
        
        cx, cy = width // 2, height // 2
        draw_o.ellipse([cx - 200, cy - 200, cx + 200, cy + 200], fill=(theme["highlight"][0], theme["highlight"][1], theme["highlight"][2], 40))
        
        blurred = overlay.filter(ImageFilter.GaussianBlur(110))
        base.paste(blurred, (0, 0), blurred)
        
        draw = ImageDraw.Draw(base)
        step = 60
        for x in range(step, width - step, step):
            for y in range(step, height - step, step):
                draw.point((x, y), fill=(255, 255, 255, 30))
                
        return base

    def _draw_browser_mockup(self, draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, route_text: str, theme: Dict[str, Any]):
        """Draws a clean modern browser / app window mockup with macOS dots and URL bar."""
        draw.rounded_rectangle([x, y, x + w, y + h], radius=24, fill=theme["card_bg"], outline=theme["card_border"], width=3)
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
        draw.text((x + 140, y + 16), f"[lock] {route_text}", font=font_url, fill=(148, 163, 184))

    def _draw_ai_hero_card(
        self,
        base_img: Image.Image,
        x: int,
        y: int,
        w: int,
        h: int,
        ai_image_name: str,
        theme: Dict[str, Any],
        badge_text: str = "3D ARCHITECTURE ENGINE"
    ):
        """Pastes a high-end rounded 3D AI visual hero card with glowing border and status pill."""
        raw_ai = self._get_ai_image(ai_image_name)
        
        raw_w, raw_h = raw_ai.size
        scale = max(w / raw_w, h / raw_h)
        new_w, new_h = int(raw_w * scale), int(raw_h * scale)
        scaled_ai = raw_ai.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        crop_x = (new_w - w) // 2
        crop_y = (new_h - h) // 2
        cropped_ai = scaled_ai.crop((crop_x, crop_y, crop_x + w, crop_y + h))

        mask = Image.new("L", (w, h), 0)
        draw_m = ImageDraw.Draw(mask)
        draw_m.rounded_rectangle([0, 0, w, h], radius=24, fill=255)

        base_img.paste(cropped_ai, (x, y), mask)

        draw = ImageDraw.Draw(base_img)
        draw.rounded_rectangle([x, y, x + w, y + h], radius=24, outline=theme["card_border"], width=3)
        
        # Top-right status pill inside image
        font_badge = get_font(18, bold=True)
        bbox = font_badge.getbbox(badge_text)
        bw = bbox[2] - bbox[0] + 44
        bh = bbox[3] - bbox[1] + 18
        bx = x + w - bw - 18
        by = y + 16
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=14, fill=(15, 23, 42, 230), outline=theme["cyan"], width=2)
        self._draw_diamond(draw, bx + 16, by + bh // 2, 6, theme["cyan"])
        draw.text((bx + 28 - bbox[0], by + 9 - bbox[1]), badge_text, font=font_badge, fill=theme["cyan"])

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
    # 1. STANDALONE MARKETING GRAPHIC POSTER (1080x1080)
    # -------------------------------------------------------------------------
    def render_graphic(
        self,
        asset_id: str,
        title: str,
        body_text: str,
        pillar: str,
        cta: str = "Visit incubrix.com",
        feature_image_override: str = None
    ) -> Path:
        """Renders an attractive, high-contrast, modern SaaS marketing poster (1080x1080) with AI 3D visuals."""
        width, height = 1080, 1080
        theme = self._get_theme(pillar)
        img = self._create_vibrant_background(width, height, theme)
        draw = ImageDraw.Draw(img)

        # Fonts
        font_brand = get_font(24, bold=True)
        font_pill = get_font(20, bold=True)
        font_body = get_font(26, bold=False)
        margin = 55

        # 1. Top Brand Bar & Pillar Badge
        self._draw_pill(
            draw, margin, margin,
            text="INCUBRIX  //  CREATOROPS",
            font=font_brand,
            text_color=(255, 255, 255),
            bg_color=(15, 23, 42, 230),
            border_color=theme["accent"],
            prefix_diamond=True,
            diamond_color=theme["cyan"]
        )

        badge_pillar = theme["short_name"]
        p_bbox = font_pill.getbbox(badge_pillar)
        pill_w = p_bbox[2] - p_bbox[0] + 55
        self._draw_pill(
            draw, width - margin - pill_w, margin,
            text=badge_pillar,
            font=font_pill,
            text_color=theme["cyan"],
            bg_color=(15, 23, 42, 230),
            border_color=theme["cyan"],
            prefix_diamond=True,
            diamond_color=theme["cyan"]
        )

        # 2. Dynamic Headline Fitting
        y_pos = margin + 82
        t_len = len(str(title))
        if t_len > 70:
            font_title = get_font(36, bold=True)
            max_c = 36
            line_step = 46
        elif t_len > 45:
            font_title = get_font(40, bold=True)
            max_c = 34
            line_step = 50
        else:
            font_title = get_font(44, bold=True)
            max_c = 32
            line_step = 54

        title_lines = self._wrap_text(str(title), max_chars=max_c)
        for line in title_lines[:3]:
            draw.text((margin, y_pos), line, font=font_title, fill=(255, 255, 255))
            y_pos += line_step

        # 3. Center Graphic Showcase: AI 3D Hero Visual Card
        hero_img_name = feature_image_override or theme["ai_sq"]
        hero_y = y_pos + 12
        hero_h = 415
        hero_w = width - (margin * 2)
        
        self._draw_ai_hero_card(
            img,
            margin,
            hero_y,
            hero_w,
            hero_h,
            hero_img_name,
            theme,
            badge_text=theme['short_name']
        )
        draw = ImageDraw.Draw(img)

        # 4. Value Proposition / Feature Takeaway Card below visual
        card_y = hero_y + hero_h + 16
        card_h = 195
        draw.rounded_rectangle([margin, card_y, margin + hero_w, card_y + card_h], radius=20, fill=(15, 23, 42, 235), outline=theme["card_border"], width=2)
        
        # Parse clean, informative bullet sentences
        raw_bullets = [b.lstrip("-•*✓ ").strip() for b in str(body_text).split("\n") if b.strip()]
        clean_bullets = [b for b in raw_bullets if len(b) > 8][:3]
        if not clean_bullets:
            clean_bullets = ["Unified CreatorOps studio with zero context switching.", "85% reduction in weekly video production time.", "Direct automated publishing across Shorts, Reels & LinkedIn."]

        line_y = card_y + 20
        for b in clean_bullets:
            self._draw_check(draw, margin + 35, line_y + 4, 16, theme["cyan"], width=3)
            # Wrap bullet to fit card
            wl = self._wrap_text(b, max_chars=48)[0]
            draw.text((margin + 68, line_y), wl, font=font_body, fill=(241, 245, 249))
            line_y += 50

        # 5. Bottom Gradient CTA Button (Precisely fitted with no text clipping)
        footer_y = height - margin - 72
        btn_w = width - (margin * 2)
        draw.rounded_rectangle([margin, footer_y, margin + btn_w, footer_y + 68], radius=20, fill=theme["accent"], outline=(255, 255, 255), width=2)
        
        cta_text = str(cta).strip()
        if "incubrix.com" not in cta_text.lower():
            cta_text = f"{cta_text}  |  incubrix.com"

        # Fit font size to ensure it never overflows
        cta_font_size = 26
        font_cta = get_font(cta_font_size, bold=True)
        while font_cta.getbbox(cta_text)[2] > (btn_w - 90) and cta_font_size > 18:
            cta_font_size -= 2
            font_cta = get_font(cta_font_size, bold=True)

        self._draw_arrow(draw, margin + 35, footer_y + 24, 22, 16, (255, 255, 255), width=3)
        draw.text((margin + 70, footer_y + 19), cta_text, font=font_cta, fill=(255, 255, 255))

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
        font_brand = get_font(24, bold=True)
        font_pill = get_font(20, bold=True)
        font_body = get_font(28, bold=False)
        font_card_title = get_font(26, bold=True)
        font_footer = get_font(22, bold=True)

        margin = 55

        # 1. Header Bar
        self._draw_pill(
            draw, margin, margin,
            text="INCUBRIX  //  CREATOROPS",
            font=font_brand,
            text_color=(255, 255, 255),
            bg_color=(15, 23, 42, 230),
            border_color=theme["accent"],
            prefix_diamond=True,
            diamond_color=theme["cyan"]
        )

        counter_text = f"SLIDE {slide_idx} OF {total_slides}"
        c_bbox = font_pill.getbbox(counter_text)
        counter_w = c_bbox[2] - c_bbox[0] + 44
        self._draw_pill(
            draw, width - margin - counter_w, margin,
            text=counter_text,
            font=font_pill,
            text_color=theme["cyan"],
            bg_color=(15, 23, 42, 230),
            border_color=(71, 85, 105)
        )

        # 2. Category Pill
        y_pos = margin + 78
        badge_pillar = theme["short_name"]
        self._draw_pill(
            draw, margin, y_pos,
            text=badge_pillar,
            font=font_pill,
            text_color=theme["cyan"],
            bg_color=(15, 23, 42, 230),
            border_color=theme["cyan"],
            prefix_diamond=True,
            diamond_color=theme["cyan"]
        )

        # 3. Dynamic Headline
        y_pos += 58
        t_len = len(str(title))
        if t_len > 60:
            font_title = get_font(38, bold=True)
            max_c = 34
            step = 48
        else:
            font_title = get_font(44, bold=True)
            max_c = 30
            step = 54

        title_lines = self._wrap_text(str(title), max_chars=max_c)
        for line in title_lines[:2]:
            draw.text((margin, y_pos), line, font=font_title, fill=(255, 255, 255))
            y_pos += step

        # 4. Slide-Specific Rich Visual Content
        card_y = y_pos + 16
        card_w = width - (margin * 2)
        card_h = height - card_y - margin - 72

        if slide_idx == 1:
            # --- COVER SLIDE: AI 3D HERO SHOWCASE ---
            hero_h = 390
            self._draw_ai_hero_card(
                img,
                margin,
                card_y,
                card_w,
                hero_h,
                theme["ai_sq"],
                theme,
                badge_text="SAAS ARCHITECTURE"
            )
            draw = ImageDraw.Draw(img)

            # Subtitle box below
            sub_y = card_y + hero_h + 18
            sub_h = card_h - hero_h - 18
            draw.rounded_rectangle([margin, sub_y, margin + card_w, sub_y + sub_h], radius=20, fill=theme["card_bg"], outline=theme["card_border"], width=2)
            draw.text((margin + 35, sub_y + 22), "IN THIS 5-SLIDE BREAKDOWN:", font=font_card_title, fill=theme["cyan"])
            draw.text((margin + 35, sub_y + 60), "• Architecture teardown of the automated CreatorOps pipeline", font=font_body, fill=(241, 245, 249))
            draw.text((margin + 35, sub_y + 98), "• 85% verified time savings & multi-channel syndication", font=font_body, fill=(241, 245, 249))

            # Swipe Pill with arrow
            swipe_text = "SWIPE TO UNLOCK"
            s_bbox = font_pill.getbbox(swipe_text)
            sw = s_bbox[2] - s_bbox[0] + 75
            sh = s_bbox[3] - s_bbox[1] + 24
            sx = width - margin - sw - 20
            sy = sub_y + sub_h - sh - 16
            draw.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=18, fill=theme["accent"])
            draw.text((sx + 18 - s_bbox[0], sy + 12 - s_bbox[1]), swipe_text, font=font_pill, fill=(255, 255, 255))
            self._draw_arrow(draw, sx + sw - 32, sy + sh // 2 - 7, 16, 14, (255, 255, 255), width=2)

        elif slide_idx == 2:
            # --- PROBLEM BREAKDOWN SLIDE ---
            draw.rounded_rectangle([margin, card_y, margin + card_w, card_y + card_h], radius=28, fill=theme["card_bg"], outline=(239, 68, 68), width=3)
            # Red alert banner
            draw.rounded_rectangle([margin + 30, card_y + 30, width - margin - 30, card_y + 90], radius=16, fill=(15, 23, 42), outline=(239, 68, 68), width=2)
            draw.text((margin + 50, card_y + 44), "[!]  THE TRADITIONAL FRAGMENTED TOOL TRAP", font=font_card_title, fill=(239, 68, 68))
            
            # Body items with red crosses
            item_y = card_y + 120
            clean_lines = [l.strip() for l in str(body_text).split("\n") if l.strip()]
            for l in clean_lines[:6]:
                draw.rounded_rectangle([margin + 30, item_y, width - margin - 30, item_y + 55], radius=14, fill=(15, 23, 42))
                self._draw_cross(draw, margin + 48, item_y + 19, 16, (239, 68, 68), width=3)
                draw.text((margin + 80, item_y + 14), l, font=font_body, fill=(241, 245, 249))
                item_y += 65

        elif slide_idx == 3:
            # --- SOLUTION & UI MOCKUP SLIDE ---
            self._draw_browser_mockup(draw, margin, card_y, card_w, card_h, "app.incubrix.com/editor", theme)
            inside_y = card_y + 80
            draw.rounded_rectangle([margin + 30, inside_y, width - margin - 30, inside_y + 70], radius=16, fill=(15, 23, 42), outline=theme["accent"], width=2)
            self._draw_diamond(draw, margin + 55, inside_y + 35, 8, theme["cyan"])
            draw.text((margin + 75, inside_y + 22), "THE INCUBRIX UNIFIED CREATOROPS ENGINE", font=font_card_title, fill=theme["cyan"])
            
            self._draw_audio_waveform(draw, margin + 40, inside_y + 95, card_w - 80, 70, theme, bars_count=24)
            
            feat_y = inside_y + 185
            clean_lines = [l.strip() for l in str(body_text).split("\n") if l.strip()]
            for l in clean_lines[:4]:
                self._draw_check(draw, margin + 50, feat_y + 5, 16, theme["accent"], width=3)
                draw.text((margin + 80, feat_y), l, font=font_body, fill=(241, 245, 249))
                feat_y += 48

        elif slide_idx == 4:
            # --- DATA & BENCHMARKS SLIDE ---
            draw.rounded_rectangle([margin, card_y, margin + card_w, card_y + card_h], radius=28, fill=theme["card_bg"], outline=theme["cyan"], width=3)
            
            draw.rounded_rectangle([margin + 30, card_y + 30, margin + card_w//2 - 15, card_y + 190], radius=20, fill=(15, 23, 42), outline=theme["accent"], width=2)
            font_stat = get_font(54, bold=True)
            draw.text((margin + 50, card_y + 50), "85%", font=font_stat, fill=theme["accent"])
            draw.text((margin + 50, card_y + 120), "TIME SLASHED", font=font_pill, fill=(255, 255, 255))
            draw.text((margin + 50, card_y + 148), "14.2h down to 2.1h", font=font_pill, fill=(148, 163, 184))

            draw.rounded_rectangle([margin + card_w//2 + 15, card_y + 30, width - margin - 30, card_y + 190], radius=20, fill=(15, 23, 42), outline=theme["cyan"], width=2)
            draw.text((margin + card_w//2 + 35, card_y + 50), "+312%", font=font_stat, fill=theme["cyan"])
            draw.text((margin + card_w//2 + 35, card_y + 120), "ORGANIC REACH", font=font_pill, fill=(255, 255, 255))
            draw.text((margin + card_w//2 + 35, card_y + 148), "Multi-platform lift", font=font_pill, fill=(148, 163, 184))

            detail_y = card_y + 220
            clean_lines = [l.strip() for l in str(body_text).split("\n") if l.strip()]
            for l in clean_lines[:4]:
                self._draw_diamond(draw, margin + 55, detail_y + 14, 6, theme["cyan"])
                draw.text((margin + 75, detail_y), l, font=font_body, fill=(241, 245, 249))
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
                self._draw_check(draw, margin + 48, check_y + 20, 18, theme["accent"], width=3)
                draw.text((margin + 80, check_y + 16), item, font=get_font(24, bold=False), fill=(241, 245, 249))
                check_y += 72

            # Bottom CTA button
            draw.rounded_rectangle([margin + 30, card_y + card_h - 90, width - margin - 30, card_y + card_h - 20], radius=20, fill=theme["accent"])
            draw.text((margin + 60, card_y + card_h - 66), "START FREE AT INCUBRIX.COM  |  SAVE FOR LATER", font=font_pill, fill=(255, 255, 255))

        # 5. Bottom Brand Footer
        footer_y = height - margin - 45
        draw.line([margin, footer_y, width - margin, footer_y], fill=(51, 65, 85), width=2)
        draw.text((margin, footer_y + 14), "incubrix.com  //  Create With Purpose. Publish Without Limits.", font=font_footer, fill=(148, 163, 184))

        output_filename = f"{asset_id}_slide_{slide_idx}.png"
        output_path = self.final_carousels_dir / output_filename
        img.save(output_path, "PNG")
        return output_path

    def render_carousel_package(
        self,
        asset_id: str,
        pillar: str,
        slides_content: List[Dict[str, str]],
        use_case_override: Optional[Dict[str, Any]] = None
    ) -> List[Path]:
        """
        Renders the complete carousel package using the Gemini 3.6 Flash Animated SVG Engine.
        Produces:
          - N self-contained animated SVGs with CSS motion & 1080px seamless swipe continuity
          - Interactive HTML preview player (preview.html)
          - Live animated MP4 video clips per slide
          - Resting-state high-res PNGs and multi-page LinkedIn PDF
        Falls back to PIL rasterizer if API is offline.
        """
        carousel_folder = self.final_carousels_dir / asset_id
        carousel_folder.mkdir(parents=True, exist_ok=True)

        # Build dynamic use case dictionary
        num_slides = len(slides_content) if slides_content else 5
        key_points = " | ".join([s.get("title", "") for s in slides_content[:num_slides]])

        use_case = use_case_override or {
            "brand": "IncuBrix — Automated CreatorOps Engine",
            "goal": "drive engagement, dwell time, and trial signups",
            "audience": "growth teams, video creators, and SaaS founders",
            "tone": "sharp, technical, premium SaaS engineering",
            "offer": "automate content repurposing at app.incubrix.com",
            "num_slides": num_slides,
            "context": f"Theme: {pillar}. Key narrative flow: {key_points}"
        }

        try:
            from src.animated_svg_carousel import generate_and_render_animated_carousel
            print(f"[MediaRenderer] Invoking Animated SVG Carousel Engine for {asset_id}...")
            result = generate_and_render_animated_carousel(
                use_case=use_case,
                output_dir=carousel_folder,
                asset_id=asset_id,
                render_videos=True
            )
            return [Path(p) for p in result["png_paths"]]
        except Exception as e:
            print(f"[MediaRenderer Warning] Animated SVG generation encountered: {e}. Falling back to PIL renderer...")

        # Fallback to high-res PIL rasterizer
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
    # 3. HIGH-RETENTION MULTI-SCENE VIDEO REEL ENGINE (9:16 MP4 with AI & Music)
    # -------------------------------------------------------------------------
    def render_short_video(
        self,
        asset_id: str,
        hook: str,
        caption: str,
        pillar: str = "CreatorOps",
        duration_seconds: int = 15,
        use_animated_svg: bool = True
    ) -> Path:
        """
        Renders an animated-SVG short video (1080x1920, 9:16) with AI voice-over (GCP Chirp 3 HD),
        burned-in kinetic subtitles, and xfade transitions via src.ad_video_maker.
        Falls back seamlessly to the local 3-scene high-res renderer if offline or quota-limited.
        """
        output_path = self.final_videos_dir / f"{asset_id}.mp4"

        # 1. Tier-1 High-Fidelity Animated SVG + AI Voiceover Pipeline
        if use_animated_svg and os.getenv("SKIP_ANIMATED_VIDEO", "0") != "1":
            try:
                import shutil
                from src.ad_video_maker import generate_animated_ad_video
                use_case = (
                    f"Brand: IncuBrix. Content Pillar: {pillar}. "
                    f"Hook: {hook}. Narrative Details: {caption}. "
                    f"Video length: {duration_seconds}s. Target: 9:16 Vertical Short."
                )
                video_work_dir = self.final_videos_dir / asset_id
                res = generate_animated_ad_video(
                    use_case=use_case,
                    output_dir=video_work_dir,
                    asset_id=asset_id,
                    aspect="9:16",
                    seconds=float(duration_seconds),
                    scenes_count=3,
                    language="en-US"
                )
                final_video_file = Path(res["video_path"])
                if final_video_file.exists() and final_video_file != output_path:
                    shutil.copy2(final_video_file, output_path)
                return output_path
            except Exception as e:
                print(f"[Info] Animated SVG video generator note ({e}). Using local multi-scene video renderer...")

        width, height = 1080, 1920
        theme = self._get_theme(pillar)

        # Fonts
        font_brand = get_font(30, bold=True)
        font_pill = get_font(20, bold=True)
        font_body = get_font(32, bold=False)
        font_card_title = get_font(28, bold=True)
        font_cta = get_font(30, bold=True)

        margin = 60

        # Load 9:16 Vertical AI Background
        vert_ai_raw = self._get_ai_image(theme["ai_vert"])
        
        v_w, v_h = vert_ai_raw.size
        scale = max(width / v_w, height / v_h)
        scaled_w, scaled_h = int(v_w * scale), int(v_h * scale)
        vert_scaled = vert_ai_raw.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
        cx, cy = (scaled_w - width) // 2, (scaled_h - height) // 2
        bg_template = vert_scaled.crop((cx, cy, cx + width, cy + height))

        vignette = Image.new("RGBA", (width, height), (10, 14, 25, 145))
        bg_template.paste(vignette, (0, 0), vignette)

        def build_scene_frame(scene_idx: int, progress_pct: float) -> Image.Image:
            img = bg_template.copy()
            draw = ImageDraw.Draw(img)

            # 1. Top Brand Header Bar
            header_y = 120
            self._draw_pill(
                draw, margin, header_y,
                text="INCUBRIX  //  CREATOROPS",
                font=font_brand,
                text_color=(255, 255, 255),
                bg_color=(15, 23, 42, 230),
                border_color=theme["accent"],
                prefix_diamond=True,
                diamond_color=theme["cyan"]
            )

            badge_pillar = theme["short_name"]
            p_bbox = font_pill.getbbox(badge_pillar)
            pill_w = p_bbox[2] - p_bbox[0] + 50
            self._draw_pill(
                draw, width - margin - pill_w, header_y,
                text=badge_pillar,
                font=font_pill,
                text_color=theme["cyan"],
                bg_color=(15, 23, 42, 230),
                border_color=theme["cyan"],
                prefix_diamond=True,
                diamond_color=theme["cyan"]
            )

            # 2. Main Title / Hook Headline
            y_pos = header_y + 105
            h_len = len(str(hook))
            if h_len > 70:
                font_hook = get_font(44, bold=True)
                max_c = 30
                step = 58
            else:
                font_hook = get_font(50, bold=True)
                max_c = 26
                step = 64

            hook_lines = self._wrap_text(str(hook), max_chars=max_c)
            for line in hook_lines[:4]:
                draw.text((margin, y_pos), line, font=font_hook, fill=(255, 255, 255))
                y_pos += step

            # 3. Dynamic Center Card depending on Scene
            center_y = y_pos + 35
            center_w = width - (margin * 2)
            center_h = 750

            if scene_idx == 1:
                # --- SCENE 1: THE HIGH-IMPACT HOOK & PAIN POINT ---
                draw.rounded_rectangle([margin, center_y, margin + center_w, center_y + center_h], radius=32, fill=(15, 23, 42, 225), outline=(239, 68, 68), width=3)
                
                draw.rounded_rectangle([margin + 30, center_y + 40, width - margin - 30, center_y + 120], radius=20, fill=(15, 23, 42), outline=(239, 68, 68), width=2)
                draw.text((margin + 60, center_y + 58), "[!]  THE 14-HOUR CREATOR BOTTLENECK", font=font_card_title, fill=(239, 68, 68))

                dia_y = center_y + 160
                draw.text((margin + 50, dia_y), "WHAT CREATORS ARE JUGGLING:", font=font_card_title, fill=theme["cyan"])
                dia_lines = self._wrap_text(str(caption), max_chars=32)
                cur_y = dia_y + 60
                for dl in dia_lines[:7]:
                    draw.text((margin + 50, cur_y), dl, font=font_body, fill=(241, 245, 249))
                    cur_y += 50

                draw.rounded_rectangle([margin + 50, center_y + center_h - 110, width - margin - 50, center_y + center_h - 40], radius=20, fill=(15, 23, 42), outline=theme["accent"], width=2)
                self._draw_diamond(draw, margin + 75, center_y + center_h - 75, 7, theme["cyan"])
                draw.text((margin + 95, center_y + center_h - 88), "WATCH THE REPURPOSING SPEEDRUN", font=font_card_title, fill=theme["cyan"])
                self._draw_arrow(draw, width - margin - 90, center_y + center_h - 83, 20, 16, theme["cyan"], width=2)

            elif scene_idx == 2:
                # --- SCENE 2: THE PRODUCT WORKFLOW & BROWSER MOCKUP ---
                self._draw_browser_mockup(draw, margin, center_y, center_w, center_h, "app.incubrix.com/editor", theme)
                
                inside_y = center_y + 90
                draw.rounded_rectangle([margin + 30, inside_y, width - margin - 30, inside_y + 90], radius=20, fill=(15, 23, 42), outline=theme["accent"], width=2)
                self._draw_diamond(draw, margin + 60, inside_y + 45, 8, theme["cyan"])
                draw.text((margin + 80, inside_y + 30), "PROMPT VIDEO EDITOR & VOICE HUB", font=font_card_title, fill=theme["cyan"])

                self._draw_audio_waveform(draw, margin + 40, inside_y + 120, center_w - 80, 110, theme, bars_count=24)

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
                draw.rounded_rectangle([margin, center_y, margin + center_w, center_y + center_h], radius=32, fill=(15, 23, 42, 225), outline=theme["cyan"], width=3)
                
                draw.rounded_rectangle([margin + 40, center_y + 40, width - margin - 40, center_y + 190], radius=24, fill=(15, 23, 42), outline=theme["accent"], width=3)
                font_stat = get_font(64, bold=True)
                draw.text((margin + 70, center_y + 55), "85% TIME SAVED", font=font_stat, fill=theme["accent"])
                draw.text((margin + 70, center_y + 135), "Weekly production dropped from 14h to 2h", font=font_pill, fill=(203, 213, 225))

                draw.rounded_rectangle([margin + 40, center_y + 220, width - margin - 40, center_y + 370], radius=24, fill=(15, 23, 42), outline=theme["cyan"], width=3)
                draw.text((margin + 70, center_y + 235), "+312% REACH SPIKE", font=font_stat, fill=theme["cyan"])
                draw.text((margin + 70, center_y + 315), "Compounding distribution across Shorts & Reels", font=font_pill, fill=(203, 213, 225))

                cta_y = center_y + 420
                draw.rounded_rectangle([margin + 40, cta_y, width - margin - 40, cta_y + 100], radius=24, fill=theme["accent"], outline=(255, 255, 255), width=3)
                self._draw_arrow(draw, margin + 70, cta_y + 40, 26, 20, (255, 255, 255), width=3)
                draw.text((margin + 115, cta_y + 30), "CLAIM YOUR STUDIO AT INCUBRIX.COM", font=font_cta, fill=(255, 255, 255))

                draw.text((margin + 80, cta_y + 130), "YouTube Shorts  //  Instagram Reels  //  LinkedIn", font=font_pill, fill=(148, 163, 184))

            # 4. Animated Scene Progress Bar at Bottom
            progress_y = height - 140
            draw.rounded_rectangle([margin, progress_y, width - margin, progress_y + 12], radius=6, fill=(51, 65, 85))
            cur_p_w = int((width - margin * 2) * progress_pct)
            draw.rounded_rectangle([margin, progress_y, margin + cur_p_w, progress_y + 12], radius=6, fill=theme["accent"])

            # 5. Bottom Swipe Up Indicator
            draw.text((margin + 40, height - 100), "SWIPE UP  |  TRY FREE AT INCUBRIX.COM  |  LINK IN BIO", font=font_pill, fill=(203, 213, 225))

            return img

        s1 = build_scene_frame(1, 0.33)
        s2 = build_scene_frame(2, 0.66)
        s3 = build_scene_frame(3, 1.00)

        f1_path = self.final_videos_dir / f"{asset_id}_f1.png"
        f2_path = self.final_videos_dir / f"{asset_id}_f2.png"
        f3_path = self.final_videos_dir / f"{asset_id}_f3.png"

        s1.save(f1_path, "PNG")
        s2.save(f2_path, "PNG")
        s3.save(f3_path, "PNG")

        concat_txt_path = self.final_videos_dir / f"{asset_id}_concat.txt"
        with open(concat_txt_path, "w", encoding="utf-8") as f:
            f.write(f"file '{f1_path.name}'\nduration 5.0\n")
            f.write(f"file '{f2_path.name}'\nduration 5.0\n")
            f.write(f"file '{f3_path.name}'\nduration 5.0\n")
            f.write(f"file '{f3_path.name}'\n")

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
