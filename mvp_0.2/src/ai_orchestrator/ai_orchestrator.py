import openai
import json
import os
import logging
import subprocess
import requests
from src.run_management.run_executor import execute_run
from src.run_management.run_tracking import log_run
from src.run_management.directory_manager import setup_run_directory, move_input_files
from src.run_management.cli_run_manager import create_run

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", force=True)

MODULE_DATABASE_URL = "https://orange-broccoli-54776gp7wv7379g6-5000.app.github.dev/module-database"

class AIOrchestrator:
    def __init__(self, openai_api_key):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.module_database = self.fetch_module_data()
        self.module_tickets = []
        logging.debug("✅ AIOrchestrator initialized.")

    def fetch_module_data(self):
        try:
            response = requests.get(MODULE_DATABASE_URL, timeout=10)
            if response.status_code == 200:
                module_data = response.json()
                return {module["name"]: module for module in module_data}
        except requests.RequestException as e:
            logging.error(f"🚨 Error fetching module data: {str(e)}")
            return {}

    def fetch_module_tickets(self):
        try:
            response = requests.get(f"{MODULE_DATABASE_URL}/module-tickets", timeout=10)
            if response.status_code == 200:
                return [ticket["module_name"] for ticket in response.json()]
            else:
                logging.error(f"⚠️ Failed to fetch module tickets: {response.status_code} - {response.text}")
                return []
        except requests.RequestException as e:
            logging.error(f"🚨 Error fetching module tickets: {str(e)}")
            return []

    def create_module_ticket(self, module_name):
        ticket = {
            "module_name": module_name,
            "reason": "Required for workflow execution",
            "status": "pending"
        }
        self.module_tickets.append(ticket)
        logging.info(f"[TICKET CREATED] Missing Module: {module_name}")

        try:
            response = requests.post(f"{MODULE_DATABASE_URL}/module-tickets", json=ticket, timeout=10)
            if response.status_code == 201:
                logging.debug(f"✅ Module ticket synced successfully: {module_name}")
            else:
                logging.error(f"⚠️ Failed to sync module ticket: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            logging.error(f"🚨 Error syncing module ticket: {str(e)}")

    def generate_workflow(self, user_request):
        self.module_database = self.fetch_module_data()
        available_modules = list(self.module_database.keys())
        existing_tickets = self.fetch_module_tickets()

        prompt = f"""
        You are an AI bioinformatics orchestrator. Based on the user's request:
        {user_request}
        Generate a workflow using the best-known bioinformatics tools.
        Use the following available modules: {available_modules} or pending modules: {existing_tickets}.

        If a required module does not exist include it in the 'missing_modules' list.

        Return the output **strictly as a JSON object** with keys 'workflow' and 'missing_modules'.
        """
        logging.debug(f"🔍 kk: full prompt was: {prompt}")

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o"
        )

        try:
            raw_response = response.choices[0].message.content.strip()
            logging.debug(f"🔍 AI Raw Response: {raw_response}")
            if raw_response.startswith("```json") and raw_response.endswith("```"):
                raw_response = raw_response[7:-3].strip()
            try:
                workflow_data = json.loads(raw_response)
            except json.JSONDecodeError as e:
                logging.error(f"🚨 JSON Parsing Error: {e}")
                return {"error": "AI response was not valid JSON.", "raw_response": raw_response}
            workflow = workflow_data.get("workflow", {})
            missing_modules = workflow_data.get("missing_modules", [])
            logging.debug(f"🔍 existing tickets were: {existing_tickets}")
            logging.debug(f"🔍 AI returned missing modules as: {missing_modules}")

            for module in missing_modules:
                logging.warning(f"⚠️ Missing module detected: {module}")
                self.create_module_ticket(module)

            return {"workflow": workflow, "missing_modules": missing_modules}

        except json.JSONDecodeError as e:
            logging.error(f"🚨 Failed to parse AI response: {str(e)}")
            return {"workflow": {}, "missing_modules": []}

    def refine_workflow(self, workflow):
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
            return workflow

    def execute_workflow(self, workflow, base_path):
        input_files = []
        if not workflow:
            logging.error("🚨 No steps found in workflow. Execution aborted.")
            return None

        run_id = log_run(input_files, "")
        run_dir = setup_run_directory(base_path, run_id)
        move_input_files(input_files, os.path.join(run_dir, "input"))

        for step in workflow:
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
        user_request = create_run([], base_path)
        workflow_result = self.generate_workflow(user_request)
        workflow = workflow_result["workflow"]
        refined_workflow = self.refine_workflow(workflow)
        run_id = self.execute_workflow(refined_workflow, base_path)
        logging.info(f"Run completed with ID: {run_id}")

        if self.module_tickets:
            logging.warning("\n[TICKETS CREATED] The following modules need to be added:")
            for ticket in self.module_tickets:
                logging.warning(f"- {ticket['module_name']} (Status: {ticket['status']})")

    def generate_snakemake_workflow(self, workflow):
        self.module_database = self.fetch_module_data()
        workflow_prompt = self.format_prompt(workflow)

        response = self.client.chat.completions.create(
            messages=[{"role": "system", "content": "You are an expert in bioinformatics workflow automation."},
                      {"role": "user", "content": workflow_prompt}],
            model="gpt-4o"
        )

        snakemake_script = response.choices[0].message.content.strip()
        self.save_snakemake_script(snakemake_script)
        return snakemake_script

    def format_prompt(self, workflow):
        module_info = {step["tool"]: self.module_database.get(step["tool"], {}) for step in workflow}

        prompt = ("Given the following bioinformatics workflow steps and their required tools, generate a valid "
                  "Snakemake workflow ensuring correct dependencies and module connections."
                  "\n\nWorkflow Steps:\n")

        for step in workflow:
            tool = step["tool"]
            inputs = module_info[tool].get("inputs", "Unknown")
            outputs = module_info[tool].get("outputs", "Unknown")
            prompt += f"- Step: {step['step']}\n  Tool: {tool}\n  Inputs: {inputs}\n  Outputs: {outputs}\n\n"

        prompt += "\nEnsure that each step's outputs correctly connect to the inputs of the next step. Return only a valid Snakefile script."
        return prompt

    def save_snakemake_script(self, script):
        snakefile_path = "./Snakefile"
        with open(snakefile_path, "w") as f:
            f.write(script)
        logging.debug("✅ Snakemake workflow saved.")

    def execute_snakemake(self):
        try:
            subprocess.run(["snakemake", "--cores", "all", "--dry-run"], check=True)
            logging.debug("✅ Snakemake dry-run successful. Proceeding to execution...")
            subprocess.run(["snakemake", "--cores", "all"], check=True)
            logging.debug("✅ Snakemake workflow executed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"🚨 Snakemake execution failed: {str(e)}")
