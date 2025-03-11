import unittest
from unittest.mock import patch, MagicMock
import json
from src.run_management.run_executor import RunExecutor
from src.run_management.run_tracking import RunTracker
from src.run_management.cli_run_manager import CLIRunManager
from ai_orchestrator import AIOrchestrator

class TestAIOrchestrator(unittest.TestCase):
    
    def setUp(self):
        self.mock_openai_client = MagicMock()
        self.mock_executor = MagicMock(spec=RunExecutor)
        self.mock_tracker = MagicMock(spec=RunTracker)
        self.mock_cli_manager = MagicMock(spec=CLIRunManager)
        
        self.orchestrator = AIOrchestrator("fake_api_key", "module_metadata.json")
        self.orchestrator.client = self.mock_openai_client
        self.orchestrator.executor = self.mock_executor
        self.orchestrator.tracker = self.mock_tracker
        self.orchestrator.cli_manager = self.mock_cli_manager

    @patch("builtins.open", create=True)
    @patch("json.load")
    def test_load_modules(self, mock_json_load, mock_open):
        mock_json_load.return_value = {"FastQC": {}, "DESeq2": {}}
        self.orchestrator.load_modules()
        self.assertEqual(self.orchestrator.modules, {"FastQC": {}, "DESeq2": {}})

    @patch("openai.Client.chat.completions.create")
    def test_generate_workflow(self, mock_openai_response):
        mock_openai_response.return_value = MagicMock(choices=[MagicMock(message={"content": json.dumps({"steps": [{"module": "FastQC", "params": {}}]})})])
        user_request = "Run FastQC and DESeq2"
        workflow = self.orchestrator.generate_workflow(user_request)
        self.assertIn("steps", workflow)
        self.assertEqual(workflow["steps"][0]["module"], "FastQC")

    @patch("openai.Client.chat.completions.create")
    def test_refine_workflow(self, mock_openai_response):
        initial_workflow = {"steps": [{"module": "FastQC", "params": {}}]}
        refined_workflow = {"steps": [{"module": "FastQC", "params": {"threads": 4}}]}
        mock_openai_response.return_value = MagicMock(choices=[MagicMock(message={"content": json.dumps(refined_workflow)})])
        
        refined_result = self.orchestrator.refine_workflow(initial_workflow)
        self.assertEqual(refined_result["steps"][0]["params"], {"threads": 4})

    def test_execute_workflow(self):
        workflow = {"steps": [{"module": "FastQC", "params": {}}]}
        self.mock_tracker.create_run.return_value = "run_1234"
        run_id = self.orchestrator.execute_workflow(workflow)
        self.mock_executor.run_module.assert_called_once_with("FastQC", {})
        self.mock_tracker.log_step.assert_called_once_with("run_1234", "FastQC", {})
        self.assertEqual(run_id, "run_1234")

    @patch("ai_orchestrator.AIOrchestrator.generate_workflow")
    @patch("ai_orchestrator.AIOrchestrator.refine_workflow")
    @patch("ai_orchestrator.AIOrchestrator.execute_workflow")
    def test_interactive_cli(self, mock_execute, mock_refine, mock_generate):
        mock_generate.return_value = {"steps": [{"module": "FastQC", "params": {}}]}
        mock_refine.return_value = {"steps": [{"module": "FastQC", "params": {"threads": 4}}]}
        mock_execute.return_value = "run_1234"
        
        self.mock_cli_manager.get_user_request.return_value = "Run FastQC"
        self.orchestrator.interactive_cli()
        
        mock_generate.assert_called_once()
        mock_refine.assert_called_once()
        mock_execute.assert_called_once()

if __name__ == "__main__":
    unittest.main()
