import json
import os
import unittest
from unittest.mock import Mock, patch

from google.genai._interactions_errors import InternalServerError
from pydantic import ValidationError

from backend.services.answer_evaluator import (
    AnswerEvaluation,
    EvaluationConfigurationError,
    EvaluationProviderError,
    evaluate_answer,
)


class AnswerEvaluationTests(unittest.TestCase):
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True)
    @patch("backend.services.answer_evaluator.genai.Client")
    def test_evaluate_answer_returns_structured_scores(self, client_factory):
        interaction = Mock()
        interaction.output_text = json.dumps(
            {
                "correctness_score": 5,
                "completeness_score": 4,
                "relevance_score": 4,
                "clarity_score": 3,
                "technical_terminology_score": 4,
                "feedback": "Good explanation.",
                "strengths": ["Correct distinction"],
                "improvements": ["Add an example"],
            }
        )
        client_factory.return_value.interactions.create.return_value = interaction

        result = evaluate_answer(
            question="What is a Python list?",
            competency="Python basics",
            reference_answer="A list is mutable.",
            candidate_answer="A list can be changed.",
        )

        self.assertEqual(result.correctness_score, 5)
        self.assertEqual(result.as_result()["overall_score"], 80)
        client_factory.return_value.interactions.create.assert_called_once()
        self.assertFalse(
            client_factory.return_value.interactions.create.call_args.kwargs["store"]
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key_is_reported(self):
        with self.assertRaises(EvaluationConfigurationError):
            evaluate_answer("Question", None, None, "Answer")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True)
    @patch("backend.services.answer_evaluator.genai.Client")
    def test_interactions_api_errors_are_reported_as_provider_errors(
        self, client_factory
    ):
        response = Mock(status_code=503, request=Mock())
        error = InternalServerError(
            "Gemini is temporarily unavailable.",
            response=response,
            body={"error": {"code": "service_unavailable"}},
        )
        client_factory.return_value.interactions.create.side_effect = error

        with self.assertRaises(EvaluationProviderError):
            evaluate_answer("Question", None, None, "Answer")

    def test_scores_outside_rubric_are_rejected(self):
        with self.assertRaises(ValidationError):
            AnswerEvaluation(
                correctness_score=6,
                completeness_score=3,
                relevance_score=3,
                clarity_score=3,
                technical_terminology_score=3,
                feedback="Feedback",
                strengths=[],
                improvements=[],
            )


if __name__ == "__main__":
    unittest.main()
