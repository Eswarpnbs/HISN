# Real smishing evaluation: 5,971 real SMS

Input: SMS Phishing Dataset (Mishra and Soni 2022, Mendeley Data, CC BY 4.0), 5971 messages (4844 legitimate, 638 smishing, 489 spam); columns `LABEL`/`TEXT`; SHA-256 of input `649844f1c62a6b27e145eaf17a65f7010c56c390e11a794ea8329993a05ba71e`. Produced by `python tools/real_smishing_eval.py`. Counting rules were committed before the first run.

## 1. HISN message checks (facts given to the agents)

| Class | Any risk signal | Asks for a secret | Web address | Offers a link | Number to call |
|---|---|---|---|---|---|
| smishing | 505/638 = 79.2% (75.8-82.1%) | 1/638 = 0.2% (0.0-0.9%) | 96/638 = 15.0% (12.5-18.0%) | 7/638 = 1.1% (0.5-2.2%) | 413/638 = 64.7% (60.9-68.3%) |
| spam | 195/489 = 39.9% (35.6-44.3%) | 1/489 = 0.2% (0.0-1.1%) | 85/489 = 17.4% (14.3-21.0%) | 2/489 = 0.4% (0.1-1.5%) | 114/489 = 23.3% (19.8-27.3%) |
| ham | 7/4844 = 0.1% (0.1-0.3%) | 4/4844 = 0.1% (0.0-0.2%) | 2/4844 = 0.0% (0.0-0.2%) | 0/4844 = 0.0% (0.0-0.1%) | 1/4844 = 0.0% (0.0-0.1%) |

## 2. Prototype filter at the operator thresholds

| Threshold | Legitimate blocked | Smishing caught | Spam caught |
|---|---|---|---|
| 0.5 | 0/4844 = 0.0% (0.0-0.1%) | 13/638 = 2.0% (1.2-3.5%) | 2/489 = 0.4% (0.1-1.5%) |
| 0.2 | 121/4844 = 2.5% (2.1-3.0%) | 169/638 = 26.5% (23.2-30.0%) | 27/489 = 5.5% (3.8-7.9%) |
| 0.15 | 121/4844 = 2.5% (2.1-3.0%) | 169/638 = 26.5% (23.2-30.0%) | 27/489 = 5.5% (3.8-7.9%) |

Reading: the message checks are what the agents are told; a high rate on smishing with a low rate on legitimate SMS means the facts are informative. They never block anything by themselves: an unauthenticated sender claiming a protected entity is held by the fixed gate, and a person decides.

Limits: English SMS collected for research (mostly India and UK), not UAE traffic; no sender IDs or authentication, so the essential-sender lane is not tested.
