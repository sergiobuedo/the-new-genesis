"""Longitudinal SQLite-WAL Scientific Data Warehouse for Universe XXV (v3.0).

Stores persistent time-series epochs, bilingual (EN + ES) day-by-day executive
summaries, emergent societal archetype classifications, and historical events.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List


class LongitudinalWarehouse:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS epoch_telemetry (
                day INTEGER PRIMARY KEY,
                year INTEGER,
                season TEXT,
                temp_c REAL,
                live_pop INTEGER,
                null_pop INTEGER,
                sylphid_pop INTEGER,
                lithokin_pop INTEGER,
                vespera_pop INTEGER,
                societal_archetype TEXT,
                mean_stress REAL,
                crowding_sink_index REAL,
                gini_index REAL,
                cultural_entropy REAL,
                clustering REAL,
                intra_gifts INTEGER,
                inter_species_gifts INTEGER,
                clashes INTEGER,
                pidgin_words INTEGER,
                philosophical_acts INTEGER,
                sha256_head TEXT,
                recorded_at REAL
            );

            CREATE TABLE IF NOT EXISTS daily_summaries (
                day INTEGER PRIMARY KEY,
                year INTEGER,
                season TEXT,
                archetype_en TEXT,
                archetype_es TEXT,
                summary_en TEXT,
                summary_es TEXT,
                live_pop INTEGER,
                null_pop INTEGER,
                milestones_json TEXT,
                recorded_at REAL
            );

            CREATE TABLE IF NOT EXISTS historical_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tick INTEGER,
                day INTEGER,
                year INTEGER,
                season TEXT,
                kind TEXT,
                summary TEXT,
                actors_json TEXT,
                x REAL,
                y REAL,
                importance INTEGER
            );
            """
        )
        self._conn.commit()

    def record_epoch(self, m: Dict[str, Any]) -> None:
        sp = m.get("species_counts", {})
        self._conn.execute(
            """
            INSERT OR REPLACE INTO epoch_telemetry VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                m["day"],
                m["year"],
                m["season"],
                m["ambient_temp_c"],
                m["live_population"],
                m["control_population"],
                sp.get("Sylphid", 0),
                sp.get("Lithokin", 0),
                sp.get("Vespera", 0),
                m.get("archetype_en", "Pre-Social Awakening"),
                m["psychology"]["mean_stress"],
                m["psychology"]["calhoun_sink_index"],
                m["gini_index"],
                m["cultural_entropy_bits"],
                m["social_clustering"],
                m["altruism_acts"],
                m["inter_species_peace"],
                m["conflict_acts"],
                m["pidgin_words_count"],
                m["philosophical_count"],
                m["ledger_head_hash"],
                time.time(),
            ),
        )
        self._conn.commit()

    def record_daily_summary(self, entry: Dict[str, Any]) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO daily_summaries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry["day"],
                entry["year"],
                entry["season"],
                entry["archetype_en"],
                entry["archetype_es"],
                entry["summary_en"],
                entry["summary_es"],
                entry["live_pop"],
                entry["null_pop"],
                json.dumps(entry.get("milestones", []), ensure_ascii=False),
                time.time(),
            ),
        )
        self._conn.commit()

    def recent_daily_summaries(self, limit: int = 35) -> List[Dict[str, Any]]:
        cur = self._conn.execute(
            "SELECT * FROM daily_summaries ORDER BY day DESC LIMIT ?", (limit,)
        )
        rows = []
        for r in cur.fetchall():
            rows.append(
                {
                    "day": r["day"],
                    "year": r["year"],
                    "season": r["season"],
                    "archetype_en": r["archetype_en"],
                    "archetype_es": r["archetype_es"],
                    "summary_en": r["summary_en"],
                    "summary_es": r["summary_es"],
                    "live_pop": r["live_pop"],
                    "null_pop": r["null_pop"],
                    "milestones": json.loads(r["milestones_json"] or "[]"),
                }
            )
        return rows

    def record_event(self, ev: Dict[str, Any]) -> None:
        self._conn.execute(
            """
            INSERT INTO historical_events (tick, day, year, season, kind, summary, actors_json, x, y, importance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ev["tick"],
                ev["day"],
                ev["year"],
                ev["season"],
                ev["kind"],
                ev["summary"],
                json.dumps(ev["actors"]),
                ev["x"],
                ev["y"],
                ev["importance"],
            ),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
