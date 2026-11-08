# Real Arabic message evaluation: 13,241 real Arabic tweets (original file only)

Input: Dataset of Arabic Spam and Ham Tweets (Kaddoura and Henno, Zayed University, CC BY 4.0), 13240 messages (11299 legitimate `ham`, 1941 spam `spam`); text column `Tweet Text`, label column `Label`; SHA-256 of input `1135b1b4ff20bd2630c2d39458a360bccfe061c00a784a983e9429de122270e9`. Produced by `python tools/real_arabic_eval.py`. Counting rules were committed before the first run.

| Class | Filter keyword hit (would be scored up) | Any message-check risk signal | Asks for a secret |
|---|---|---|---|
| spam | 48/1941 = 2.5% (1.9-3.3%) | 63/1941 = 3.2% (2.5-4.1%) | 0/1941 = 0.0% (0.0-0.2%) |
| legitimate | 226/11299 = 2.0% (1.8-2.3%) | 94/11299 = 0.8% (0.7-1.0%) | 0/11299 = 0.0% (0.0-0.0%) |

Reading: a keyword hit on legitimate Arabic means the filter would score it up. For an essential sender HISN then holds and routes it to a named officer instead of losing it; for others it is the operator's filter cost. The Arabic keywords and checks were written by the team and are pending native review.

Limits: tweets (2023, Gulf Arabic and MSA), not SMS; no sender authentication.
