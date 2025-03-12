import json
import unittest
from unittest.mock import patch, MagicMock
from src.ai_orchestrator.ai_orchestrator import AIOrchestrator


class TestAIOrchestrator(unittest.TestCase):

    @patch("openai.OpenAI", autospec=True)  # Ensure OpenAI client is properly mocked
    def test_generate_workflow(self, mock_openai_client):
        """Test generating a workflow using mocked OpenAI API."""
        
        # Mock OpenAI Client Instance
        mock_client = MagicMock()
        mock_openai_client.return_value = mock_client

        # Mock OpenAI chat.completions.create response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({"workflow": {}, "missing_modules": []})))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        # Create AIOrchestrator
        orchestrator = AIOrchestrator(openai_api_key="mocked_api_key")
        user_request = "Run RNA-seq analysis"
        workflow = orchestrator.generate_workflow(user_request)

        # Assertions
        expected_output = {"workflow": {}, "missing_modules": []}
        self.assertEqual(workflow, expected_output)

    @patch("openai.OpenAI", autospec=True)
    def test_refine_workflow(self, mock_openai_client):
        """Test refining a workflow using mocked OpenAI API."""
        
        # Mock OpenAI Client Instance
        mock_client = MagicMock()
        mock_openai_client.return_value = mock_client

        # Mock OpenAI chat.completions.create response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({"workflow": {"steps": ["Step1"]}})))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        # Create AIOrchestrator
        orchestrator = AIOrchestrator(openai_api_key="mocked_api_key")
        workflow = {"steps": []}  # Initial empty workflow
        refined_workflow = orchestrator.refine_workflow(workflow)

        # Assertions
        expected_output = {"workflow": {"steps": ["Step1"]}}
        self.assertEqual(refined_workflow, expected_output)


if __name__ == "__main__":
    unittest.main()
