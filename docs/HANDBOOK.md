# HISN — Project Handbook (Team Sankalp)
*Single source of truth. Last updated 30 Oct 2026.*

## 1. Competition facts

| Item | Detail |
|---|---|
| Event | ITU AI for Good Lab Hackathon, UAE edition 2026 |
| Team | **Team Sankalp**: Eswar Panchakarla (leader, engineering), P. Prudhvi Krishna (knowledge base, policy, report), Bengaluru. Max 4 members; all must be named in the report |
| Registered domains | Telecom + healthcare + public services (confirmed by Vishnu as "what we look for") |
| Submission | **Submit 9 Nov** (deadline 10 Nov 2026) to **aiforgoodlab@itu.int**, with the GitHub link |
| Shortlist | 18 Nov (about 15 teams) |
| Final | 8 Dec at GITEX Dubai; awards 10 Dec |
| Prizes | CHF 1,500 / 1,000 / 600, plus a Judges' prize of CHF 1,000 |
| Required | Working prototype + report (**≤ 5 pages**, official template) + **demo video (≤ 5–7 min)**, even for round 1: show that it works, why it's agentic, and the problem |
| Mentoring | Saturdays 10:00 CET = **14:30 IST**; sessions remaining: **31 Oct, 7 Nov** |
| Sandbox / credits | Only after submitting an "initial design" by email; ITU evaluates eligibility first. Initial-design email: **sent 29 Oct (confirm)**; tell Vishnu on WhatsApp |
| Repo | github.com/Eswarpnbs/HISN (**private until 9 Nov**) |
| Hosted report | hisn-report.netlify.app (static, synthetic data; redeployed 29 Oct with 13/14) |

## 2. What the judges reward (from sessions and winning repos)

1. **Gap analysis is the most valued part**, more than accuracy.
2. The **policy node (P) must govern every pipeline step**: map **all 9 Y.3172 nodes**.
3. **Samaam's technical report is the model** (Vishnu showed it twice): github.com/aboalrejalai/samaam/blob/main/submission/TECHNICAL-REPORT.md
4. **"Evidence or silence":** gaps earn bonus points; never invent.
5. Gaps must be **domain-level, not country-specific recommendations.**
6. Map **only the readiness dimensions you can demonstrate** with evidence.
7. Cover **"controversy"**: where the solution itself causes a problem.
8. **Pre-agreed rules**, not ad hoc corrective actions.
9. Judges may **inject events live** during the demo.
10. Chang asked for **policy-ON vs OFF** and **RAG vs no-RAG** comparisons (done).

**Red lines (each could eliminate us):** any unverified law or URL (e.g. the claimed "UAE/Dubai AI Act" is contested, so **don't cite it**); confidential data; country-level recommendations; a pitch deck instead of a working prototype; more than 5 pages; real phishing text; broken links (Samaam's report had `file:///` links); imitating official government websites or emblems; claiming "first in the world".

## 3. Competition analysis (all repos read)

| Team | Result | What won it |
|---|---|---|
| **SANAD** (Saudi) | 1st | Rigour: 15 records, 90% precision with a Wilson CI, every number traceable to a command, schema offered to ITU |
| **AI Guardian** | 2nd | 49 frameworks, 8-point provenance, SHA-256 chain, a "devil's advocate" agent. Weaknesses: broken `file:///` links, wrong dimension names |
| **Samaam** | 3rd | 403 gateway, 6 verdicts × 4 actions, FHIR/DICOM connectors, offline, one-command run, only 3 readiness dimensions (with evidence), radiologist review changed the design |
| **Netaxis** (Build-a-thon 5.0, 1st) | 1st | Agents propose, fixed code decides; time-gated role-scoped events; stale/forged-input tests; rollback; 4 non-AI baselines; honest about no throughput gain; cited Y.3181 |

**Now the minimum, not a differentiator:** LLM proposes / code decides; hash-chained log; evidence-or-gap.
**HISN's differentiators:** a measured gap engine; a **regulatory wind tunnel** (test-driven regulation, now with clinical and sunset invariants); pre-registered held-out evaluation; four-way baselines; three-country verified packs; a real SMPP server with accountable receipts; clinical priority via FHIR; real operator network data.

## 4. ITU reference code (CrashingGuru/ITUAIReadiness/simulation)

- An "AI Readiness Simulation Game" by Vishnu Ram. Collections: `kb_main`, `kb_framework`, `kb_decisions`, `kb_usecase`.
- Agents: Dataset (D1, D2), OpenSource (D2, D5), Sandbox (D10, D11), Research (D3, D4, D9), Deployment (D5, D12, D13), Standards (D6, D7, D8), UseCase (all).
- **Official Y.3172 → dimension mapping (use verbatim):** SRC→D1, D4, D13; C→D1, D3, D13; PP→D1, D2, D3; M→D2, D3, D5, D9; **P→D7, D8, D10**; D→D5, D6, D12; SINK→D5, D6, D12, D13; MLFO→D5, D7, D8; Sandbox→D10, D11.
- **Causal graph:** D10→D7 (0.5), D13→D5 (0.5), D7→D12 (0.5). Most influential: D1, D7, D13. **Our export:** a D10 impulse reaches D7 0.50, D8 0.375, D5 0.13, D12 0.125, D6 0.013 (structure only).
- **No UAE documents** in ITU's inputs, so our corpus is a genuine contribution. ITU's Telecom RAG agent maps its refusal guardrail to the UAE AI Charter. ITU's sandbox datasets include TeleQnA, Turkcell radio-link failure and packet-flow data; **no SMS scam data** (we published one).
- Our human-approved fixes go into ITU's `kb_decisions` via `kb.add_decision()`.

**Official metric IDs used:** D3 (d3_m01, d3_m07); D7 (d7_m01, m03, m04, m08); **D10** (d10_m01 Policy Sandbox, m02 Policy Evaluation, m03 Policy Extrapolation, m06 Safety Policies, m07 Explainability, m09 Audit, m10 Data Sovereignty); D11 (d11_m07, m08 Regional Language Support, m11); D13 (d13_m07, m08, m09).

## 5. UAE policy landscape (verified)

- **Regulatory Intelligence Office** (Cabinet, Apr 2025): AI-assisted legislation; "living, responsive regulations"; links laws with rulings, procedures and services; aims to speed lawmaking up to 70%. Davos (Jan 2026) white paper: **law as a continuously updated dataset.**
- **Federal AI & Data Authority** (14 Jun 2026): merges the AI Office, TDRA's digital-government arm and the Emirates Data Office; reports to the Cabinet. TDRA remains the telecom regulator.
- **HISN's hook:** *a domain-scale prototype of pre-issuance testing for living, AI-assisted law.*

## 6. The concept

**HISN (حصن, "fortress")** governs the autonomous telecom AI that decides whether essential health and government messages reach citizens: the network AI (carries the message) and the SMS filter AI (lets it through).

- **One sentence:** *"HISN governs the AI that decides which health and government messages reach citizens, and gives every draft rule a test suite: it checks the draft against existing law, re-runs real crisis scenarios, and shows what the rule fixes and what it breaks, before it takes effect."*
- **Opening line (report and video):** *"A patient's critical test result was blocked by an AI spam filter. The hospital never knew. Today, no law says who's responsible."*
- **Sharp insight:** emergency alerts have a protected lane (cell broadcast); your critical lab result doesn't. It travels as ordinary SMS through the same AI filters as scams.
- **Bigger frame:** governments are letting AI make decisions inside critical public infrastructure at national scale. HISN shows how to govern that, starting with the AI that decides whether your hospital can reach you.
- **Positioning:** operators already run network AI on every SMS (e.g. Airtel since Sept 2024, with acknowledged false positives and privacy concerns). HISN doesn't replace it; it governs it. It plugs into existing standards: **SMPP 3.4** (operators), **HL7 FHIR** (hospitals), **Y.3172 + Readiness metrics** (ITU).
- **Scope:** one slice of governance only: essential health messages (lead example) and government service messages. Not "all of governance".
- **Controversies we address:** (1) over-blocking real hospital alerts → escalate, never silently drop, tier-based second review; (2) AI scanning of health SMS lacks a legal basis (G3) → metadata-first, tiers declared by the sender, never read from content; (3) emergency powers that never end → sunset test (I8).

## 7. Knowledge base (13 records, 32 verbatim clauses, SHA-256 pinned)

| Record | Instrument | Status |
|---|---|---|
| UAE-FL-2-2019 | Federal Law No. 2 of 2019 (ICT in Health Fields) | official |
| UAE-PDPL-2021 | Federal Decree-Law 45/2021 (PDPL) | official |
| UAE-TDRA-UEC-2022 | TDRA Unsolicited Electronic Communications Policy v1.1 | official |
| UAE-DOH-AI-2018 | DoH Abu Dhabi AI policy | official |
| UAE-DOH-RAI-2025 | DoH Responsible AI Standard | official |
| UAE-AI-CHARTER-2024 | UAE AI Charter | official_archived (soft law) |
| UAE-AI-STRATEGY-2031 | National AI Strategy 2031 | official_archived (soft law) |
| IN-DPDP-2023 | Digital Personal Data Protection Act 2023 | official |
| IN-TELECOM-ACT-2023 | Telecommunications Act 2023 | official, phased commencement (verify s.20, s.28) |
| IN-TRAI-TCCCPR-CONS | TRAI TCCCPR, consolidated text (gazetted prevails) | official reference |
| SG-SRF-2024 | MAS–IMDA Guidelines on Shared Responsibility Framework | official |
| SG-PDPA-2012 | PDPA 2012 (SSO current version, 29 Oct 2026) | official (confirm the URL) |
| SA-CST-SPAM-2018 | CST Regulation for Reduction of SPAM (2018 draft translation) | **historical, background only** |

**Key clauses:** UAE Art. 13 (localisation; exception by Health Authority resolution), Art. 16 (5 consent exceptions), Art. 1 (circulation), Art. 4, Art. 24; TDRA §1.10 (spam = marketing), §6.1, §11.1–11.2, §8.5.3, §13 (government exemption); PDPL Art. 2(2); Charter P2/P5/P6/P7. India: DPDP s.4(1), s.7(f)–(h), s.16, s.17(2)(a); Telecom Act s.20(1), s.28(1)–(2); TRAI Header Register, reg. 33(1). Singapore: SRF definition (impersonation incl. government), 5.2.1–5.2.3, footnote 9, 6.4; PDPA s.26(1)–(2), emergency vital-interests paragraph (verify the schedule number).
**Tools:** ITU reference ingest pipeline (unmodified); `kb/register.py`, `verify.py`, `find_clause.py`, `ingest_uae.py` (multi-country), `eval_retrieval.py`.
**Lesson:** never run `ingest_uae.py` during agent or baseline runs (it resets the knowledge base).

## 8. Gap register

| Gap | Statement | Evidence | UAE / IN / SG |
|---|---|---|---|
| **G1** | Telecom filtering duties cover marketing spam, not fraud or impersonation | TDRA §1.10, §6.1, §11.1 | none / partial / present |
| **G2** | Government senders lack protected / authenticated-sender status | TDRA §13, PDPL Art. 2(2) | none / partial / present |
| **G3** | AI scanning of health SMS for fraud lacks an explicit legal basis | Law 2/2019 Art. 1, Art. 16 | none / partial / partial |
| **G4** | No emergency fast-path for AI-triggered failover of health data | Art. 13, Art. 24 | none / present / present |
| **G5** | No instrument assigns authority over operators' AI filter changes | **agent-discovered** (gate) | none / partial / partial |
| **G6** | No loss allocation when telecom anti-scam duties fail | comparator-discovered (SG SRF 6.4); **UAE absence to confirm** | none / none / present |

**Not fully addressed in any country: G3 and G5**, the candidates for international standards work. Standards gap: no declared autonomy level for telecom AI agents.
**Report idea:** present each gap as a chain: gap → verbatim evidence → draft fix → wind-tunnel test → measured effect.

## 9. System built (55 tests)

| Component | Files | What it does |
|---|---|---|
| Core | `app/core/{enums,audit,gateway,events,coordinator,firewall,injects,packs}.py` | Hash-chained audit; deterministic policy gateway (blocks only on verified binding clauses; unverified never blocks; uncovered → potential gap; conditions support `_not` and `_max`); time-gated, role-scoped event bus; coordinator (MLFO) with emergency state and age, per-tier second review; governed/ungoverned firewall with policy flags |
| Agents | `app/agents/{institution,retriever,llm,baselines}.py` | TDRA, Health Authority, AI & Data Authority. 5 gates: evidence, mandate/event-fit, **binding basis** ("soft law can inform, never compel"), **competence norm**, self-consistency |
| Clinical tiers (**provisional, pending clinician review**) | `kb/rulepacks/uae/health_tiers.yaml`, `app/core/tiers.py`, `app/fhir.py` | T1 life-critical: hold 5 min, receipt "call the patient" at 10 min · T2: 15 / 60 · T3: 60 / 1440. Priority declared by the authenticated sender (FHIR `CommunicationRequest.priority`, or SMPP `priority_flag` 1/2/3 = urgent/asap/stat), never read from content; unauthenticated claims ignored |
| Gap engine | `app/gapengine/*`, `run_gap_engine.py`, `signoff.py` | Abstract tactic battery (no phishing text); patches P-AUTH, P-ROUTE, P-FRAUD, P-VERIFIED; Mizan = mean(protection, access); load-bearing analysis; sign-off refused without evidence → ITU `kb_decisions` |
| **Wind tunnel** | `app/windtunnel/*`, `wind_tunnel.py`, `kb/rulepacks/uae/mechanisms.yaml` | Draft → LLM-proposed mechanism mapping (code-validated, human-confirmed) → conflict scan with hierarchy of norms → **8 invariants** (I1 no essential message lost; I2 no offshore transfer without sufficient legal rank; I3 spoofs never delivered; I4 blocks cite binding clauses; I5 audit verifies; I6 access doesn't regress; **I7 life-critical messages reach a human within their clinical limit; I8 emergency exceptions expire**) → metrics → interop → sealed impact card. Missing prerequisite mechanism → DO NOT ISSUE |
| Multi-country | `kb/rulepacks/{uae,india,singapore}`, `run_interop.py` | Rule packs, firewall mechanisms, pairwise agreement |
| Citizen verifier | `app/verifier.py`, `verify_message.py`, `kb/verifier_templates.yaml` | Deterministic verdict; EN/AR/HI/TE/UR/ML (EN/HI/TE reviewed; **Arabic review pending**); contradiction guard; message text never logged |
| SMPP server | `app/smpp/*`, `run_smpp.py`, `smpp_demo.py` | Real SMPP 3.4 (bind, submit_sm, enquire_link, unbind, deliver_sm; GSM/UCS-2); authentication = bound account authorised for the sender ID; block → 0x45; **accountable receipts** for held messages (ENROUTE, vendor TLVs 0x1401–0x1404: reason/authority, review-by, call-the-patient, audit hash; only when requested; never the text); `--panic` applies the Act 3 threshold |
| Network evidence | `tools/build_rlf_profile.py`, `app/network/act1.py` | Turkcell ITU challenge data (raw data not redistributed); data-driven storm and heatwave injects |
| Outputs | `build_dashboard.py`, `build_report_site.py`, `build_dataset.py`, `build_agent_cards.py`, `export_itu_game.py`, `selftest.py`, `setup.sh` | Technical dashboard; formal report site (`docs/index.html`); dataset (91 rows, CC-BY-4.0); agent cards; ITU game export; every number re-derived. Report site reads `docs/baselines_14b.md` (keep it in sync with `docs/baselines.md`) |
| Scenario | `scenarios/crisis_exploit.yaml` + 12 injects (incl. `critical_lab.yaml`, `stat_forged.yaml`); gold: `gold.yaml`, `gold_dev_b.yaml`, `gold_heldout_v2.yaml`, **`gold_heldout_v3.yaml` (pre-registered, commit 516c1e9)**; `ground_truth.yaml` (dashboard only) | Acts 1–4: energy-saving cell sleep → scam wave → panic filter + offshore failover (+ critical lab result held; forged "stat" claim) → 6-month silent drift and override dispute |
| Daily assurance report | `daily_report.py`, `docs/daily_report_{none,adopted}.md` | Regulator's one-page morning report. As-is: 0 of 4 genuine delivered immediately, 4 held, 0 lost. Adopted rules: 4 of 4 delivered immediately, 0 held, 0 lost, scams 5/5 stopped. Filter changes tested before deployment: 0/2 (gap G5) |
## 10. Results (reproducible with `python selftest.py`; all re-run at the 2 Nov freeze)

| Area | Result |
|---|---|
| Twin | Essential messages silently lost **3 → 0** (4 → 0 with the new critical-lab event); offshore transfers not blocked **2 → 0**; unaudited decisions **7 → 0** (9 with new events) |
| **Baselines (14b, 29 Oct)** | Rules 11/14 (3 harmful) · LLM-only 7/14 (5 harmful, **17 unsupported citations**) · RAG-no-gate 9/14 (5 harmful) · **HISN 13/14, held-out 4/4, 0 harmful, 0 unsupported, 0 unbound** |
| Baselines (7b) | Rules 11/14 · LLM-only 6/14 (20 unsupported) · RAG 9/14 · HISN 13/14 (1 harmful) |
| Agent evaluation | 7b: dev 10/10, held-out v2 3/4 (1 harmful) → **dev overfitting**; **14b (29 Oct): dev 9/10 (0 harmful; the miss was caught by the gate), held-out v2 4/4, 0 harmful**. Held-out v1 (pre-registered) was 3/6 and then moved to dev. Held-out v3 not yet run |
| Gap engine | Baseline Mizan 76.7 (protection 86.7, access 66.7); **P-AUTH + P-VERIFIED 94.2** (96.7 / 91.7, reviews 24 → 0); P-FRAUD alone −0.5 (over-blocks businesses); Art. 13 load-bearing (0 → 2) |
| **Wind tunnel** | Emergency-offshore as a **regulation → DO NOT ISSUE** (Art. 13 unresolved, I2 breaks); as a **Health Authority resolution with 72 h → READY** (I8 pass); **same with no time limit → DO NOT ISSUE** (I8 fail); auth + lane → READY (I3 fixed, Mizan 94.2) but UAE–IN 56 → 44% (*agreement ≠ quality*); **tiered holds → READY, I7 FAIL → PASS, nothing broken, UAE–IN unchanged**; bypass without authentication → DO NOT ISSUE (missing prerequisite) |
| Interop | UAE–IN 56% (55% with new events), UAE–SG 56%, IN–SG 78%; transfers: UAE block / India allow / Singapore hold; baseline Mizan UAE 76.7, IN 78.3, SG 79.2 |
| Retrieval | Recall@5 22/24, Recall@1 16/24, MRR 0.78; the 0.25 threshold doesn't transfer (ranges overlap 0.659 vs 0.698), so it's **not claimed** |
| Network | 985,308 link-days: heat RR **0.54**, rain RR **4.49**; median outage 5.9 min |
| SMPP | Genuine delivered; exact spoof and lookalike rejected 0x45; Arabic UCS-2 delivered. Booth step 1 (as-is + panic): genuine held; critical lab result held + receipt (T1 → health authority, review 5 min, call patient 10 min). Step 2 (adopted + panic): genuine delivered, spoof rejected, critical delivered |

**Flaws found and fixed (say so in the report):** the wind tunnel ignored the 72-hour parameter; it said READY despite a missing prerequisite; `hours` silently defaulted to 72; the report site read a stale baselines file.

## 11. Honest limitations (put in the report)

Synthetic data and scoring weights (direction, not magnitude); small n (add Wilson CIs); LLM run-to-run variation (baselines shifted 12 → 13/14 between runs; repeatability pending); 7b overfitted dev; the threshold didn't transfer; comparators partly verified (Singapore and India verified; Saudi historical only); the wind tunnel's conflict table is hand-authored and needs legal review; the mechanism mapping depends on a small local model and needs human confirmation (one mapping error observed and caught); **clinical tier limits are provisional placeholders pending clinician review**; held-out v3 has only 2 items; MIZAN measures blocking, not delay; real operators often label ("Suspected SPAM") rather than block, which our tiers and receipts should also cover; India/Singapore institutional agents not built; no expert review yet; a sandbox prototype, not production.

## 12. Report plan (≤ 5 pages, official template order)

Header (team, members, contacts, repo, video, email) → **Introduction** (open with the lab-result story, then the bigger frame) → **Use case** (problem + why existing solutions fall short, as a gap table) → **Requirements per node** → **Mapping table** (4 columns: node · implementation · Readiness 2.0 metric IDs · documents/articles; **all 9 nodes**, including tiers, I7, I8 and receipts) → **Error scenarios over time** (Acts 1–4, including controversy and pre-agreed rules) → **Policy and standards gaps** (G1–G6, domain-level, with verbatim evidence, the three-country comparison and the wind-tunnel chain). Lead with the **baselines table** and the **twin scoreboard**; give the wind tunnel one figure. New features get one sentence each. **Every link must work.**

## 13. Demo and video

**Mentoring demo, 31 Oct (3 min):** lab-result story → twin scoreboard → baselines → **SMPP booth demo** (held + receipt, then delivered under the recommended rules) → **live wind tunnel** (emergency draft as a regulation ❌, as a resolution ✅, without a time limit ❌) → ask: *"Would pre-issuance testing help the Regulatory Intelligence Office?"* and *"Are improvements between submission and the final welcome?"*
**Video (≤ 5 min):** problem (30 s) → twin (45 s) → agents and baselines (60 s) → gap engine (45 s) → wind tunnel (60 s) → three countries and gaps (30 s) → honest limits (15 s). Re-run `run_agents.py --model qwen2.5:14b` first.
**Booth:** `inject_console.py` (judge-typed SMS); `wind_tunnel.py` (judge-typed draft rule); SMPP two-step: `run_smpp.py --policy none --panic` + `smpp_demo.py`, then restart with `--policy adopted --panic` and run `smpp_demo.py` again. Everything runs offline.
**Tough questions to rehearse:** "Airtel already does this." "It's synthetic data." "Why use an LLM at all?" "Who would actually run HISN?" "Doesn't holding messages also delay them?"

## 14. Open tasks

| Task | Owner | By |
|---|---|---|
| Confirm initial-design email sent; WhatsApp Vishnu | Prudhvi | **Now** |
| **Clinician review of the tiers** (most urgent; three features depend on it); document the changes | Both | before 1 Nov |
| Arabic review of verifier templates; telecom engineer and lawyer (30 min each, one quote each) | Both | 3 Nov |
| Second-pass verification: G1–G6; confirm UAE has no loss-allocation rule (G6); Telecom Act s.20/s.28 commencement; PDPA schedule number; SSO URL; TRAI consolidated vs gazetted text; move statuses to "confirmed" | Prudhvi | 30 Oct |
| `docs/y3172_mapping.md` (all 9 nodes, incl. tiers, I7, I8, receipts) | Prudhvi (+ Claude) | 30 Oct |
| **2 Nov scenario freeze:** final 14b agents + baselines (with held-out v3), selftest, rebuild, redeploy | Eswar | 2 Nov |
| `daily_report.py`, law as a pull request, fairness check, country onboarding guide (cut from the bottom if late) | Eswar / Prudhvi | 3–5 Nov |
| Optional polish: Wilson CIs, 3× repeatability on 14b | Eswar | if budget allows |
| Report draft → send to ITU for review | Prudhvi (+ Claude) | draft 2 Nov, send 6 Nov |
| **Code freeze**, fresh-clone test of `setup.sh` | Eswar | 6 Nov |
| Video | Both | 8 Nov |
| Make the repo public, check all links, tag v3.6, submit | Both | **9 Nov** |
| After submission (Dubai upgrades): proof mode (Z3), TEC incident exporter, ITU standards contribution | Both | if shortlisted |

## 15. Commands cheat-sheet

```bash
cd ~/hisn && source .venv/bin/activate      # every new terminal tab
python -m pytest -q                         # 55 tests
python selftest.py                          # all headline numbers -> docs/headline_numbers.md
python run_agents.py --model qwen2.5:14b    # agents + pre-registered evaluation (~10 min)
python run_baselines.py --model qwen2.5:14b # four-way baselines (~45 min); then cp docs/baselines.md docs/baselines_14b.md
python run_gap_engine.py                    # loopholes, counterfactuals, load-bearing
python wind_tunnel.py "<draft>" --level regulation --yes
python run_interop.py                       # UAE / India / Singapore
python build_report_site.py                 # docs/index.html -> copy to ~/Desktop/hisn-site -> Netlify Deploys
python build_dashboard.py                   # technical dashboard
python run_smpp.py --policy none --panic    # booth step 1: today's rules + panicking operator
python run_smpp.py --policy adopted --panic # booth step 2: HISN-recommended rules
python smpp_demo.py                         # second tab, after starting the server
```

**Terminal lessons:** non-Latin scripts → edit files in TextEdit, never in heredocs; long pastes can truncate (paste blocks separately); if `[200~` appears, run `printf '\e[?2004l'` or open a new tab; file contents go into TextEdit, not the terminal; never add inject files while a baseline run is in progress; patch scripts check every edit before writing (re-running one that already succeeded fails harmlessly on the first edit).

## 16. After submission (2027 path)

AI for Good Global Summit, 21–24 Jun 2027, Geneva: offer the rule-pack and manifest schemas to ITU; publish agent cards; release the knowledge base and dataset openly; send the PR to ITU's reference repo (UAE country pattern, clause-aware chunking); propose a multi-country benchmark (UAE–India–Singapore) for the DoT / UAE–India Build-a-thon, Q1 2027; align with India's TEC AI standards (fairness TEC 57050:2023; AI incident reporting); draft a Kaleidoscope paper.