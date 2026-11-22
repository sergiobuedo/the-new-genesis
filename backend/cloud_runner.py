"""24/7 Autonomous Cloud Simulation Runner for TheNewGenesis · God's Window.

Executes continuous multi-species simulation bursts on cloud Linux servers (with
local Ollama `qwen2.5:1.5b` inside the runner), persisting `latest_public_state.json`,
`world_init.json`, and `universe_xxv.sqlite` so https://agobac-ia.es runs 24/7
even when the Principal Investigator's personal workstation is powered off.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from backend.academia.paper_generator import compile_weekly_apa_paper
from backend.mirofish_lab.observer import MiroFishObservatory

ROOT_DIR = Path(__file__).resolve().parent.parent
CHRONICLES_DIR = ROOT_DIR / "chronicles"
PAPERS_DIR = CHRONICLES_DIR / "papers"


def push_live_telemetry_snapshot(commit_msg: str) -> None:
    """Commits and pushes fresh read-only telemetry to `live-telemetry` branch if in CI."""
    if os.getenv("GITHUB_ACTIONS") != "true":
        return
    subprocess.run(
        [
            "git",
            "add",
            "-f",
            "chronicles/latest_public_state.json",
            "chronicles/world_init.json",
            "chronicles/universe_xxv.sqlite",
            "chronicles/event_chain.jsonl",
            "chronicles/papers/",
        ],
        cwd=str(ROOT_DIR),
        check=False,
    )
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(ROOT_DIR))
    if diff.returncode != 0:
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(ROOT_DIR), check=False)
        subprocess.run(
            ["git", "push", "origin", "HEAD:live-telemetry", "--force"],
            cwd=str(ROOT_DIR),
            check=False,
        )


async def run_cloud_burst(duration_seconds: int = 660, speed: int = 5) -> None:
    CHRONICLES_DIR.mkdir(parents=True, exist_ok=True)
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    obs = MiroFishObservatory(ledger_dir=CHRONICLES_DIR, seed=4201, founders_per_lineage=7)
    obs.speed_multiplier = speed
    await obs.cortex.probe()

    (CHRONICLES_DIR / "world_init.json").write_text(
        json.dumps(obs.world_init_payload(), ensure_ascii=False), encoding="utf-8"
    )

    start_ts = time.time()
    last_push_ts = 0.0

    try:
        while (time.time() - start_ts) < duration_seconds:
            for _ in range(speed):
                await obs.step_once()

            now = time.time()
            if (now - last_push_ts) >= 35.0:
                last_push_ts = now
                snap = obs.snapshot_for_ui()
                (CHRONICLES_DIR / "latest_public_state.json").write_text(
                    json.dumps(snap, ensure_ascii=False), encoding="utf-8"
                )
                push_live_telemetry_snapshot(
                    f"telemetry: Y{snap['world']['year']} D{snap['world']['day']} (Pop {snap['metrics']['live_population']})"
                )

            await asyncio.sleep(0.18)

        # Weekly Sunday APA 7th Monograph check
        now_utc = datetime.now(timezone.utc)
        manifest_path = PAPERS_DIR / "papers_manifest.json"
        papers = (
            json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest_path.exists()
            else []
        )
        expected_issues = max(1, (obs.live.world.day // 280) + 1)
        if now_utc.weekday() == 6 and len(papers) < expected_issues:
            compile_weekly_apa_paper(
                CHRONICLES_DIR / "universe_xxv.sqlite", PAPERS_DIR, len(papers) + 1
            )

        snap = obs.snapshot_for_ui()
        (CHRONICLES_DIR / "latest_public_state.json").write_text(
            json.dumps(snap, ensure_ascii=False), encoding="utf-8"
        )
        push_live_telemetry_snapshot(
            f"telemetry(sync): Y{snap['world']['year']} D{snap['world']['day']}"
        )
    finally:
        await obs.cortex.close()
        obs.warehouse.close()


if __name__ == "__main__":
    dur = int(os.getenv("CLOUD_BURST_SECONDS", "660"))
    spd = int(os.getenv("COSMOS_SPEED", "5"))
    asyncio.run(run_cloud_burst(duration_seconds=dur, speed=spd))
