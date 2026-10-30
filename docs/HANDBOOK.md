# HISN — Project Handbook (Team Sankalp)
*Single source of truth. Last updated 30 Oct 2026 (evening).*

## 1. Competition facts

| Item | Detail |
|---|---|
| Event | ITU AI for Good Lab Hackathon, UAE edition 2026 |
| Team | **Team Sankalp**: Eswar Panchakarla (leader, engineering), P. Prudhvi Krishna (knowledge base, policy, report), Bengaluru. Max 4 members; all must be named in the report |
| Registered domains | Telecom + healthcare + public services (confirmed by Vishnu as "what we look for") |
| Submission | **Submit 9 Nov** (deadline 10 Nov 2026) to **aiforgoodlab@itu.int**: technical report (max 5 pages, official template), GitHub repository, knowledge base |
| Video | **Optional in round 1**; required for shortlisted teams; **max 7 minutes** |
| Evaluation / shortlist | 11–18 Nov first round; shortlist announced 18 Nov |
| Final | 8 Dec, onsite at GITEX Dubai; awards 10 Dec |
| Prizes | CHF 1,500 / 1,000 / 600; Judges' prize CHF 1,000 (engagement, future research, development, innovation or **standards potential**); one prize per team |
| Opportunity | Winning solutions may be deployed in the **2027 Summit live multi-country error exercise** |
| Mentoring | Saturdays 10:00 CET = **14:30 IST**; sessions remaining: **31 Oct, 7 Nov** |
| Sandbox / credits | Initial-design email **sent 29 Oct** (13/14, 17 unsupported citations); WhatsApp Vishnu |
| Repo | github.com/Eswarpnbs/HISN (**private until 9 Nov**); contact eswarpnbs@gmail.com in README |
| Hosted report | hisn-report.netlify.app (redeployed 29 Oct; **rebuild and redeploy after the freeze run**) |

## 2. What the judges score

**Official evaluation criteria (problem statement):**
1. **Knowledge-base quality:** completeness, accuracy and structure of ingested national material; retrieval of relevant policy context.
2. **Agent capability:** relevance and accuracy in simulated error scenarios; adherence to laws, mandates and coordination mechanisms.
3. **Policy, strategy and standards gaps:** unclear responsibilities, standards, technology and legislative gaps, coordination problems, conflicting objectives. **Relevance of gaps and accuracy of global policy examples is "critical".** Domain-level, not country-specific recommendations.
4. **Auditability:** logs, reasoning traces, source attribution.
5. **Alignment with ITU standards:** Y.3172 pipeline and AI Readiness Framework.

**FAQ facts:** accuracy of the prototype is **not** an evaluation criterion (lead with gaps and auditability, not 13/14). Pick evaluation scenarios **where policy gaps can be identified**. Follow-ups: ITU Study Group contributions, Kaleidoscope paper, open source.

**Report contents (FAQ a–h):** (a) introduction of the agentic solution; (b) use case; (c) requirements; (d) Y.3172 mapping; (e) ITU AI Readiness Report 2.0 mapping; (f) requirements mapped to local policies; (g) evaluation scenario covering technical solution and policy; (h) policy and standards gaps.

**From mentoring and winning repos:** gap analysis valued most; policy node governs every step; Samaam's report is the model; evidence or silence; controversy covered; pre-agreed rules; judges may inject events live; policy-ON vs OFF and RAG vs no-RAG comparisons (done).

**Red lines:** any unverified law or URL (don't cite the contested "UAE/Dubai AI Act"); confidential data; country-level recommendations; a pitch deck instead of a prototype; more than 5 pages; real phishing text; broken links; imitating official government websites or emblems; claiming "first in the world".

## 3. Competition analysis

| Team | Result | What won it |
|---|---|---|
| **SANAD** (Saudi) | 1st | Rigour: every number traceable to a command, Wilson CIs, schema offered to ITU |
| **AI Guardian** | 2nd | 49 frameworks, provenance, SHA-256 chain, devil's-advocate agent; weaknesses: broken links, wrong dimension names |
| **Samaam** | 3rd | 403 gateway, FHIR/DICOM, offline, one-command run, only 3 evidenced dimensions, radiologist review changed the design |
| **Netaxis** (Build-a-thon 5.0) | 1st | Agents propose, code decides; time-gated events; forged-input tests; non-AI baselines; honest about limits |

**HISN's differentiators:** ready-to-run multi-agent, multi-country policy error exercise; regulatory wind tunnel with 8 invariants (incl. clinical limit and sunset), running as **law as a pull request** in CI; audited referral protocol between authorities; policy and legal adviser agent; gap register with verified global examples from 5 jurisdictions; cross-language fairness check and pre-deployment filter-change gate; daily assurance report; real SMPP server with accountable receipts; FHIR clinical priority; real operator network data; pre-registered held-out tests; four-way baselines; Wilson CIs.

## 4. ITU reference code (CrashingGuru/ITUAIReadiness/simulation)

- AI Readiness Simulation Game by Vishnu Ram. Collections: `kb_main`, `kb_framework`, `kb_decisions`, `kb_usecase`.
- **Official Y.3172 → dimension mapping:** SRC→D1, D4, D13; C→D1, D3, D13; PP→D1, D2, D3; M→D2, D3, D5, D9; **P→D7, D8, D10**; D→D5, D6, D12; SINK→D5, D6, D12, D13; MLFO→D5, D7, D8; Sandbox→D10, D11.
- **Causal graph:** D10→D7, D13→D5, D7→D12 (0.5 each).
- **No UAE documents** in ITU's inputs: our UAE corpus is a genuine contribution. No SMS scam data in ITU's sandbox (we published one).
- Human-approved fixes go to ITU's `kb_decisions`.

**Metric names verified against ITU's `data/framework/dimensions.json` (30 Oct):** d3_m01 Integrated Workflow · d3_m07 Coverage and Scale · d7_m01 Coordination Level · d7_m03 Intent Representations · d7_m04 Interoperability Standards · d7_m08 International Cooperation · d10_m01 Policy Sandbox · d10_m02 Policy Evaluation · d10_m03 Policy Extrapolation · d10_m06 Safety Policies · d10_m07 Explainability Metrics · d10_m09 Audit Metrics · d10_m10 Data Sovereignty · d11_m07 Language Repository · d11_m08 Regional Language Support (claim after Arabic review) · d13_m07 Uptime · d13_m08 Area Coverage · d13_m09 Network Quality. Full mapping: `docs/y3172_mapping.md`, `docs/readiness_mapping.md`.

## 5. UAE policy landscape (verified)

- **Regulatory Intelligence Office** (Cabinet, Apr 2025): AI-assisted, "living" legislation; law as a continuously updated dataset.
- **Federal AI & Data Authority** (14 Jun 2026): merges the AI Office, TDRA's digital-government arm and the Emirates Data Office. TDRA remains the telecom regulator.
- **Telecom Law Art. 14(3):** TDRA is solely responsible for regulations on subscriber service standards and complaints, so the power to govern operators' filters already exists.
- **HISN's hook:** a domain-scale prototype of pre-issuance testing for living, AI-assisted law.

## 6. The concept

**HISN (حصن, "fortress")** governs the telecom AI that decides whether essential health and government messages reach people.

- **One sentence:** *HISN governs the AI that decides which health and government messages reach citizens, and gives every draft rule a test suite before it takes effect.*
- **Opening line:** *"A patient's critical test result was blocked by an AI spam filter. The hospital never knew. Today, no law says who's responsible."*
- **Frame for judges and ITU:** *a ready-to-run multi-country policy error exercise for AI in critical public communications*, the kind the 2027 Summit plans to run live.
- **Sharp insight:** emergency alerts have a protected lane; your critical lab result doesn't.
- **Positioning:** operators already run network AI on every SMS (e.g. Airtel since Sept 2024, with acknowledged false positives). HISN doesn't replace it; it governs it. It plugs into SMPP 3.4, HL7 FHIR and Y.3172.
- **Scope:** essential health messages (lead) and government service messages only.
- **Controversies addressed:** over-blocking hospital messages; AI scanning of health SMS without legal basis (G3); emergency powers that never end (I8); language bias in content filtering.

## 7. Knowledge base (15 records, 36 verbatim clauses, SHA-256 pinned, all verified)

| Record | Instrument | Status |
|---|---|---|
| UAE-FL-2-2019 | Federal Law No. 2 of 2019 (ICT in Health Fields) | official |
| UAE-PDPL-2021 | Federal Decree-Law 45/2021 (PDPL) | official |
| UAE-TDRA-UEC-2022 | TDRA Unsolicited Electronic Communications Policy v1.1 | official |
| **UAE-TELECOM-2003** | Federal Decree-Law No. 3 of 2003 Regulating Telecommunications (as amended) | official (added 30 Oct) |
| **UAE-CYBERCRIME-2021** | Federal Decree-Law No. 34 of 2021 on Countering Rumors and Cybercrimes (as amended 2024) | official (added 30 Oct) |
| UAE-DOH-AI-2018 | DoH Abu Dhabi AI policy | official |
| UAE-DOH-RAI-2025 | DoH Responsible AI Standard | official |
| UAE-AI-CHARTER-2024 | UAE AI Charter | official_archived (soft law) |
| UAE-AI-STRATEGY-2031 | National AI Strategy 2031 | official_archived (soft law) |
| IN-DPDP-2023 | Digital Personal Data Protection Act 2023 | official |
| IN-TELECOM-ACT-2023 | Telecommunications Act 2023 | **official; s.20 and s.28 in force from 26 Jun 2024 (S.O. 2408(E))** |
| IN-TRAI-TCCCPR-CONS | TRAI TCCCPR consolidated text (May 2026; **includes the Feb 2025 amendment**) | official reference; gazetted text prevails |
| SG-SRF-2024 | MAS–IMDA Shared Responsibility Framework | official |
| SG-PDPA-2012 | PDPA 2012 | official; emergency exception = **First Schedule, Part 1, para 2** (confirmed) |
| SA-CST-SPAM-2018 | CST Regulation for Reduction of SPAM (2018 draft translation) | historical, background only |

**Key clauses:** UAE Law 2/2019 Art. 1, 4, 13, 16, 24; TDRA §1.10, §6.1, §8.5.3, §11.1–11.2, §13; PDPL Art. 2(2); Charter P2, P5, P6, P7; **Telecom Law Art. 12 (TDRA oversees licensees), Art. 14(3) (subscriber service standards); Cybercrime Law Art. 40 (internet fraud, false impersonation)**. India: DPDP s.4(1), s.7(f)–(h), s.16, s.17(2)(a); Telecom Act s.20(1), s.28; TRAI Header Register, reg. 33(1); **IN-TRAI-GOVMSG (Government Message definition, 2025)**. Singapore: SRF definitions, 5.2.1–5.2.3, fn 9, 6.4; PDPA s.26, First Schedule Part 1 para 2.
**Cited outside the pinned corpus:** CBUAE Consumer Protection Regulation, Art. 6, cl. 6.2.2.4 (verified on the CBUAE Rulebook, 30 Oct).
**Retrieval test:** `kb/retrieval_gold.yaml`, 50 questions (46 answerable, 4 out-of-corpus), v2 additions pre-registered 30 Oct.
**Lessons:** never run `ingest_uae.py` during agent or baseline runs (it resets the KB); the UAE portal blocks `curl`, so download PDFs in a browser.

## 8. Gap register (`docs/gap_register.yaml`; global examples in `docs/global_examples.yaml`)

| Gap | Statement | Evidence | UAE / IN / SG | Global examples (verified) |
|---|---|---|---|---|
| **G1** | Telecom filtering duties cover marketing spam, not fraud or impersonation | TDRA §1.10, §6.1, §11.1; **Cybercrime Law Art. 40** (the scammer's act is a crime, but operators have no filtering duty) | none / partial / present | Australia: Scams Prevention Framework Act 2025; ACMA Industry Code C661:2022 |
| **G2** | Government senders lack protected / authenticated-sender status | TDRA §13, PDPL Art. 2(2) | none / **present** / present | India: TCCCPR 2025 Government Message ("-G", DLT-only, can't be blocked via preferences); Australia: SMS Sender ID Register (1 Jul 2026, labels unregistered IDs "Unverified") |
| **G3** | AI scanning of health SMS for fraud lacks an explicit legal basis | Law 2/2019 Art. 1, Art. 16 | none / partial / partial | EU: scanning private communications needed a specific, temporary derogation (Reg. 2021/1232; lapsed Apr 2026, reinstated Jul 2026 to Apr 2028) |
| **G4** | No emergency path for **systematic, AI-triggered** failover of health data | Art. 13, Art. 24 | none / present / present | EU: GDPR Art. 49(1)(f) covers individual, occasional emergencies only (EDPB 2/2018) |
| **G5** | No instrument assigns authority over operators' AI filter changes | agent-discovered (gate); **competence exists in Telecom Law Art. 14(3) but is not exercised** | none / partial / partial | Australia (partial): C661:2022 oversees outcomes and false positives, not change approval; EU: none found |
| **G6** | No allocation of scam losses to **telecom operators** when their duties fail | SG SRF 6.4; UAE bank-side compensation exists (CBUAE CPR cl. 6.2.2.4, verified) | none (telecom) / none / present | Australia: SPF compensation pathway, compliance-linked; Scams Ombudsman from 31 Mar 2027 |

**Standards candidates (Judges' prize, ITU Study Groups):** G3 and G5, plus a declared autonomy level for telecom AI agents.
**Report idea:** each gap as a chain: gap → verbatim evidence → global example → draft fix → wind-tunnel test → measured effect.

## 9. System built (68 tests)

| Component | Files | What it does |
|---|---|---|
| Core | `app/core/{enums,audit,gateway,events,coordinator,firewall,injects,packs}.py` | Hash-chained audit; policy gateway (`_not`, `_max` conditions); time-gated, role-scoped events; coordinator with emergency age, per-tier second review and **audited referral routing** (`route_referrals=True` in `run_agents.py` only; REFER_TO_TDRA delivered once to TDRA) |
| Agents | `app/agents/{institution,retriever,llm,baselines}.py` | TDRA, Health Authority, AI & Data Authority; 5 gates (evidence, mandate, binding basis, competence, self-consistency); TDRA handles referrals |
| **Policy and legal adviser** | `app/agents/adviser.py`, `ask_adviser.py --country UAE/IN/SG` | Answers legal questions from retrieved evidence only; invented citations withheld; soft-law-only = no binding basis; related gaps with verified global examples; audited |
| Clinical tiers (**provisional**) | `kb/rulepacks/uae/health_tiers.yaml`, `app/core/tiers.py`, `app/fhir.py` | T1 5/10 min · T2 15/60 · T3 60/1440; priority declared by the authenticated sender (FHIR or SMPP `priority_flag`) |
| Gap engine | `app/gapengine/*`, `run_gap_engine.py`, `signoff.py` | Tactic battery; P-AUTH, P-ROUTE, P-FRAUD, P-VERIFIED; MIZAN; load-bearing analysis |
| **Wind tunnel** | `app/windtunnel/*`, `wind_tunnel.py`, `kb/rulepacks/uae/mechanisms.yaml` | Draft → mechanisms (human-confirmed) → conflicts → **8 invariants (I1–I8)** → metrics → interop → impact card; missing prerequisite → DO NOT ISSUE; `hours` unstated = no limit |
| **Law as a pull request** | `drafts/*.yaml`, `app/windtunnel/confirmed.py`, `tools/wind_tunnel_ci.py`, `.github/workflows/wind-tunnel.yml` | Draft rules proposed as pull requests; CI runs the wind tunnel and posts the impact card; check fails on DO NOT ISSUE (closed PR #1 = evidence) |
| Multi-country | `kb/rulepacks/{uae,india,singapore}`, `run_interop.py` | Rule packs; pairwise agreement |
| Citizen verifier | `app/verifier.py`, `verify_message.py`, `kb/verifier_templates.yaml` | 6 languages (EN/HI/TE reviewed; **Arabic pending**) |
| SMPP server | `app/smpp/*`, `run_smpp.py` (`--policy none/adopted`, `--panic`), `smpp_demo.py` | Real SMPP 3.4; accountable receipts for held messages (TLVs 0x1401–0x1404); never the text |
| Daily assurance report | `daily_report.py --policy none/adopted` | Regulator's morning page; includes the filter-change gate verdicts |
| Fairness check | `tools/fairness_check.py`, `scenarios/fairness_pairs.yaml` (non-English pending review) | Same message, 6 languages, 4 policy states |
| Filter-change gate | `app/core/fairness.py`, `tools/filter_change_check.py --threshold X` | DEPLOY / DO NOT DEPLOY on language parity |
| Statistics | `app/core/stats.py` | 95% Wilson intervals on all accuracies (dashboard, report site, selftest) |
| Outputs | `build_dashboard.py`, `build_report_site.py`, `build_dataset.py`, `build_agent_cards.py`, `export_itu_game.py`, `selftest.py`, `setup.sh` | Every number re-derived; report site reads `docs/baselines_14b.md` (copy after each baseline run); held-out v3 shown |
| Scenario | `scenarios/crisis_exploit.yaml` + 12 injects; gold `gold.yaml`, `gold_dev_b.yaml`, `gold_heldout_v2.yaml`, `gold_heldout_v3.yaml` (pre-registered, 516c1e9) | Acts 1–4 incl. critical lab result and forged "stat" claim |
| Mapping docs | `docs/y3172_mapping.md`, `docs/readiness_mapping.md` | All 9 nodes; verified metric names; 8 perspectives with evidence |

## 10. Results (all re-run at the freeze; KB changed on 30 Oct, so agent and baseline numbers will move)

| Area | Result |
|---|---|
| Twin | Silently lost 4 → 0; offshore transfers 2 → 0; unaudited decisions 9 → 0 |
| Baselines (14b, 29 Oct) | Rules 11/14 (3 harmful) · LLM-only 7/14 (5 harmful, 17 unsupported) · RAG 9/14 (5 harmful) · **HISN 13/14 (69–99%), held-out 4/4, 0 harmful, 0 unsupported** |
| Agents (14b, 29 Oct) | dev 9/10 (0 harmful), held-out v2 4/4; held-out v3 not yet run |
| Gap engine | MIZAN 76.7 → **94.2** with P-AUTH + P-VERIFIED; P-FRAUD alone −0.5 |
| Wind tunnel | Emergency offshore: regulation ❌, resolution 72 h ✅, no time limit ❌ (I8); tiered holds ✅ (I7 fixed, nothing broken); bypass without authentication ❌ (missing prerequisite); CI PR #1 refused automatically |
| Daily report | Today's rules: 0/4 genuine delivered immediately, 4 held, 0 lost; recommended rules: 4/4 delivered, 0 held, 0 lost, scams 5/5 stopped; filter changes: both DO NOT DEPLOY |
| Fairness | Today's rules after panic/drift: English critical message held, 5 other languages delivered; recommended rules: equal in all 6 |
| Adviser | "Can an operator scan health SMS content?" UAE and India: no binding basis → G3, EU example |
| **Retrieval (50 questions)** | **Clause-first (agents' order) Recall@5 41/46 (77–95%)**, R@1 22/46, MRR 0.63; plain R@5 34/46 strict, 39/46 passage-level; out-of-corpus similarity up to 0.698 (thresholds not claimed); 2 Charter questions miss |
| Interop | UAE–IN 55%, UAE–SG 56%, IN–SG 78% |
| Network | 985,308 link-days: heat RR 0.54, rain RR 4.49 |
| Fresh clone | `setup.sh` on a clean machine: KB builds from verbatim clauses, all tests pass |

**Flaws found and fixed (say so in the report):** wind tunnel ignored the 72-hour parameter; READY despite a missing prerequisite; `hours` defaulted to 72; report site read a stale baselines file; retrieval test re-sorted results and hid clause-first's advantage; `verify.py` said "verified" when sources were missing; G6 overstated (UAE has bank-side compensation); India G2 understated.

## 11. Honest limitations

Synthetic data and weights (direction, not magnitude); small samples (Wilson CIs shown); LLM run-to-run variation; 7b overfitted dev; similarity thresholds not a safeguard; conflict table hand-authored, needs legal review; mechanism mapping needs human confirmation; **clinical tiers provisional pending clinician review**; held-out v3 has 2 items; MIZAN measures blocking, not delay; operators often label rather than block; fairness texts machine-drafted, pending native review; retrieval R@1 trade-off for clause-first; simplified filter model, not a real operator's AI; India and Singapore agents not built; no expert review yet; sandbox prototype, not production.

## 12. Report plan (≤ 5 pages, following FAQ a–h)

Header (team, members, contact, repo, video, email) → **(a) Introduction:** lab-result story, then the "multi-country error exercise" frame → **(b) Use case** → **(c) Requirements** → **(d) Y.3172 mapping** (all 9 nodes, from `docs/y3172_mapping.md`) → **(e) Readiness Report 2.0** (8 perspectives + metrics, from `docs/readiness_mapping.md`) → **(f) Local policy mapping** (UAE clauses per requirement) → **(g) Evaluation scenario** (Acts 1–4, twin, agents, wind tunnel, adviser, fairness) → **(h) Gaps** (G1–G6 chains with global examples; G3/G5 as standards candidates). Lead with gaps and auditability, not accuracy. Every link must work.

## 13. Demo and video

**Mentoring demo, 31 Oct (3 min):** lab-result story → SMPP held + receipt → daily reports side by side → GitHub PR #1 (law refused) → adviser live (let Vishnu ask) → baselines in one line → two questions: *pre-issuance testing for the Regulatory Intelligence Office?* and *are improvements after submission welcome?*
**Video (≤ 7 min, optional in round 1):** script drafted in chat (problem, twin, agents and baselines, gaps, wind tunnel, three countries, limits, close); record after the freeze.
**Booth:** `inject_console.py`; `wind_tunnel.py`; `ask_adviser.py`; SMPP two-step (`--policy none --panic`, then `--policy adopted --panic`). All offline.
**Tough questions:** "Airtel already does this." "It's synthetic." "Why an LLM?" "Who would run HISN?" "Doesn't holding delay messages?" "Isn't SMS blocking rare?" (answer: the scenario is chosen to surface gaps, as the FAQ asks).

## 14. Open tasks

| Task | Owner | By |
|---|---|---|
| Rehearse mentoring demo twice; record all feedback | Both | 31 Oct |
| **Clinician review of tiers** (briefs ready) | Both | ASAP |
| Arabic review (verifier + fairness texts); telecom engineer and lawyer quotes | Both | 3 Nov |
| **Freeze run:** agents + baselines (held-out v3, new KB), `cp docs/baselines.md docs/baselines_14b.md`, selftest, rebuild all pages, daily reports, fairness, redeploy | Eswar | after mentoring; again if tiers change |
| Report draft (FAQ a–h) → ITU review | Prudhvi (+ Claude) | draft 2–3 Nov, send 6 Nov |
| Video | Both | 8 Nov |
| 9 Nov: repo public; **branch protection requiring "Regulatory wind tunnel"**; click every link; tag v3.6; submit | Both | 9 Nov |
| Optional: 3× repeatability on 14b | Eswar | if time |
| Dubai upgrades: proof mode (Z3), TEC incident exporter, ITU standards contribution (G3, G5) | Both | if shortlisted |

## 15. Commands cheat-sheet

```bash
cd ~/hisn && source .venv/bin/activate      # every new terminal tab
python -m pytest -q                         # 68 tests
python selftest.py                          # headline numbers -> docs/headline_numbers.md
python run_agents.py --model qwen2.5:14b    # agents + referrals + pre-registered evaluation
python run_baselines.py --model qwen2.5:14b && cp docs/baselines.md docs/baselines_14b.md
python kb/register.py && python kb/verify.py && python kb/ingest_uae.py   # KB (never during runs)
python kb/eval_retrieval.py                 # 50-question retrieval test
python ask_adviser.py "<question>" --country UAE
python wind_tunnel.py "<draft>" --level regulation --yes
python tools/wind_tunnel_ci.py drafts/<file>.yaml
python daily_report.py --policy none        # and --policy adopted
python tools/fairness_check.py
python tools/filter_change_check.py --threshold 0.2
python build_dashboard.py && python build_report_site.py   # then copy docs/index.html to ~/Desktop/hisn-site -> Netlify
python run_smpp.py --policy none --panic    # booth step 1 (then smpp_demo.py in a second tab)
python run_smpp.py --policy adopted --panic # booth step 2
```

**Terminal lessons:** non-Latin text → TextEdit, not heredocs; long pastes can truncate (paste in parts; check with `tail`); file contents go into TextEdit, not the terminal; replace `<placeholders>` with real values; quote file names with spaces; never add injects during a baseline run; patch scripts check every edit before writing (re-running a finished one fails harmlessly); zsh needs quotes around `--include="*.py"`; GitHub workflow pushes need a token with `workflow` scope.

## 16. After submission (2027 path)

Geneva Summit (21–24 Jun 2027): offer HISN for the live multi-country error exercise; contribute G3 and G5 to ITU Study Groups; offer rule-pack and manifest schemas; release the knowledge base and dataset; send the PR to ITU's reference repo (UAE country pattern, clause-aware chunking); propose a UAE–India–Singapore benchmark for the DoT / UAE–India Build-a-thon (Q1 2027); align with India's TEC AI standards (TEC 57050:2023; AI incident reporting); Kaleidoscope paper.