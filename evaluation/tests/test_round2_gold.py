from __future__ import annotations

import os
import unittest
from pathlib import Path

from evaluation.round2_gold import cumulative_levels, load_round2_gold_csv, score_round2_gold


class Round2GoldRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gold_path = Path(
            os.environ.get(
                "SKINMINER_ROUND2_GOLD",
                Path(__file__).resolve().parents[1] / "gold" / "gold_set_round2_annotation.csv",
            )
        )
        cls.rows = load_round2_gold_csv(cls.gold_path)

    def test_input_contract(self) -> None:
        self.assertEqual(len(self.rows), 130)
        self.assertEqual(len({row.sample_id for row in self.rows}), 130)
        self.assertEqual(len([row for row in self.rows if row.source_baseline == "gpt"]), 107)

    def test_cumulative_semantics(self) -> None:
        self.assertEqual(cumulative_levels("v1"), ("v1",))
        self.assertEqual(cumulative_levels("v2"), ("v1", "v2"))
        self.assertEqual(cumulative_levels("v4"), ("v1", "v2", "v3", "v4"))

    def _assert_score(self, level: str, expected: tuple[int, ...]) -> None:
        score = score_round2_gold(self.rows, provider="gpt", policy_level=level)
        actual = (
            score.verified,
            score.unresolved,
            score.rejected,
            score.scope_tp,
            score.scope_fp,
            score.scope_value_tp,
        )
        self.assertEqual(actual, expected)

    def test_gpt_v1(self) -> None:
        self._assert_score("v1", (1, 94, 12, 1, 0, 0))
        score = score_round2_gold(self.rows, provider="gpt", policy_level="v1")
        self.assertEqual(score.scope_precision, 1.0)

    def test_gpt_v2_extended(self) -> None:
        self._assert_score("v2", (25, 70, 12, 25, 0, 24))
        score = score_round2_gold(self.rows, provider="gpt", policy_level="v2")
        self.assertEqual(score.scope_precision, 1.0)
        self.assertEqual(score.end_to_end_precision, 0.96)

    def test_gpt_v3(self) -> None:
        self._assert_score("v3", (47, 48, 12, 25, 22, 24))
        score = score_round2_gold(self.rows, provider="gpt", policy_level="v3")
        self.assertAlmostEqual(score.scope_precision * 100, 53.1915, places=4)

    def test_gpt_v4(self) -> None:
        self._assert_score("v4", (51, 44, 12, 25, 26, 24))
        score = score_round2_gold(self.rows, provider="gpt", policy_level="v4")
        self.assertAlmostEqual(score.scope_precision * 100, 49.0196, places=4)
        self.assertEqual(score.unresolved_keep_yes, 0)
        self.assertEqual(score.rejected_keep_no, 12)

    def test_claude_fails_closed_without_provider_aggregate(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be inferred"):
            score_round2_gold(self.rows, provider="claude", policy_level="v2")


if __name__ == "__main__":
    unittest.main()
