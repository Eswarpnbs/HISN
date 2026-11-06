"""Regression tests for the evidence gate and deterministic policy controls."""
import tempfile
import unittest
from pathlib import Path

import yaml

from app.core.coordinator import Coordinator
from app.core.gateway import PolicyGateway
from app.core.events import Event
from app.agents.institution import InstitutionalAgent


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

    def _agent_proposal(self, verbatim):
        audit = AuditStub()
        evidence = [{
            "id": "UAE-FL-2-2019-ART13", "similarity": 0.95,
            "basis": "FEDERAL_LAW", "record_id": "UAE-FL-2-2019",
            "article": "Article (13)", "text": "Exact retrieved clause text",
            "verbatim": verbatim,
        }]
        agent = InstitutionalAgent(
            "health_authority",
            retriever=lambda query: evidence,
            llm=lambda system, user: {
                "proposed_action": "RECOMMEND_RELEASE_BY_NAMED_OFFICER",
                "cited_ids": ["UAE-FL-2-2019-ART13"],
                "assessment": "Evidence supports human review.",
                "missing_provision": None, "uncertainty": "medium",
                "scam_likelihood": "medium",
            },
            audit=audit,
        )
        event = Event("HEALTH-ESC", 0, "escalation", ("health_authority",), {})
        return agent.handle(event, {"action": "ESCALATED"}, 0)

    def test_decisive_agent_proposal_requires_verbatim_clause(self):
        result = self._agent_proposal(verbatim=False)
        self.assertEqual(result["status"], "POTENTIAL_GAP")
        self.assertEqual(result["proposed_action"], "LOG_GAP")
        self.assertEqual(result["reason"], "no_competent_binding_basis")

    def test_verbatim_binding_clause_can_ground_agent_proposal(self):
        result = self._agent_proposal(verbatim=True)
        self.assertEqual(result["status"], "PROPOSED")
        self.assertEqual(result["proposed_action"], "RECOMMEND_RELEASE_BY_NAMED_OFFICER")

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

    def test_gateway_rejects_rule_basis_mismatch(self):
        with open("kb/rulepacks/uae/rules.yaml", encoding="utf-8") as f:
            pack = yaml.safe_load(f)
        pack["rules"][0]["basis"] = "SOFT_LAW"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rules.yaml"
            path.write_text(yaml.safe_dump(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "rule_basis_does_not_match"):
                PolicyGateway(str(path), AuditStub())

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
