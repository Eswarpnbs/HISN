# Governance case brief: the filter-threshold change

_A policy input in the sense of ITU AI Readiness Report 2.0, Dimension 10: an operational lesson turned into a governance lesson. Synthetic scenario; domain-level lesson, not a national recommendation._

## What happened
After a scam wave, the operator tightened its SMS filter (threshold 0.50 to 0.20, Act 3). Six months later the vendor silently retuned it (0.15, Act 4). Neither change had a named approval or a pre-deployment test.

## What it broke
- **Genuine messages held:** 4 of 4 genuine hospital and government messages were held for a human instead of delivered.
- **Unequal by language:** the same critical lab result was held in English but delivered in Arabic, Hindi, Telugu, Urdu and Malayalam, because content scoring reads only English.
- **Outside the safe range:** replaying the timeline shows current rules meet all targets only at thresholds of 0.30 or above; both real changes (0.20, 0.15) fall outside it.
- **Declared automation level broken:** the filter's demand mapping is declared "Human" (ITU-T Y.3173), but both changes had no named approval: 2/2 violations.

## Why
The filter decides on content with a human-set threshold, and nobody is assigned to approve changes to it: a missing upgrade-stage lifecycle policy (gap G5). Australia's C661:2022 code oversees filter outcomes and false positives, but not change approval; no example of change approval was found.

## The rule that prevents it (tested)
1. **Pre-deployment check for every filter change:** both scenario changes return DO NOT DEPLOY.
2. **Identity-based protection:** under the tested rule set (sender authentication + verified lane), every threshold meets every target and all 6 languages are treated equally.

## Lesson
Safety should not depend on an AI parameter nobody approves. Either the parameter needs an accountable approval step, or protection should rest on something it cannot change: verified sender identity.

_Evidence: docs/daily_report_none.md, docs/fairness_check.md, docs/what_if_none.md, docs/automation_levels.md, docs/gap_register.yaml, docs/global_examples.yaml._
