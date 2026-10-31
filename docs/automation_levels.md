# ITU-T Y.3173 network intelligence levels of HISN components

_Capability per dimension declared from Table 7-1 (kb/automation_levels.yaml); per-dimension and overall levels computed by app/core/automation.py exactly as clause 7.2 specifies (highest matching level per dimension; overall = minimum)._

| Component | Action impl. | Data collection | Analysis | Decision | Demand mapping | Overall |
|---|---|---|---|---|---|---|
| Operator SMS filter AI (as modelled) | System (L5) | Human and System (L2) | Human and System (L3) | Human and System (L3) | Human (L3) | **L2 Preliminary intelligence** |
| Network energy-saving AI (Act 1, as modelled) | System (L5) | Human and System (L2) | Human and System (L3) | Human and System (L3) | Human (L3) | **L2 Preliminary intelligence** |
| TDRA, Health Authority and AI & Data Authority agents | Human (L0) | Human and System (L2) | System (L5) | Human (L2) | Human (L3) | **L0 Manual network operation** |
| Policy and legal adviser agent | Human (L0) | Human and System (L2) | System (L5) | Human (L2) | Human (L3) | **L0 Manual network operation** |
| Deterministic policy gateway (Y.3172 P) | System (L5) | Human and System (L2) | Human and System (L3) | Human and System (L3) | Human (L3) | **L2 Preliminary intelligence** |
| Coordinator (Y.3172 MLFO) | System (L5) | Human and System (L2) | Human and System (L3) | Human and System (L3) | Human (L3) | **L2 Preliminary intelligence** |
| Regulatory wind tunnel | Human (L0) | Human and System (L2) | Human and System (L3) | Human and System (L3) | Human and System (L4) | **L0 Manual network operation** |
| Gap engine | Human (L0) | Human and System (L2) | Human and System (L3) | Human and System (L3) | Human (L3) | **L0 Manual network operation** |

**Reading:** the language-model components (agents, adviser) analyse at the System level but are L0 overall, because they never implement actions; the wind tunnel and gap engine are L0 because nothing is adopted without named sign-off. The network functions run at L2 under human-defined rules.

**Table 7-2 Note 1 (human authority):** in every component, decisions and instructions by a human have the highest authority: held messages are released by a named human, a second human reviews within the clinical limit, and sign-off is refused without evidence.

## Justifications (Table 7-1 conditions)

**Operator SMS filter AI (as modelled)**
- action implementation: System. Delivers, holds or blocks every message automatically in all scenarios.
- data collection: Human and System. Collects message metadata automatically according to rules defined by humans.
- analysis: Human and System. Scores messages automatically according to rules defined by humans (keyword, route and URL rules).
- decision: Human and System. Applies thresholds defined by humans.
- demand mapping: Human. Threshold changes are set by operations teams; HISN requires a named approval for each change.

**Network energy-saving AI (Act 1, as modelled)**
- action implementation: System. Puts cells into energy-saving sleep automatically.
- data collection: Human and System. Collects network KPIs automatically according to rules defined by humans.
- analysis: Human and System. Analyses KPIs according to rules defined by humans.
- decision: Human and System. Triggers energy-saving mode according to rules defined by humans.
- demand mapping: Human. Energy-saving targets are set by operations teams.

**TDRA, Health Authority and AI & Data Authority agents**
- action implementation: Human. Agents only propose; every action is executed by deterministic code or a named human.
- data collection: Human and System. Receive only events routed to their role and retrieve evidence by human-defined intents.
- analysis: System. Language-model analysis uses learned rules, not human-written ones.
- decision: Human. Decisive actions need a named human; deterministic gates can only downgrade a proposal to a logged gap.
- demand mapping: Human. Mandates and allowed actions are written by humans.

**Policy and legal adviser agent**
- action implementation: Human. Answers only; never acts.
- data collection: Human and System. Retrieves evidence automatically from a human-curated knowledge base.
- analysis: System. Language-model analysis uses learned rules.
- decision: Human. Answers inform; humans decide (Readiness Report 2.0 FAQ 7).
- demand mapping: Human. Questions are posed by humans.

**Deterministic policy gateway (Y.3172 P)**
- action implementation: System. Blocks or allows data transfers automatically in all scenarios.
- data collection: Human and System. Receives event fields defined by humans.
- analysis: Human and System. Matches events against a human-authored, verified rule pack.
- decision: Human and System. Decides by rules defined by humans.
- demand mapping: Human. Rules are authored and verified by humans.

**Coordinator (Y.3172 MLFO)**
- action implementation: System. Routes events, escalations and referrals automatically.
- data collection: Human and System. Releases events according to human-defined timing and audiences.
- analysis: Human and System. Applies pre-agreed rules.
- decision: Human and System. Tier limits and routing rules are defined by humans.
- demand mapping: Human. Scenario and rules are written by humans.

**Regulatory wind tunnel**
- action implementation: Human. Nothing is issued without named human sign-off.
- data collection: Human and System. Runs the human-defined scenario and battery.
- analysis: Human and System. Deterministic invariants and conflict table defined by humans.
- decision: Human and System. Verdict computed by human-defined rules.
- demand mapping: Human and System. A model proposes the mechanism mapping from a human-defined vocabulary; a human confirms it.

**Gap engine**
- action implementation: Human. Patches are adopted only with named sign-off.
- data collection: Human and System. Runs a human-defined abstract tactic battery.
- analysis: Human and System. Measures effects with human-defined metrics.
- decision: Human and System. Flags loopholes by human-defined criteria.
- demand mapping: Human. Candidate patches are written by humans.

