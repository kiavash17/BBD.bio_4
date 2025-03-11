import openai
import json
import os
from src.run_management.run_executor import RunExecutor
from src.run_management.run_tracking import RunTracker
from src.run_management.cli_run_manager import CLIRunManager

class AIOrchestrator:
    def __init__(self, openai_api_key, module_metadata_path):
        self.client = openai.Client(api_key=openai_api_key)
        self.module_metadata_path = module_metadata_path
        self.executor = RunExecutor()
        self.tracker = RunTracker()
        self.cli_manager = CLIRunManager()
        self.load_modules()

    def load_modules(self):
        with open(self.module_metadata_path, 'r') as f:
            self.modules = json.load(f)

    def generate_workflow(self, user_request):
        """Uses AI to generate a workflow based on user input."""
        prompt = f"""
        You are an AI bioinformatics orchestrator. Based on the user's request:
        {user_request}
        Generate a workflow using the available modules: {list(self.modules.keys())}.
        """
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o"
        )
        
        workflow = response.choices[0].message["content"]
        return json.loads(workflow)  # Expected to be JSON formatted

    def refine_workflow(self, workflow):
        """Asks user for refinements before executing the workflow."""
        prompt = f"""
        Here is the generated workflow:
        {json.dumps(workflow, indent=2)}
        Would you like to modify any steps? Change parameters? Let me know.
        """
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o"
        )
        
        return json.loads(response.choices[0].message["content"])

    def execute_workflow(self, workflow):
        """Executes the workflow step-by-step."""
        run_id = self.tracker.create_run(workflow)
        
        for step in workflow.get("steps", []):
            module_name = step["module"]
            params = step.get("params", {})
            print(f"Running {module_name} with params: {params}")
            self.executor.run_module(module_name, params)
            self.tracker.log_step(run_id, module_name, params)

        print("Workflow completed.")
        return run_id

    def interactive_cli(self):
        """Connects AI Orchestrator with CLI for user interaction."""
        user_request = self.cli_manager.get_user_request()
        workflow = self.generate_workflow(user_request)
        refined_workflow = self.refine_workflow(workflow)
        run_id = self.execute_workflow(refined_workflow)
        print(f"Run completed with ID: {run_id}")

# Example Usage:
# orchestrator = AIOrchestrator("your_openai_api_key", "module_metadata.json")
# orchestrator.interactive_cli()
