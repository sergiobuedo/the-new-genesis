"""Reproducible Multi-Seed Statistical Benchmark (N Paired Replicates: Live vs. Null).

Executes N independent random seeds under identical frozen physics & climate,
comparing the Cultural/Free-Will population (`Live`) against its synchronized
Instinct-Only Control Twin (`Null`). Computes exact inferential statistics
(Mean, SD, Paired Cohen's d, Exact Paired Permutation p-value, Extinction Rate,
and Technological Divergence Rate) and exports FAIR CSV + JSON datasets.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import statistics
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.mirofish_lab.observer import MiroFishObservatory


def _exact_paired_permutation_p(diffs: List[float]) -> float:
    """Exact two-sided paired sign-flip permutation p-value (or Monte Carlo if N > 14)."""
    n = len(diffs)
    if n == 0:
        return 1.0
    obs = abs(sum(diffs) / n)
    if obs == 0.0:
        return 1.0
    if n <= 14:
        extreme = 0
        total = 1 << n
        for signs in itertools.product((-1.0, 1.0), repeat=n):
            val = abs(sum(s * d for s, d in zip(signs, diffs)) / n)
            if val >= obs - 1e-12:
                extreme += 1
        return round(extreme / total, 6)
    # Deterministic fallback for larger N
    import random
    rng = random.Random(42)
    trials = 20000
    extreme = 0
    for _ in range(trials):
        val = abs(sum((1.0 if rng.random() < 0.5 else -1.0) * d for d in diffs) / n)
        if val >= obs - 1e-12:
            extreme += 1
    return round((extreme + 1) / (trials + 1), 6)


def _cohens_d_paired(diffs: List[float]) -> float:
    if len(diffs) < 2:
        return 0.0
    mean_d = statistics.mean(diffs)
    sd_d = statistics.stdev(diffs)
    if sd_d == 0.0:
        return 0.0
    return round(mean_d / sd_d, 4)


def run_single_replicate(seed: int, days: int, founders_per_lineage: int = 7) -> Dict[str, Any]:
    """Runs one isolated paired replicate (Live vs. Null) for `days` planetary days."""
    ticks = days * 24
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        obs = MiroFishObservatory(
            ledger_dir=Path(td),
            seed=seed,
            founders_per_lineage=founders_per_lineage,
            enable_metapopulation=False,
            allow_refugia=False,
        )
        # v3.0-protocol: ZERO artificial refugia or re-biogenesis in BOTH Live and Null (extinction is 100% real!)
        obs.live.allow_refugia = False
        obs.control.allow_refugia = False
        try:
            for _ in range(ticks):
                obs.live.step_tick()
                obs.control.step_tick()
            m = obs.compute_scientific_metrics()
            disc = m.get("discoveries", {})
            ag_day = disc.get("first_agriculture")
            fire_day = disc.get("struct_hearth")
            ag_before_fire = bool(ag_day is not None and (fire_day is None or ag_day < fire_day))
            return {
                "seed": seed,
                "days_simulated": days,
                "founders_per_lineage": founders_per_lineage,
                "initial_founders_total": founders_per_lineage * 3,
                "live_final_pop": int(m["live_population"]),
                "null_final_pop": int(m["control_population"]),
                "pop_diff_live_minus_null": int(m["live_population"]) - int(m["control_population"]),
                "live_extinct": int(m["live_population"] == 0),
                "null_extinct": int(m["control_population"] == 0),
                "bonded_couples": int(m.get("bonded_couples", 0)),
                "pregnant_count": int(m.get("pregnant_count", 0)),
                "shared_words": int(m.get("shared_words_count", 0)),
                "discoveries_count": len(disc),
                "emergent_compounds": int(m.get("emergent_compounds_count", 0)),
                "mean_stress": round(float(m.get("mean_stress", 0.0)), 2),
                "gini_index": round(float(m.get("gini_index", 0.0)), 4),
                "social_clustering": round(float(m.get("social_clustering", 0.0)), 4),
                "crowding_sink_index": round(float(m.get("crowding_sink_index", 0.0)), 4),
                "altruism_acts": int(m.get("altruism_acts", 0)),
                "inter_species_peace": int(m.get("inter_species_peace", 0)),
                "conflict_acts": int(m.get("conflict_acts", 0)),
                "ag_day": ag_day if ag_day is not None else "",
                "fire_day": fire_day if fire_day is not None else "",
                "ag_before_fire": int(ag_before_fire),
            }
        finally:
            obs.warehouse.close()


def run_multi_seed_benchmark(
    num_seeds: int = 10,
    days: int = 120,
    base_seed: int = 1001,
    output_dir: Path = Path("chronicles"),
    model_tag: str = "abm_v3_baseline",
    founders_per_lineage: int = 7,
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    for i in range(num_seeds):
        sd = base_seed + i
        row = run_single_replicate(seed=sd, days=days, founders_per_lineage=founders_per_lineage)
        row["model_tag"] = model_tag
        rows.append(row)
        print(
            f"[Seed {sd}] Day {days} (Founders={founders_per_lineage*3}): Live={row['live_final_pop']} vs Null={row['null_final_pop']} "
            f"| Words={row['shared_words']} | Disc={row['discoveries_count']} | AgBeforeFire={row['ag_before_fire']}"
        )

    csv_path = output_dir / "benchmark_results.csv"
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    live_pops = [float(r["live_final_pop"]) for r in rows]
    null_pops = [float(r["null_final_pop"]) for r in rows]
    diffs = [l - n for l, n in zip(live_pops, null_pops)]
    words_list = [float(r["shared_words"]) for r in rows]
    disc_list = [float(r["discoveries_count"]) for r in rows]

    summary = {
        "protocol_version": "v4.0-protocol",
        "model_tag": model_tag,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_replicates": num_seeds,
        "days_per_replicate": days,
        "founders_per_lineage": founders_per_lineage,
        "initial_founders_total": founders_per_lineage * 3,
        "base_seed": base_seed,
        "live_pop_mean": round(statistics.mean(live_pops), 2),
        "live_pop_sd": round(statistics.stdev(live_pops), 2) if num_seeds >= 2 else 0.0,
        "null_pop_mean": round(statistics.mean(null_pops), 2),
        "null_pop_sd": round(statistics.stdev(null_pops), 2) if num_seeds >= 2 else 0.0,
        "live_extinction_pct": round(100.0 * sum(r["live_extinct"] for r in rows) / num_seeds, 1),
        "null_extinction_pct": round(100.0 * sum(r["null_extinct"] for r in rows) / num_seeds, 1),
        "paired_diff_mean": round(statistics.mean(diffs), 2),
        "paired_cohens_d": _cohens_d_paired(diffs),
        "paired_permutation_p": _exact_paired_permutation_p(diffs),
        "shared_words_mean": round(statistics.mean(words_list), 2),
        "shared_words_sd": round(statistics.stdev(words_list), 2) if num_seeds >= 2 else 0.0,
        "discoveries_mean": round(statistics.mean(disc_list), 2),
        "discoveries_sd": round(statistics.stdev(disc_list), 2) if num_seeds >= 2 else 0.0,
        "gini_mean": round(statistics.mean(float(r["gini_index"]) for r in rows), 4),
        "clustering_mean": round(statistics.mean(float(r["social_clustering"]) for r in rows), 4),
        "altruism_mean": round(statistics.mean(float(r["altruism_acts"]) for r in rows), 2),
        "conflict_mean": round(statistics.mean(float(r["conflict_acts"]) for r in rows), 2),
        "ag_before_fire_pct": round(100.0 * sum(r["ag_before_fire"] for r in rows) / num_seeds, 1),
    }

    json_path = output_dir / "benchmark_summary.json"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("BENCHMARK_SUMMARY:", json.dumps(summary))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Multi-Seed Paired Statistical Benchmark (Live vs. Null).")
    parser.add_argument("--seeds", type=int, default=10, help="Number of independent random seeds (default: 10)")
    parser.add_argument("--days", type=int, default=120, help="Planetary days per replicate (default: 120)")
    parser.add_argument("--base-seed", type=int, default=1001, help="Starting seed integer (default: 1001)")
    parser.add_argument("--founders-per-lineage", type=int, default=7, help="Initial adult founders per lineage (3 lineages total; default: 7 = 21 total, 15 = 45 Dunbar band)")
    parser.add_argument("--model-tag", type=str, default="abm_v3_baseline", help="Model/ablation arm identifier (e.g. v3_dunbar45, qwen2.5:1.5b, llama3.2:1b)")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent.parent
    run_multi_seed_benchmark(
        num_seeds=args.seeds,
        days=args.days,
        base_seed=args.base_seed,
        output_dir=root / "chronicles",
        model_tag=args.model_tag,
        founders_per_lineage=args.founders_per_lineage,
    )
