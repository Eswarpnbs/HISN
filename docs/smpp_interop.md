# SMPP interoperability check (independent client library)

Client: smpplib (open source, not HISN code). Server: HISN SMPP 3.4 listener. Audit chain verified: True. All outcomes as expected: True. Produced by `python tools/smpp_interop_check.py`. HISN's receipt carries vendor-specific optional parameters (tags 0x1401-0x1404, inside the range SMPP 3.4 reserves for vendors), which smpplib skips as unknown.

| Case | Expected | Outcome via smpplib | Receipt text (start) |
|---|---|---|---|
| Genuine hospital message, authorised account | held + receipt (authenticated) | held + receipt | id:Q1 sub:001 dlvrd:000 submit date:2611090555 done date:2611090555 st |
| Same sender ID from an unauthorised account | held + receipt (NOT authenticated) | held + receipt | id:Q2 sub:001 dlvrd:000 submit date:2611090555 done date:2611090555 st |
| Held message, sender bound as transmitter only | held (receipt not pushed: SMPP 3.4) | held |  |
| Ordinary message, no risk words | delivered | delivered |  |
| Wrong password | bind refused | bind refused (PDUError) |  |
