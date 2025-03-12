import openai
import json
import os
import requests
import logging
import traceback
from src.run_management.run_executor import execute_run
from src.run_management.run_tracking import log_run
from src.run_management.directory_manager import setup_run_directory, move_input_files
from src.run_management.cli_run_manager import create_run

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", force=True)

MODULE_DATABASE_URL = "https://orange-broccoli-54776gp7wv7379g6-5000.app.github.dev/module-database"


class AIOrchestrator:
    def __init__(self, openai_api_key):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.module_tickets = []  # List to track missing module requests
        self.module_database = self.fetch_module_data()  # Initialize module database
        logging.debug("✅ AIOrchestrator initialized.")

    def fetch_module_data(self):
        """Fetches the available bioinformatics modules from the backend module database."""
        try:
            logging.debug("🔍 Fetching module data from API...")
            response = requests.get(MODULE_DATABASE_URL, timeout=10)

            if response.status_code == 200:
                module_data = response.json()
                logging.debug(f"✅ Successfully fetched module data: {module_data}")
                return {module["name"]: module for module in module_data}  # Store as dict for easy lookup

            logging.error(f"⚠️ Failed to fetch module data: {response.status_code} - {response.text}")
            return {}

        except requests.RequestException as e:
            logging.error(f"🚨 Error fetching module data: {str(e)}")
            return {}

    def generate_workflow(self, user_request):
        """Generates a workflow based on user input, checking available modules dynamically."""
        self.module_database = self.fetch_module_data()  # Ensure the module database is up-to-date
        available_modules = list(self.module_database.keys())

        prompt = f"""
        You are an AI bioinformatics orchestrator. Based on the user's request:
        {user_request}
        Generate a workflow using the best-known bioinformatics tools.
        Use the following available modules: {available_modules}
        If a required module does not exist, note it separately.
        """

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o"
        )

        try:
            workflow_data = json.loads(response.choices[0].message.content)
            workflow = workflow_data.get("workflow", {})
            missing_modules = workflow_data.get("missing_modules", [])

            for module in missing_modules:
                logging.warning(f"⚠️ Missing module detected: {module}")
                self.create_module_ticket(module)

            return {"workflow": workflow, "missing_modules": missing_modules}  # Ensure test compatibility

        except json.JSONDecodeError as e:
            logging.error(f"🚨 Failed to parse AI response: {str(e)}")
            return {"workflow": {}, "missing_modules": []}  # Ensure test compatibility

    def create_module_ticket(self, module_name):
        """Logs a ticket for a missing module and syncs it with the backend database."""
        ticket = {
            "module_name": module_name,
            "reason": "Required for workflow execution",
            "status": "pending"
        }
        self.module_tickets.append(ticket)
        logging.info(f"[TICKET CREATED] Missing Module: {module_name}")

        # Sync with backend
        try:
            response = requests.post(f"{MODULE_DATABASE_URL}/module-tickets", json=ticket, timeout=10)
            if response.status_code == 201:
                logging.debug(f"✅ Module ticket synced successfully: {module_name}")
            else:
                logging.error(f"⚠️ Failed to sync module ticket: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            logging.error(f"🚨 Error syncing module ticket: {str(e)}")

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

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            logging.error(f"🚨 Failed to parse AI response in refine_workflow: {str(e)}")
            return workflow  # Return the original workflow if AI response is invalid

    def execute_workflow(self, workflow, base_path):
        """Executes the workflow step-by-step."""
        input_files = []  # This should come from the user request
        if not workflow.get("steps"):
            logging.error("🚨 No steps found in workflow. Execution aborted.")
            return None

        run_id = log_run(input_files, "")
        run_dir = setup_run_directory(base_path, run_id)
        move_input_files(input_files, os.path.join(run_dir, "input"))

        for step in workflow["steps"]:
            module_name = step.get("module")
            params = step.get("params", {})

            if not module_name:
                logging.warning("⚠️ Skipping step with missing module name.")
                continue

            logging.info(f"🚀 Running {module_name} with params: {params}")
            execute_run(run_id, input_files, os.path.join(run_dir, "output"), os.path.join(run_dir, "logs"))

        logging.info("✅ Workflow execution completed.")
        return run_id

    def interactive_cli(self, base_path):
        """Connects AI Orchestrator with CLI for user interaction."""
        user_request = create_run([], base_path)  # Mock user input
        workflow_result = self.generate_workflow(user_request)
        workflow = workflow_result["workflow"]  # Ensure compatibility with test expectations
        refined_workflow = self.refine_workflow(workflow)
        run_id = self.execute_workflow(refined_workflow, base_path)
        logging.info(f"Run completed with ID: {run_id}")

        if self.module_tickets:
            logging.warning("\n[TICKETS CREATED] The following modules need to be added:")
            for ticket in self.module_tickets:
                logging.warning(f"- {ticket['module_name']} (Status: {ticket['status']})")


# Example Usage:
# orchestrator = AIOrchestrator("your_openai_api_key")
# orchestrator.interactive_cli("/path/to/base")
