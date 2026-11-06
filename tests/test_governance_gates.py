"""Regression tests for the evidence gate and deterministic policy controls."""
import tempfile
import unittest
from pathlib import Path

import yaml

from app.core.coordinator import Coordinator
from app.core.gateway import PolicyGateway


class AuditStub:
    def __init__(self):
        self.records = []

    def write(self, record):
        self.records.append(record)
        return "test-hash"


class FirewallStub:
    def __init__(self):
        self.threshold = 0.5
        self.changes = []

    def set_threshold(self, value, reason=""):
        self.changes.append((value, reason))
        self.threshold = value


class GovernanceGateTests(unittest.TestCase):
    def _coordinator(self, payload, verifier=None, enforce_levels=True):
        with tempfile.TemporaryDirectory() as tmp:
            scenario = Path(tmp) / "scenario.yaml"
            scenario.write_text(yaml.safe_dump({
                "name": "policy gate test",
                "duration": 0,
                "events": [{
                    "id": "FILTER-1", "t": 0, "kind": "filter_policy",
                    "audience": ["filter_ai"], "payload": payload,
                }],
            }), encoding="utf-8")
            audit, firewall = AuditStub(), FirewallStub()
            coordinator = Coordinator(
                str(scenario), audit, firewall, enforce_levels=enforce_levels,
                approval_verifier=verifier,
            )
            outcomes = coordinator.run()
            return outcomes, audit, firewall

    def test_unapproved_threshold_change_fails_closed_by_default(self):
        outcomes, audit, firewall = self._coordinator({"threshold": 0.2, "reason": "test"})
        self.assertEqual(outcomes[0]["action"], "HELD_FOR_APPROVAL")
        self.assertEqual(firewall.threshold, 0.5)
        self.assertEqual(firewall.changes, [])
        self.assertTrue(any(r["kind"] == "automation_level_violation" for r in audit.records))

    def test_legacy_approved_by_string_is_not_authorization(self):
        outcomes, _, firewall = self._coordinator({
            "threshold": 0.2, "approved_by": "Someone", "reason": "spoof test",
        })
        self.assertEqual(outcomes[0]["action"], "HELD_FOR_APPROVAL")
        self.assertEqual(firewall.threshold, 0.5)

    def test_verified_approval_allows_change(self):
        verifier = lambda approval, event: (
            approval.get("officer") == "authorized-officer"
            and approval.get("signature") == "test-signature"
            and event.id == "FILTER-1"
        )
        outcomes, _, firewall = self._coordinator({
            "threshold": 0.2, "reason": "approved test",
            "approval": {"officer": "authorized-officer", "signature": "test-signature"},
        }, verifier=verifier)
        self.assertEqual(outcomes[0]["action"], "APPLIED")
        self.assertEqual(firewall.threshold, 0.2)

    def test_verifier_error_fails_closed(self):
        def broken_verifier(approval, event):
            raise RuntimeError("identity service unavailable")

        outcomes, audit, firewall = self._coordinator({
            "threshold": 0.2, "approval": {"officer": "someone"},
        }, verifier=broken_verifier)
        self.assertEqual(outcomes[0]["action"], "HELD_FOR_APPROVAL")
        self.assertEqual(firewall.threshold, 0.5)
        self.assertTrue(any(r["kind"] == "approval_verification_error" for r in audit.records))

    def test_gateway_accepts_exact_clause_and_manifest_reference(self):
        gateway = PolicyGateway("kb/rulepacks/uae/rules.yaml", AuditStub())
        citation = gateway.pack["rules"][0]["citation"]
        self.assertEqual(citation["clause_id"], "UAE-FL-2-2019-ART13")
        self.assertEqual(len(citation["source_sha256"]), 64)
        decision = gateway.evaluate({
            "type": "message_log_transfer", "data_class": "health",
            "destination_country": "XX",
        })
        self.assertEqual(decision["action"].value, "BLOCK_PROHIBITED")
        self.assertEqual(decision["verdict"].value, "VIOLATION")

    def test_gateway_rejects_modified_rule_quote(self):
        with open("kb/rulepacks/uae/rules.yaml", encoding="utf-8") as f:
            pack = yaml.safe_load(f)
        pack["rules"][0]["citation"]["quote"] += " altered"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rules.yaml"
            path.write_text(yaml.safe_dump(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "citation_quote_not_exact_clause_text"):
                PolicyGateway(str(path), AuditStub())


if __name__ == "__main__":
    unittest.main()
