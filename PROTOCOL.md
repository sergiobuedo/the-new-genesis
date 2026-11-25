# Research Protocol & Pre-Registration: The New Genesis (Project Universe XXV)

**Protocol Version:** `v1.0-protocol` (Frozen Engine Baseline)  
**Principal Investigator:** Dr. Sergio Buedo Martínez (PhD in Social Education, Anthropologist & Computational Systems Researcher)  
**Public Repository (Open Code & Data):** https://github.com/sergiobuedo/the-new-genesis  
**Live 24/7 Read-Only Observatory:** https://agobac-ia.es  
**Target Registries:** Open Science Framework (OSF) / Zenodo Archival DOI  

---

## 1. Scientific Objective
To empirically measure whether autonomous, mortal cognitive agents—operating under **strict epistemic isolation** (zero pre-trained human lexical or meta-simulation hints) and **0% human intervention**—spontaneously develop shared symbolic language, cooperative provisioning, cumulative material culture, and higher demographic resilience than a synchronized **instinct-only Null-Control Twin** under identical 1:1 Earth geophysical conditions.

## 2. Pre-Registered Falsifiable Hypotheses
Across $N \ge 10$ independent random-seed paired replicates (`Live` vs. `Null-Control Twin`) evaluated under the frozen `v1.0-protocol` codebase:

- **H1 (Cultural Survival Advantage):** Experimental populations equipped with episodic memory, social learning, symbolic vocalization, and autonomous cognition (`Live`) will achieve significantly higher final population survival and lower extinction rates than instinct-only control populations (`Null`) exposed to identical seasons, predation, and disease (paired non-parametric test, $\alpha = 0.05$, one-tailed).
- **H2 (Spontaneous Lexical Emergence Under Epistemic Isolation):** Experimental populations (`Live`) will converge on shared phonetic lexicons (consensus $\ge 50\%$, zero English/Spanish cheat words permitted by `EpistemicGuard`) significantly above zero across independent seeds.
- **H3 (Non-Linear Counterfactual Technological Divergence):** Because the engine enforces no predetermined human technology tree, the discovery order of foundational survival breakthroughs (e.g., seed-planting/agriculture vs. controlled fire/hearth ignition) will exhibit measurable variance across independent seeds rather than reproducing a single deterministic human sequence.

## 3. Experimental Architecture & Controls
1. **Exact 1:1 Earth & 8-Planet Solar System Physics:** Mean radius $R = 6{,}371\text{ km}$, surface $510{,}072{,}000\text{ km}^2$, $23.4^\circ$ axial tilt, $24\text{h}/365\text{d}$ calendar, 9-month ($270\text{d}$) sexual gestation, 42 terrestrial/Pleistocene fauna species, 22 flora species, real `(lat, lon)` continental region mapping, and an Open-Ended Combinatorial Material Physics Engine (`backend/world/combinatorics.py`).
2. **Pure 1:1 Verifiable Reality (Zero Artificial Multipliers):** Every reported individual corresponds 1:1 to a complete simulated agent persisted in `SQLite-WAL` and hashed into an append-only `SHA-256` event chain. No extrapolated demographic multipliers are used.
3. **Epistemic Veil (`EpistemicGuard`):** Verified by automated test suite (`tests/test_scientific_purity.py`, 13/13 tests). Agents receive only first-person phenomenological sensory vectors and pure planetary `Year / Day` time (zero `BCE/CE` or human historical labels).
4. **Synchronized Null-Control Twin:** Every experimental run spawns an identical twin ecosystem (`enable_culture = False`) driven strictly by biological homeostatic instincts under the same random seed and climate.

## 4. Transparent Methodological Limitations (Peer-Review Disclosure)
To uphold strict academic integrity, the following limitations are explicitly declared:
- **Hybrid ABM + LLM Architecture:** Core biological homeostasis (metabolism, mammalian lactation, gestation, predation) is governed by explicit Python ecological equations, while higher-order social/cultural deliberation uses a local quantized LLM (`qwen2.5:1.5b`) when available. This experiment therefore studies **emergent cultural, linguistic, and ecological dynamics in hybrid multi-agent systems**, not biological abiogenesis from raw physics.
- **Pre-Trained Model Residual Priors:** Even with strict lexical scrubbing (`EpistemicGuard`), any pre-trained LLM retains latent statistical reasoning patterns learned from human corpora.
- **Live Observatory Continuity Cut:** In the continuous public Observatory (`seed=4201`), a biological bug-fix (`v23.4`, correcting leftover pre-365-day lactation/mentorship day thresholds) occurred at Day 2,692. Accordingly, formal inferential claims must rely on the **frozen `v1.0-protocol` Multi-Seed Benchmark (`benchmark_results.csv`)** rather than extrapolating from the single longitudinal pilot (`N = 1`).

## 5. Open Data & Reproducibility (FAIR Principles)
All multi-seed raw replicate outputs are exported as standard tabular CSV (`chronicles/benchmark_results.csv`) and summary JSON (`chronicles/benchmark_summary.json`) for independent verification in R, SPSS, or Python.
