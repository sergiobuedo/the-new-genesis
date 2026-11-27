# Research protocol and pre-registration: The New Genesis (Project Universe XXV)

**Protocol version:** `v3.0-protocol` (zero-refugia, authentic human ontogeny, and unbiased causal control)  
**Principal investigator:** Dr. Sergio Buedo Martínez  
**Repository and open data:** https://github.com/sergiobuedo/the-new-genesis  
**Public observatory:** https://agobac-ia.es  

---

## 1. Aim of the study
This project tests whether autonomous, mortal software agents operating without human language cues or external intervention develop shared vocal symbols, cooperative habits, and cumulative material practices that improve survival compared with an instinct-only control population living under the same environment.

## 2. Pre-registered hypotheses
All inferential tests are evaluated across $N \ge 10$ independent random-seed paired runs (`Live` vs. `Null`) using the frozen `v2.0-protocol` codebase:

- **H1 (Survival under cultural transmission):** Populations with episodic memory, phonetic communication, social learning, and autonomous deliberation (`Live`) will retain more living individuals and suffer fewer extinctions than matched instinct-only controls (`Null`) across seasonal stress ($\alpha = 0.05$, one-tailed paired test).
- **H2 (Spontaneous lexical convergence):** Under lexical isolation (no human words allowed on the public acoustic channel), `Live` populations will converge on shared phonetic terms above zero across independent seeds.
- **H3 (Non-linear discovery order):** Because the simulation contains no fixed technology tree, the sequence in which populations discover core survival practices (for example, planting seeds versus controlling fire) will vary across independent runs rather than following a single human historical order.

## 3. Experimental setup and controls
1. **Planetary and biological parameters:** The environment uses Earth's physical dimensions ($R = 6{,}371\text{ km}$, surface area $510{,}072{,}000\text{ km}^2$, $23.4^\circ$ axial tilt, 24-hour days, 365-day years, and 270-day gestation) within an eight-planet solar system model (lunar tides and long-term orbital variation). Agents occupy real `(lat, lon)` regions alongside 42 fauna species, 22 flora species, and a continuous material-combination model (`backend/world/combinatorics.py`).
2. **One-to-one population accounting:** Every individual reported in the interface or in the dataset corresponds directly to one simulated agent recorded in `SQLite-WAL` and hashed in `event_chain.jsonl` (`SHA-256`). No population multipliers are applied.
3. **Epistemic isolation:** Automated tests (`tests/test_scientific_purity.py`, 13/13 passing) verify that agent prompts exclude simulation terms, human historical labels (`BCE`/`CE`), and modern material names. Time is tracked simply as planetary year and day.
4. **Equalized causal control (`v2.0-protocol`):** Both `Live` and `Null` populations share the exact same physical and biological survival rules: maternal nursing, parental provisioning, group huddling for warmth, instinctive use of healing plants, shelter-seeking in bad weather, and hunting when hungry. The only variable switched off in `Null` is symbolic cognition (LLM deliberation, phonetic language, cross-generational teaching, barter, and intentional material experimentation).

## 4. Methodological limitations
- **Hybrid architecture (ABM + LLM):** Core physiology and ecology are governed by explicit Python rules, whereas higher-level social and cultural decisions rely on a local language model (`qwen2.5:1.5b`). The study therefore evaluates emergent dynamics in hybrid multi-agent systems, not biological evolution from scratch.
- **Residual model priors:** Even when lexical filters strip human terminology from prompts and speech, a pre-trained language model retains general reasoning patterns from its training corpus.
- **Longitudinal observatory cut:** The continuous public run (`seed = 4201`) received a biological bug fix (`v23.4`) at Day 2,692 to correct leftover day thresholds for infant care and mentorship. Formal statistical claims therefore rely on the frozen multi-seed benchmark (`chronicles/benchmark_results.csv`) rather than on the single longitudinal run.

## 5. Data availability
Raw replicate outputs are published in open tabular format (`chronicles/benchmark_results.csv` and `chronicles/benchmark_summary.json`) so any researcher can replicate the statistical analysis in R, SPSS, or Python.
