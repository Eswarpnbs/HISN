# HISN Synthetic SMS Governance Dataset

Synthetic SMS metadata for testing governance of AI message filters that affect essential health and government messages: abstract tactic battery (exact spoof, lookalike, unregistered payment demand, legitimate essential and business traffic) across normal/panic/drift filter states, plus labelled scenario events. Fictional senders and example.* domains only; placeholder text, no persuasive content.

- rows: 91 ({'malicious': 64, 'legitimate': 27})
- licence: CC-BY-4.0
- sha256: `e72714484638d253ccbc56c2b172bc4c9ab07965a5ea4d5771090d6c6b272552`
- regenerate: `python build_dataset.py`

- note: class imbalance (64 malicious / 27 legitimate) by design - the battery probes attack tactics; rebalance before training classifiers
