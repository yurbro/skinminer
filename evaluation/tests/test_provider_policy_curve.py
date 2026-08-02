from __future__ import annotations

import os
import unittest
from pathlib import Path

from evaluation.provider_policy_audit import load_provider_policy_score


class ProviderPolicyAggregateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.metrics = Path(
            os.environ.get(
                "SKINMINER_PROVIDER_METRICS",
                Path(__file__).resolve().parents[1] / "data" / "provider_policy_reference.csv",
            )
        )

    def test_claude_extended(self) -> None:
        score = load_provider_policy_score(self.metrics, provider="claude", policy_level="v2")
        self.assertEqual((score.verified, score.scope_tp, score.scope_fp), (24, 24, 0))
        self.assertEqual(score.scope_precision, 1.0)

    def test_claude_strict_precision_is_undefined(self) -> None:
        score = load_provider_policy_score(self.metrics, provider="claude", policy_level="v1")
        self.assertEqual(score.verified, 0)
        self.assertIsNone(score.scope_precision)


if __name__ == "__main__":
    unittest.main()
