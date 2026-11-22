"""Plain-Language Scientific Daily Digest Extractor for Universe XXV (@UniverseXXVLab).

Runs strictly ONCE PER HUMAN DAY (via 17:00 CET automation) to summarize the last
24 hours of autonomous evolution in clear, vivid, jargon-free English prose (<255 chars/post).
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict


def generate_daily_x_digest(db_path: Path) -> Dict[str, Any]:
    if not db_path.exists():
        return {"error": f"Database not found at {db_path}"}

    state_file = db_path.parent / "latest_public_state.json"
    live_state: Dict[str, Any] = {}
    if state_file.exists():
        try:
            live_state = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            live_state = {}

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        active_day = live_state.get("world", {}).get("day")
        if active_day is not None:
            latest = conn.execute(
                "SELECT * FROM epoch_telemetry WHERE day <= ? ORDER BY day DESC LIMIT 1",
                (active_day,),
            ).fetchone()
        else:
            latest = conn.execute(
                "SELECT * FROM epoch_telemetry ORDER BY created_at DESC, day DESC LIMIT 1"
            ).fetchone()
        if not latest:
            return {"error": "No epochs recorded yet."}

        high_events = conn.execute(
            "SELECT day, year, kind, summary FROM historical_events WHERE importance >= 3 ORDER BY id DESC LIMIT 6"
        ).fetchall()

        m = live_state.get("metrics", {})
        max_gen = m.get("max_generation", 1)
        lex = m.get("shared_lexicon", [])
        word_example = (
            f"«{lex[0]['word']}» for '{lex[0]['referent']}' ({lex[0]['consensus_pct']}% consensus)"
            if lex
            else "their first spoken syllables"
        )
        stress = latest["mean_stress"]
        mood_phrase = "living in calm balance" if stress < 35 else "facing food & space tension"

        alive_species = []
        if latest["sylphid_pop"] > 0:
            alive_species.append(f"{latest['sylphid_pop']} Sylphids")
        if latest["lithokin_pop"] > 0:
            alive_species.append(f"{latest['lithokin_pop']} Lithokin")
        if latest["vespera_pop"] > 0:
            alive_species.append(f"{latest['vespera_pop']} Vespera")
        species_str = ", ".join(alive_species) if alive_species else f"{latest['live_pop']} beings"

        post_1 = (
            f"UNIVERSE XXV · 24h Field Report (Year {latest['year']}, Day {latest['day']} · Gen {max_gen})\n\n"
            f"Population: {species_str} ({mood_phrase}).\n"
            f"Zero human contact. Zero awareness of being simulated."
        )[:265]

        hunts = m.get("hunts_count", 0)
        fishing = m.get("fishing_count", 0)
        gifts = latest["altruism_acts"] if "altruism_acts" in latest.keys() else m.get("altruism_acts", 0)
        clashes = latest["clashes"]

        post_2 = (
            f"1/ How their society is evolving:\n\n"
            f"• Survival: {hunts} wild hunts, {fishing} fish catches & woven plant-fiber cloaks\n"
            f"• Social life: {gifts} voluntary food gifts vs {clashes} resource fights\n"
            f"• Language: {word_example}"
        )[:265]

        top_ev = high_events[0]["summary"] if high_events else "Resting at night and foraging in clans."
        post_3 = (
            f"2/ Latest unscripted moment:\n\n"
            f"«{top_ev[:130]}»\n\n"
            f"Watch them eat, sleep, speak & explore live in 3D (EN/ES): https://agobac-ia.es"
        )[:265]

        return {
            "day": latest["day"],
            "year": latest["year"],
            "generation": max_gen,
            "archetype": latest["societal_archetype"],
            "thread_posts": [post_1, post_2, post_3],
        }
    finally:
        conn.close()


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent
    res = generate_daily_x_digest(root / "chronicles" / "universe_xxv.sqlite")
    print(json.dumps(res, indent=2, ensure_ascii=False))
