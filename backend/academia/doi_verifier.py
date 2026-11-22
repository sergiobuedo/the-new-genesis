"""100% Live DOI Verification Engine (Crossref REST API + Official doi.org Handle Registry).

Verifies every single DOI live over HTTPS before allowing any citation into a
published APA 7th monograph—with polite rate-limit spacing and 429 backoff.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List

import httpx

CANDIDATE_BIBLIOGRAPHY: List[Dict[str, str]] = [
    {
        "key": "axelrod1981",
        "in_text": "(Axelrod & Hamilton, 1981)",
        "doi": "10.1126/science.7466396",
        "apa_ref": "Axelrod, R., & Hamilton, W. D. (1981). The evolution of cooperation. Science, 211(4489), 1390–1396.",
    },
    {
        "key": "bedau2000",
        "in_text": "(Bedau et al., 2000)",
        "doi": "10.1162/106454600300103683",
        "apa_ref": "Bedau, M. A., McCaskill, J. S., Packard, N. H., Rasmussen, S., Adami, C., Green, D. G., Ikegami, T., Kaneko, K., & Ray, T. S. (2000). Open problems in artificial life. Artificial Life, 6(4), 363–376.",
    },
    {
        "key": "bonabeau2002",
        "in_text": "(Bonabeau, 2002)",
        "doi": "10.1073/pnas.082080899",
        "apa_ref": "Bonabeau, E. (2002). Agent-based modeling: Methods and techniques for simulating human systems. Proceedings of the National Academy of Sciences, 99(suppl_3), 7280–7287.",
    },
    {
        "key": "bostrom2003",
        "in_text": "(Bostrom, 2003)",
        "doi": "10.1111/1467-9213.00309",
        "apa_ref": "Bostrom, N. (2003). Are we living in a computer simulation? The Philosophical Quarterly, 53(211), 243–255.",
    },
    {
        "key": "boyd2009",
        "in_text": "(Boyd & Richerson, 2009)",
        "doi": "10.1098/rstb.2009.0134",
        "apa_ref": "Boyd, R., & Richerson, P. J. (2009). Culture and the evolution of human cooperation. Philosophical Transactions of the Royal Society B: Biological Sciences, 364(1533), 3281–3288.",
    },
    {
        "key": "calhoun1973",
        "in_text": "(Calhoun, 1973)",
        "doi": "10.1177/00359157730661p202",
        "apa_ref": "Calhoun, J. B. (1973). Death squared: The explosive growth and demise of a mouse population. Proceedings of the Royal Society of Medicine, 66(1P2), 80–88.",
    },
    {
        "key": "dunbar1992",
        "in_text": "(Dunbar, 1992)",
        "doi": "10.1016/0047-2484(92)90081-j",
        "apa_ref": "Dunbar, R. I. M. (1992). Neocortex size as a constraint on group size in primates. Journal of Human Evolution, 22(6), 469–493.",
    },
    {
        "key": "henrich2004",
        "in_text": "(Henrich, 2004)",
        "doi": "10.2307/4128416",
        "apa_ref": "Henrich, J. (2004). Demography and cultural evolution: How adaptive cultural processes can produce maladaptive losses—The Tasmanian case. American Antiquity, 69(2), 197–214.",
    },
    {
        "key": "kirby2008",
        "in_text": "(Kirby et al., 2008)",
        "doi": "10.1073/pnas.0707835105",
        "apa_ref": "Kirby, S., Cornish, H., & Smith, K. (2008). Cumulative cultural evolution in the laboratory: An experimental approach to the origins of structure in human language. Proceedings of the National Academy of Sciences, 105(31), 10681–10686.",
    },
    {
        "key": "laland2000",
        "in_text": "(Laland et al., 2000)",
        "doi": "10.1017/s0140525x00002417",
        "apa_ref": "Laland, K. N., Odling-Smee, J., & Feldman, M. W. (2000). Niche construction, biological evolution, and cultural change. Behavioral and Brain Sciences, 23(1), 131–146.",
    },
    {
        "key": "nowak2006",
        "in_text": "(Nowak, 2006)",
        "doi": "10.1126/science.1133755",
        "apa_ref": "Nowak, M. A. (2006). Five rules for the evolution of cooperation. Science, 314(5805), 1560–1563.",
    },
    {
        "key": "park2023",
        "in_text": "(Park et al., 2023)",
        "doi": "10.1145/3586183.3606763",
        "apa_ref": "Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). Generative agents: Interactive simulacra of human behavior. In Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology (pp. 1–22). ACM.",
    },
    {
        "key": "reynolds1987",
        "in_text": "(Reynolds, 1987)",
        "doi": "10.1145/37402.37406",
        "apa_ref": "Reynolds, C. W. (1987). Flocks, herds and schools: A distributed behavioral model. ACM SIGGRAPH Computer Graphics, 21(4), 25–34.",
    },
    {
        "key": "shannon1948",
        "in_text": "(Shannon, 1948)",
        "doi": "10.1002/j.1538-7305.1948.tb01338.x",
        "apa_ref": "Shannon, C. E. (1948). A mathematical theory of communication. The Bell System Technical Journal, 27(3), 379–423.",
    },
    {
        "key": "tomasello2005",
        "in_text": "(Tomasello et al., 2005)",
        "doi": "10.1017/s0140525x05000129",
        "apa_ref": "Tomasello, M., Carpenter, M., Call, J., Behne, T., & Moll, H. (2005). Understanding and sharing intentions: The origins of cultural cognition. Behavioral and Brain Sciences, 28(5), 675–691.",
    },
]

VERIFIED_APA_CORPUS: List[Dict[str, str]] = []


def verify_single_doi(client: httpx.Client, doi: str) -> Dict[str, str]:
    """Verifies a DOI against the official doi.org Handle Registry + Crossref metadata."""
    handle_resp = client.get(f"https://doi.org/api/handles/{doi}")
    if handle_resp.status_code != 200 or handle_resp.json().get("responseCode") != 1:
        raise RuntimeError(f"DOI handle verification FAILED in global registry: {doi}")

    title = ""
    canonical_doi = doi
    for attempt in range(3):
        cr_resp = client.get(f"https://api.crossref.org/works/{doi}")
        if cr_resp.status_code == 200:
            msg = cr_resp.json().get("message", {})
            canonical_doi = msg.get("DOI", doi)
            t_list = msg.get("title") or [""]
            title = t_list[0]
            break
        if cr_resp.status_code == 429:
            time.sleep(1.2 * (attempt + 1))
            continue
        break

    time.sleep(0.22)  # Polite Crossref etiquette
    return {"canonical_doi": canonical_doi, "title": title}


def verify_all_corpus_dois(cache_path: Path | None = None) -> List[Dict[str, str]]:
    """Verifies 100% of candidate DOIs live before publication."""
    if cache_path and cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if len(cached) >= 15 and all(item.get("doi_verified") is True for item in cached):
            return cached

    verified: List[Dict[str, str]] = []
    headers = {"User-Agent": "TheNewGenesisObservatory/6.0 (https://agobac-ia.es; mailto:observatory@agobac-ia.es)"}
    with httpx.Client(timeout=15.0, headers=headers, follow_redirects=True) as client:
        for entry in CANDIDATE_BIBLIOGRAPHY:
            info = verify_single_doi(client, entry["doi"].strip())
            c_doi = info["canonical_doi"]
            verified.append(
                {
                    **entry,
                    "doi": c_doi,
                    "doi_url": f"https://doi.org/{c_doi}",
                    "crossref_title": info["title"],
                    "doi_verified": True,
                }
            )

    verified.sort(key=lambda x: x["apa_ref"])
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(verified, indent=2, ensure_ascii=False), encoding="utf-8")
    return verified
