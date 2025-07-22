import unittest
import json
import os
from scorer.pipeline import generate_ml_scores

class TestScoringPipeline(unittest.TestCase):

    def setUp(self):
        """Create a temporary transactions file for testing."""
        self.test_file_path = 'test_transactions.json'
        self.test_data = {
            # Reliable wallet: Borrows and repays fully
            "reliable_wallet": [
                {"timestamp": "2023-01-15T10:00:00Z", "action_type": "deposit", "amount_usd": 10000},
                {"timestamp": "2023-02-01T12:00:00Z", "action_type": "borrow", "amount_usd": 2000},
                {"timestamp": "2023-03-01T14:00:00Z", "action_type": "repay", "amount_usd": 2000}
            ],
            # Risky wallet: Gets liquidated
            "risky_wallet": [
                {"timestamp": "2023-05-10T09:00:00Z", "action_type": "deposit", "amount_usd": 5000},
                {"timestamp": "2023-05-11T11:00:00Z", "action_type": "borrow", "amount_usd": 4500},
                {"timestamp": "2023-06-01T18:00:00Z", "action_type": "liquidationcall"}
            ],
            # Safe wallet: Only deposits, no credit history
            "no_borrow_wallet": [
                {"timestamp": "2024-01-01T08:00:00Z", "action_type": "deposit", "amount_usd": 1000}
            ],
            # Another reliable wallet to ensure model can train
             "another_reliable_wallet": [
                {"timestamp": "2023-01-15T10:00:00Z", "action_type": "deposit", "amount_usd": 20000},
                {"timestamp": "2023-02-01T12:00:00Z", "action_type": "borrow", "amount_usd": 5000},
                {"timestamp": "2023-03-01T14:00:00Z", "action_type": "repay", "amount_usd": 5000}
            ]
        }
        with open(self.test_file_path, 'w') as f:
            json.dump(self.test_data, f)

    def tearDown(self):
        """Remove the temporary file after tests are run."""
        os.remove(self.test_file_path)

    def test_score_generation_logic(self):
        """
        Tests the overall logic of the scoring pipeline:
        1. Scores are within the 0-1000 range.
        2. A non-borrower gets the default score.
        3. A reliable wallet scores higher than a risky one.
        """
        scores = generate_ml_scores(self.test_file_path)

        # Test that all scores are valid
        for wallet, score in scores.items():
            self.assertTrue(0 <= score <= 1000, f"Score for {wallet} is out of bounds: {score}")

        # Test the non-borrower default score
        self.assertEqual(scores['no_borrow_wallet'], 750)

        # Test the relative scoring logic
        self.assertGreater(scores['reliable_wallet'], scores['risky_wallet'])

if __name__ == '__main__':
    unittest.main()