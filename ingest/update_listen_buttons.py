#!/usr/bin/env python3
"""
update_listen_buttons.py

Deterministic updater for episode-specific Listen buttons on mdBook episode pages (src/<ep>.md).
Reads dd_hub/episodes/<ep>/podcast_urls.json and renders exactly three buttons (Spotify, Apple Podcasts, Fountain.fm).
YouTube Music is excluded from page rendering by design decision.

Wrapped in <!-- LISTEN_BUTTONS_START --> ... <!-- LISTEN_BUTTONS_END -->.
"""

import os
import sys
import json
import re
from pathlib import Path

# Resolve repo root anchored on this script
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"

DEFAULT_FALLBACKS = {
    "spotify": "https://open.spotify.com/show/7doWf0GON9JsG6r8igc7RE",
    "apple_podcasts": "https://podcasts.apple.com/us/podcast/deep-dive-with-gemini/id1844532251",
    "fountain": "https://fountain.fm/show/7LBvZT6ffpGyubvk8aSF"
}

def resolve_hub_root() -> Path:
    env_hub = os.environ.get("DD_HUB_ROOT")
    if env_hub and os.path.exists(env_hub):
        return Path(env_hub)
    candidates = [
        Path("G:/My Drive/dd_hub"),
        Path("/mnt/gdrive/dd_hub"),
        Path("/workspace/dd_hub"),
        Path.home() / "Google Drive" / "dd_hub",
        Path.home() / "dd_hub"
    ]
    for c in candidates:
        if c.exists():
            return c
    return Path("G:/My Drive/dd_hub")

def generate_button_block(spotify_url: str, apple_url: str, fountain_url: str) -> str:
    btn_style_mid = 'style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;"'
    btn_style_end = 'style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px;"'
    
    html = (
        '<!-- LISTEN_BUTTONS_START -->\n'
        f'<center><a href="{spotify_url}" target="_blank" {btn_style_mid}>Spotify</a>'
        f'<a href="{apple_url}" target="_blank" {btn_style_mid}>Apple Podcasts</a>'
        f'<a href="{fountain_url}" target="_blank" {btn_style_end}>Fountain.fm</a></center>\n'
        '<!-- LISTEN_BUTTONS_END -->'
    )
    return html

def update_episode_listen_buttons(ep_num: str) -> bool:
    clean_ep = str(ep_num).replace('.md', '').lstrip('_')
    md_path = SRC_DIR / f"{clean_ep}.md"
    if not md_path.exists():
        print(f"[ERROR] Markdown file {md_path} does not exist.", file=sys.stderr)
        return False

    hub_root = resolve_hub_root()
    urls_file = hub_root / "episodes" / clean_ep / "podcast_urls.json"

    spotify_url = DEFAULT_FALLBACKS["spotify"]
    apple_url = DEFAULT_FALLBACKS["apple_podcasts"]
    fountain_url = DEFAULT_FALLBACKS["fountain"]

    if urls_file.exists():
        try:
            with open(urls_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            platforms = data.get("platforms", {})
            fallbacks = data.get("fallback_show_urls", {})
            
            spotify_url = platforms.get("spotify") or fallbacks.get("spotify") or spotify_url
            apple_url = platforms.get("apple_podcasts") or fallbacks.get("apple_podcasts") or apple_url
            fountain_url = platforms.get("fountain") or fallbacks.get("fountain") or fountain_url
            print(f"[INFO] Loaded verified URLs from {urls_file}")
        except Exception as e:
            print(f"[WARN] Failed to read {urls_file}: {e}. Retaining fallback show URLs.", file=sys.stderr)
    else:
        print(f"[INFO] {urls_file} not found; using generic show fallbacks.")

    new_block = generate_button_block(spotify_url, apple_url, fountain_url)

    raw_text = md_path.read_text(encoding="utf-8")

    # 1. Check for existing LISTEN_BUTTONS markers
    marker_regex = re.compile(r'<!-- LISTEN_BUTTONS_START -->.*?<!-- LISTEN_BUTTONS_END -->', re.DOTALL)
    if marker_regex.search(raw_text):
        updated_text = marker_regex.sub(new_block, raw_text)
    else:
        # 2. Check for existing legacy spotify <center> block
        legacy_regex = re.compile(r'<center><a href="https://open\.spotify\.com/[^"]+".*?</center>', re.DOTALL)
        if legacy_regex.search(raw_text):
            updated_text = legacy_regex.sub(new_block, raw_text)
        elif '<!-- SOCIALS_END -->' in raw_text:
            updated_text = raw_text.replace('<!-- SOCIALS_END -->', f"{new_block}\n\n<!-- SOCIALS_END -->")
        else:
            updated_text = raw_text + f"\n\n{new_block}\n"

    if updated_text == raw_text:
        print(f"[INFO] Episode {clean_ep} listen buttons already up to date. No write performed.")
        return True

    md_path.write_text(updated_text, encoding="utf-8")
    print(f"[SUCCESS] Updated listen buttons in {md_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_listen_buttons.py <episode_num_or_slug>")
        sys.exit(1)
    ep = sys.argv[1]
    update_episode_listen_buttons(ep)
