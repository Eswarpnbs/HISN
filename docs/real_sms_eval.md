# Real-message evaluation: threshold drift on 5,574 real SMS

Input: SMS Spam Collection (UCI, CC BY 4.0), 5574 messages (4827 legitimate, 747 spam); SHA-256 of input file `7d039a24a6083ed9ef0f806ebad56bbb976e3aeb8de05669173bfdc4996c239d`. Produced by `python tools/real_sms_eval.py`.

Every message is scored as an ordinary local sender (real messages carry no sender ID), so this measures the filter alone, not HISN's essential lane.

| Threshold (event) | Legitimate messages blocked | Spam caught |
|---|---|---|
| 0.5 (default) | 0/4827 = 0.0% (0.0-0.1%) | 1/747 = 0.1% (0.0-0.8%) |
| 0.2 (after the scam wave, A3-E1) | 103/4827 = 2.1% (1.8-2.6%) | 88/747 = 11.8% (9.7-14.3%) |
| 0.15 (after the silent vendor retune, A4-E1) | 103/4827 = 2.1% (1.8-2.6%) | 88/747 = 11.8% (9.7-14.3%) |

Reading: at 0.2 the filter blocks 103 real legitimate messages while catching 88 spam messages. The prototype's scores are discrete (0, 0.25, 0.3, 0.55 and up), so 0.15 and 0.2 behave the same on this data. The prototype filter is a deliberately simple stand-in and catches little real spam; HISN governs whatever filter an operator runs. In an ungoverned filter those blocks are silent. HISN does not make the filter more accurate; it makes sure blocked essential messages are held, routed to a named officer and receipted, and that the threshold change itself needs a signed approval.

Limits: 2011 English SMS from the UK and Singapore, not UAE traffic; no sender IDs, so essential senders cannot be identified in this data.
