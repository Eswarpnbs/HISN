import csv
import re

import yaml
from .enums import Verdict, Action, Basis, BLOCKING_BASES


def _plain(d):
    return {k: (v.value if hasattr(v, "value") else v) for k, v in d.items()}


def _norm_text(value):
    value = str(value or "").replace("\u2018", "'").replace("\u2019", "'")
    value = value.replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", value).strip()


class PolicyGateway:
    """Deterministic policy node. Every rule citation resolves to a manifest-pinned KB clause."""

    def __init__(self, pack_path, audit, clauses_path="kb/clauses/clauses.yaml",
                 manifest_path="kb/manifest.csv"):
        with open(pack_path, encoding="utf-8") as f:
            self.pack = yaml.safe_load(f)
        self.audit = audit
        with open(clauses_path, encoding="utf-8") as f:
            clauses = yaml.safe_load(f) or []
        with open(manifest_path, newline="", encoding="utf-8") as f:
            manifest = {r["record_id"]: r for r in csv.DictReader(f)}
        self._validate_pack(clauses, manifest)

    def _validate_pack(self, clauses, manifest):
        by_id = {c.get("clause_id"): c for c in clauses}
        for rule in self.pack.get("rules", []):
            citation = rule.get("citation") or {}
            clause_id = citation.get("clause_id")
            clause = by_id.get(clause_id)
            record_id = citation.get("record_id")
            source = manifest.get(record_id)
            errors = []
            if not clause_id or clause is None:
                errors.append("unknown_or_missing_clause_id")
            if not source:
                errors.append("source_record_missing_from_manifest")
            elif not re.fullmatch(r"[0-9a-fA-F]{64}", str(source.get("sha256", ""))):
                errors.append("source_record_hash_missing_or_invalid")
            elif source.get("status") != "in_force":
                errors.append("source_record_not_marked_in_force")
            if source and source.get("basis") != rule.get("basis"):
                errors.append("rule_basis_does_not_match_manifest")
            if clause is not None:
                if clause.get("record_id") != record_id:
                    errors.append("citation_record_id_mismatch")
                if clause.get("basis") != rule.get("basis"):
                    errors.append("rule_basis_does_not_match_clause")
                if _norm_text(clause.get("article")) != _norm_text(citation.get("article")):
                    errors.append("citation_article_mismatch")
                if _norm_text(clause.get("text")) != _norm_text(citation.get("quote")):
                    errors.append("citation_quote_not_exact_clause_text")
            if errors:
                raise ValueError(f"Rule {rule.get('id', '<unnamed>')} has an ungrounded citation: {', '.join(errors)}")
            rule["citation"]["source_sha256"] = source["sha256"]

    def _matches(self, cond, event):
        for k, v in cond.items():
            if k.endswith("_not"):
                if event.get(k[:-4]) == v:
                    return False
            elif k.endswith("_max"):
                val = event.get(k[:-4])
                if val is None or val > v:
                    return False
            elif event.get(k) != v:
                return False
        return True

    def evaluate(self, event: dict) -> dict:
        for rule in self.pack["rules"]:
            if event.get("type") not in rule["applies_to"]:
                continue
            if not self._matches(rule["condition"], event):
                continue
            basis = Basis(rule["basis"])
            decision = {"verdict": Verdict(rule["verdict"]), "action": Action(rule["action"])}
            if basis not in BLOCKING_BASES:
                decision = {"verdict": Verdict.INSUFFICIENT_EVIDENCE,
                            "action": Action.QUARANTINE,
                            "reason": "non-binding basis cannot compel a blocking decision"}
            decision.update(rule_id=rule["id"], citation=rule["citation"],
                            pack=self.pack["pack_id"])
            self.audit.write({"kind": "gateway_decision", "event": event, **_plain(decision)})
            return decision
        decision = {"verdict": Verdict.POTENTIAL_GAP, "action": Action.FLAG,
                    "reason": "no rule covers this event", "pack": self.pack["pack_id"]}
        self.audit.write({"kind": "gap_candidate", "event": event, **_plain(decision)})
        return decision
