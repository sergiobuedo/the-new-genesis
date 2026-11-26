"""Autonomous 24/7 Cloud Daily X Chronicle Publisher (PC-Off Compatible).

Generates a crisp high-DPI scientific visual card from live SQLite/JSON telemetry
(Free Will vs. Instinct-Only Control Twin trajectory + real 1:1 metrics + invented
words) and publishes the proven high-reach 2-tweet format via X's Free API v2:
  - Tweet 1: Gripping 100% factual scientific story + attached real chart (NO outbound link!)
  - Tweet 2 (reply): Direct live observatory link (https://agobac-ia.es) + open-access APA paper.

Reads credentials strictly from environment variables (GitHub Actions Secrets):
  X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
If secrets are not configured yet, runs in dry-run mode and exits 0 cleanly.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render_daily_science_card(
    state: Dict[str, Any],
    db_path: Path,
    out_png: Path,
) -> Path:
    """Renders a sleek, dark-mode scientific telemetry card (1200x675, 16:9 for X)."""
    epochs: List[Dict[str, Any]] = []
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            epochs = [dict(r) for r in conn.execute("SELECT day, live_pop, null_pop FROM epoch_telemetry ORDER BY day ASC").fetchall()]
        finally:
            conn.close()

    w = state.get("world", {})
    m = state.get("metrics", {})
    yr = w.get("year", 1)
    day = w.get("day", 1)
    live_pop = m.get("live_population", 0)
    null_pop = m.get("control_population", 0)
    words = m.get("shared_words_count", 0)
    disc = len(m.get("discoveries", {}))
    couples = m.get("bonded_couples", 0)
    preg = m.get("pregnant_count", 0)
    lex = m.get("shared_lexicon", [])
    top_word = f'"{lex[0]["word"]}" = {lex[0]["referent"]}' if lex else "forming first words"

    days_x = [e["day"] for e in epochs] if len(epochs) >= 2 else [1, max(2, day)]
    live_y = [e["live_pop"] for e in epochs] if len(epochs) >= 2 else [58, live_pop]
    null_y = [e["null_pop"] for e in epochs] if len(epochs) >= 2 else [36, null_pop]

    fig = plt.figure(figsize=(12, 6.75), dpi=130, facecolor="#0b1120")
    ax = fig.add_axes([0.08, 0.24, 0.86, 0.54], facecolor="#0f172a")

    ax.plot(days_x, live_y, color="#34d399", linewidth=3.0, label=f"Free-Will Beings (Current: {live_pop})")
    ax.fill_between(days_x, live_y, alpha=0.14, color="#34d399")
    ax.plot(days_x, null_y, color="#94a3b8", linestyle="--", linewidth=2.2, label=f"Instinct-Only Control Twin (Current: {null_pop})")

    ax.set_xlabel("Planetary Day (Exact 24h / 365d Earth Calendar)", color="#cbd5e1", fontsize=11, labelpad=8)
    ax.set_ylabel("Real 1:1 Living Individuals", color="#cbd5e1", fontsize=11)
    ax.tick_params(colors="#94a3b8", labelsize=10)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("bottom", "left"):
        ax.spines[sp].set_color("#334155")
    ax.grid(color="#1e293b", linestyle="-", linewidth=0.8, alpha=0.8)
    leg = ax.legend(loc="upper right", frameon=True, facecolor="#1e293b", edgecolor="#334155", fontsize=11)
    for text in leg.get_texts():
        text.set_color("#f8fafc")

    fig.text(0.08, 0.90, f"THE NEW GENESIS · YEAR {yr}, DAY {day:,}", color="#38bdf8", fontsize=20, fontweight="bold")
    fig.text(
        0.08,
        0.84,
        "1:1 Earth · 8-Planet Solar System · 0% Human Intervention · Pure 1:1 Verifiable Reality",
        color="#94a3b8",
        fontsize=12,
    )

    stats_line = (
        f"Live 1:1: {live_pop}   |   Control Twin: {null_pop}   |   Couples: {couples} ({preg} expecting)   |   "
        f"Invented Words: {words} ({top_word})   |   Breakthroughs: {disc}"
    )
    fig.text(0.08, 0.08, stats_line, color="#e2e8f0", fontsize=11.5, fontweight="bold")
    fig.text(0.08, 0.03, "Live 24/7 Observatory & Open APA 7th Papers: agobac-ia.es  ·  @UniverseXXVLab", color="#64748b", fontsize=10)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_png


def compose_viral_science_thread(state: Dict[str, Any]) -> Tuple[str, str]:
    """Builds Tweet 1 (NO link, high-reach hook <= 265 chars) + Tweet 2 (live link reply)."""
    w = state.get("world", {})
    m = state.get("metrics", {})
    yr = w.get("year", 1)
    day = w.get("day", 1)
    live_pop = m.get("live_population", 0)
    null_pop = m.get("control_population", 0)
    words = m.get("shared_words_count", 0)
    disc = m.get("discoveries", {})
    couples = m.get("bonded_couples", 0)
    preg = m.get("pregnant_count", 0)
    compounds = m.get("emergent_compounds_count", 0)
    lex = m.get("shared_lexicon", [])
    top_w = f' ("{lex[0]["word"]}" = {lex[0]["referent"]})' if lex else ""

    if null_pop == 0:
        contrast = f"Instinct-only Control Twin: EXTINCT (0 left).\nFree-Will beings: {live_pop} alive, {couples} couples & {preg} expecting."
    else:
        contrast = f"Free-Will beings: {live_pop} alive ({couples} couples, {preg} expecting) vs. Instinct-only Control Twin: {null_pop}."

    extra = (
        f"Open compounds synthesized: {compounds}."
        if compounds > 0
        else ("They built their first permanent shelters!" if m.get("structures", {}).get("shelter", 0) > 0 else f"Unscripted breakthroughs: {len(disc)}.")
    )

    tweet1 = (
        f"Year {yr}, Day {day:,} · The New Genesis 🔬🌍\n\n"
        f"{contrast}\n"
        f"Invented words: {words}{top_w}. {extra}\n\n"
        f"0% human intervention. What happens next?"
    )
    if len(tweet1) > 272:
        tweet1 = tweet1[:269].rstrip() + "…"

    tweet2 = (
        "Watch the 1:1 Earth simulation live 24/7 & read our open-access APA 7th scientific monographs (updated directly from SQLite):\n"
        "https://agobac-ia.es"
    )
    return tweet1, tweet2


def publish_daily_x_thread(chronicles_dir: Path) -> bool:
    state_path = chronicles_dir / "latest_public_state.json"
    db_path = chronicles_dir / "universe_xxv.sqlite"
    if not state_path.exists():
        print("SKIPPED: latest_public_state.json not found.")
        return False

    state = json.loads(state_path.read_text(encoding="utf-8"))
    chart_path = render_daily_science_card(state, db_path, chronicles_dir / "daily_x_card.png")
    t1, t2 = compose_viral_science_thread(state)

    print("=== TWEET 1 (NO LINK + CHART) ===")
    print(t1)
    print(f"[len={len(t1)}] chart={chart_path} ({chart_path.stat().st_size} bytes)")
    print("=== TWEET 2 (REPLY WITH LINK) ===")
    print(t2)

    api_key = os.getenv("X_API_KEY", "").strip()
    api_secret = os.getenv("X_API_SECRET", "").strip()
    acc_token = os.getenv("X_ACCESS_TOKEN", "").strip()
    acc_secret = os.getenv("X_ACCESS_TOKEN_SECRET", "").strip()

    if not (api_key and api_secret and acc_token and acc_secret):
        print("DRY_RUN_OK: Add X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET in GitHub Secrets for PC-off cloud auto-posting.")
        return False

    import tweepy  # Installed in workflow

    auth = tweepy.OAuth1UserHandler(api_key, api_secret, acc_token, acc_secret)
    api_v1 = tweepy.API(auth)
    media = api_v1.media_upload(filename=str(chart_path))

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=acc_token,
        access_token_secret=acc_secret,
    )
    resp1 = client.create_tweet(text=t1, media_ids=[media.media_id])
    tid1 = resp1.data["id"]
    resp2 = client.create_tweet(text=t2, in_reply_to_tweet_id=tid1)
    print(f"PUBLISHED_CLOUD_X_OK: https://x.com/UniverseXXVLab/status/{tid1} (reply {resp2.data['id']})")
    return True


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent
    publish_daily_x_thread(root / "chronicles")
