"""Signed approval records for consequential changes (maker-checker; ITU-T Y.3173 demand mapping = Human).

A name string is not an approval. An approval is a record that:
  * names an approver listed in kb/approvers.yaml, whose role may approve this kind of change;
  * is bound to one change (event id, kind and the exact new value), so it cannot be reused or altered;
  * has a validity window (simulated minutes) and expires;
  * comes from someone other than the person who requested the change (maker != checker);
  * carries an HMAC-SHA256 signature over a canonical form of all of the above.

DEMO KEYS: keys are derived from the approver id unless HISN_KEY_<APPROVER_ID> is set in the environment.
They are not secret and exist only so the prototype can show the verification boundary. A production
deployment would use the authority's own PKI or identity service; HISN does not claim that integration.
"""
import hashlib, hmac, json, os
from pathlib import Path
import yaml

ROSTER_PATH = "kb/approvers.yaml"
FIELDS = ("change_id", "kind", "value", "approver_id", "role", "requested_by", "issued_at", "expires_at")

def load_roster(path=ROSTER_PATH):
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return {a["id"]: a for a in data["approvers"]}

def _key(approver_id):
    env = os.environ.get("HISN_KEY_" + approver_id.upper().replace("-", "_"))
    return (env or ("hisn-demo-key:" + approver_id)).encode()

def canonical(rec):
    return json.dumps({k: rec.get(k) for k in FIELDS}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sign(rec):
    out = dict(rec)
    out["signature"] = hmac.new(_key(rec["approver_id"]), canonical(rec).encode(), hashlib.sha256).hexdigest()
    return out

def make_approval(change_id, kind, value, approver_id, requested_by, issued_at, valid_minutes=60, roster=None):
    roster = roster or load_roster()
    role = roster[approver_id]["role"] if approver_id in roster else "unknown"
    return sign({"change_id": change_id, "kind": kind, "value": value, "approver_id": approver_id, "role": role,
                 "requested_by": requested_by, "issued_at": issued_at, "expires_at": issued_at + valid_minutes})

def verify(approval, change_id, kind, value, now, roster=None):
    """Return (ok, reason). Every failure has a specific reason, written to the audit log by the caller."""
    if not isinstance(approval, dict):
        return False, "no_signed_approval_record"
    roster = roster or load_roster()
    aid = approval.get("approver_id")
    if aid not in roster:
        return False, "approver_not_in_roster"
    expected = hmac.new(_key(aid), canonical(approval).encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, str(approval.get("signature", ""))):
        return False, "signature_invalid"
    who = roster[aid]
    if approval.get("role") != who["role"]:
        return False, "role_mismatch"
    if kind not in who.get("may_approve", []):
        return False, "role_not_competent_for_change"
    if approval.get("change_id") != change_id or approval.get("kind") != kind:
        return False, "approval_bound_to_another_change"
    if approval.get("value") != value:
        return False, "approved_value_differs_from_change"
    if approval.get("requested_by") in (None, "", aid):
        return False, "maker_and_checker_are_the_same"
    if not (approval.get("issued_at", 1e18) <= now <= approval.get("expires_at", -1)):
        return False, "approval_expired_or_not_yet_valid"
    return True, "approved"
