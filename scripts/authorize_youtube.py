#!/usr/bin/env python3
"""
authorize_youtube.py
====================
Interactive YouTube OAuth 2.0 authorization helper for IncuBrix.
Uses Google Desktop Application loopback redirect to obtain access & refresh tokens,
stores them in token.json and updates .env.
"""

import os
import sys
import json
import urllib.parse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config import YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET

PORT = 80
REDIRECT_URI = "http://localhost"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
]

auth_code = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        if "code" in qs:
            auth_code = qs["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""
                <!DOCTYPE html>
                <html>
                <head><title>IncuBrix - YouTube Authorized</title></head>
                <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #0f172a; color: white;">
                    <div style="background: #1e293b; padding: 40px; border-radius: 16px; text-align: center; max-width: 480px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); border: 1px solid #334155;">
                        <div style="font-size: 48px; margin-bottom: 16px;">&#x2705;</div>
                        <h1 style="margin: 0 0 12px; font-size: 24px; color: #38bdf8;">YouTube Connected!</h1>
                        <p style="margin: 0 0 24px; color: #94a3b8; font-size: 14px; line-height: 1.5;">IncuBrix Growth Engine has successfully linked to your YouTube channel. You can close this tab and return to the terminal.</p>
                        <div style="font-size: 12px; color: #64748b; background: #0f172a; padding: 8px 16px; border-radius: 8px;">OAuth token exchanged successfully</div>
                    </div>
                </body>
                </html>
            """)
        elif "error" in qs:
            error = qs["error"][0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<h1>Authorization Failed: {error}</h1>".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress default noisy console logs


def exchange_code_for_token(code: str, redirect_uri: str) -> dict:
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    resp = requests.post(token_url, data=data, timeout=30)
    return resp.json()


def save_token_and_update_env(token_data: dict):
    token_file = BASE_DIR / "token.json"
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)

    access_token = token_data.get("access_token", "")
    refresh_token = token_data.get("refresh_token", "")

    # Update .env
    env_file = BASE_DIR / ".env"
    lines = []
    if env_file.exists():
        lines = env_file.read_text(encoding="utf-8").splitlines()

    new_lines = []
    has_yt_access = False
    has_yt_refresh = False

    for line in lines:
        if line.startswith("YOUTUBE_ACCESS_TOKEN="):
            new_lines.append(f"YOUTUBE_ACCESS_TOKEN={access_token}")
            has_yt_access = True
        elif line.startswith("YOUTUBE_REFRESH_TOKEN="):
            new_lines.append(f"YOUTUBE_REFRESH_TOKEN={refresh_token}")
            has_yt_refresh = True
        else:
            new_lines.append(line)

    if not has_yt_access:
        new_lines.append(f"YOUTUBE_ACCESS_TOKEN={access_token}")
    if not has_yt_refresh and refresh_token:
        new_lines.append(f"YOUTUBE_REFRESH_TOKEN={refresh_token}")

    env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    os.environ["YOUTUBE_ACCESS_TOKEN"] = access_token
    if refresh_token:
        os.environ["YOUTUBE_REFRESH_TOKEN"] = refresh_token

    print(f"\n[OK] OAuth Token saved to token.json and .env successfully!")


def main():
    global auth_code

    if "--code" in sys.argv:
        idx = sys.argv.index("--code")
        if idx + 1 < len(sys.argv):
            code = sys.argv[idx + 1]
            print(f"[*] Exchanging provided code for OAuth tokens...")
            token_data = exchange_code_for_token(code, REDIRECT_URI)
            if "access_token" not in token_data:
                # Try fallback redirect uri without port
                token_data = exchange_code_for_token(code, "http://localhost")
            if "access_token" not in token_data:
                print(f"[ERROR] Failed to obtain access token: {token_data}")
                sys.exit(1)
            save_token_and_update_env(token_data)
            print("\n[SUCCESS] YouTube is now fully authorized for LIVE uploads!")
            sys.exit(0)

    print("=" * 70)
    print("IncuBrix YouTube Channel Authorization Setup")
    print("=" * 70)

    if not YOUTUBE_CLIENT_ID or not YOUTUBE_CLIENT_SECRET:
        print("[FAIL] Missing YOUTUBE_CLIENT_ID or YOUTUBE_CLIENT_SECRET in .env")
        sys.exit(1)

    params = {
        "client_id": YOUTUBE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

    print("\nPlease authorize your YouTube channel by visiting this URL:\n")
    print("-" * 70)
    print(auth_url)
    print("-" * 70)
    print(f"\nWaiting for authorization callback on {REDIRECT_URI} ...")

    # Try opening browser automatically
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    # Start local HTTP server to capture code
    server = HTTPServer(("127.0.0.1", PORT), OAuthCallbackHandler)
    server.timeout = 180  # 3 minutes

    while not auth_code:
        server.handle_request()

    print(f"\n[+] Authorization code captured: {auth_code[:15]}...")
    print("[*] Exchanging authorization code for OAuth tokens...")

    token_data = exchange_code_for_token(auth_code, REDIRECT_URI)

    if "access_token" not in token_data:
        print(f"[ERROR] Failed to obtain access token: {token_data}")
        sys.exit(1)

    save_token_and_update_env(token_data)
    print("\n[SUCCESS] YouTube is now fully authorized for LIVE uploads!")


if __name__ == "__main__":
    main()
