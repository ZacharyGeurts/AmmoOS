#!/usr/bin/env python3
"""Shared Open Graph / Twitter Card meta tag snippets."""
from __future__ import annotations

import html

SITE = "https://zacharygeurts.github.io/Field_Primer"
OG_VERSION = "6"
OG_IMAGE = f"{SITE}/assets/images/og-image.jpg?v={OG_VERSION}"
TWITTER_SITE = "@ZacharyGeurts"
DEFAULT_TITLE = "Field Technology v6 — Serious Book · Textbook of 2026"
DEFAULT_DESC = (
    "Reality is 3D. Time is linear. Energy can be moved. "
    "22-chapter operator textbook — Grok16 2.0 single fabric, NEXUS host desktop, Queen gates, sovereign time."
)


def social_meta(
    *,
    title: str = DEFAULT_TITLE,
    description: str = DEFAULT_DESC,
    url: str = f"{SITE}/",
    image: str = OG_IMAGE,
    image_alt: str = "Field Primer — cosmic field fabric with Phi, Thermo, and Flow",
    path_prefix: str = "",
) -> str:
    """Return HTML meta tags. path_prefix is '' for index, '../' for chapters."""
    t = html.escape(title)
    d = html.escape(description)
    u = html.escape(url)
    img = html.escape(image)
    alt = html.escape(image_alt)
    icon = html.escape(f"{SITE}/favicon.png")
    apple = html.escape(f"{SITE}/apple-touch-icon.png")

    return f"""  <meta name="description" content="{d}" />
  <link rel="canonical" href="{u}" />
  <meta name="theme-color" content="#040810" />
  <link rel="icon" type="image/png" sizes="32x32" href="{path_prefix}favicon.png" />
  <link rel="apple-touch-icon" href="{path_prefix}apple-touch-icon.png" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Field Technology v6" />
  <meta property="og:title" content="{t}" />
  <meta property="og:description" content="{d}" />
  <meta property="og:url" content="{u}" />
  <meta property="og:image" content="{img}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{alt}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:site" content="{TWITTER_SITE}" />
  <meta name="twitter:creator" content="{TWITTER_SITE}" />
  <meta name="twitter:title" content="{t}" />
  <meta name="twitter:description" content="{d}" />
  <meta name="twitter:image" content="{img}" />
  <meta name="twitter:image:alt" content="{alt}" />"""


def chapter_meta(num: int, title: str, slug: str, image_file: str, alt: str) -> str:
    page_title = f"{num} — {title} · Field Technology v6"
    desc = f"Chapter {num}: {title}. Field Technology v6 — operator textbook with fullscreen reader, pinch zoom, and honesty labels."
    url = f"{SITE}/chapters/{slug}.html"
    image = f"{SITE}/assets/images/{image_file}"
    return social_meta(
        title=page_title,
        description=desc,
        url=url,
        image=image,
        image_alt=alt,
        path_prefix="../",
    )