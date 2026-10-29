"""Minimal reader for an HL7 FHIR R4 CommunicationRequest. Reads only the metadata HISN needs.
Message content is returned separately and is never stored. Authentication comes from the
transport (the bound SMPP account), never from the FHIR resource itself."""
PRIORITIES = {"routine", "urgent", "asap", "stat"}

def from_communication_request(res, authenticated):
    if res.get("resourceType") != "CommunicationRequest":
        raise ValueError("not a CommunicationRequest")
    pr = res.get("priority")
    if pr is not None and pr not in PRIORITIES:
        raise ValueError(f"invalid FHIR priority: {pr}")
    sender = (res.get("sender") or {}).get("reference")
    if not sender:
        raise ValueError("sender.reference is required")
    cats = [c.get("code") for cat in res.get("category", []) for c in cat.get("coding", [])]
    text = " ".join(p.get("contentString", "") for p in res.get("payload", []))
    meta = {"sender": sender, "priority": pr, "category": cats, "authenticated": bool(authenticated)}
    return meta, text