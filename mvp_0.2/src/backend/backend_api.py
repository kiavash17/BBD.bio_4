from flask import Flask, request, jsonify
from ai_orchestrator import AIOrchestrator

app = Flask(__name__)

# Initialize AI Orchestrator
orchestrator = AIOrchestrator("your_openai_api_key", "module_metadata.json")

@app.route('/generate-workflow', methods=['POST'])
def generate_workflow():
    data = request.get_json()
    user_request = data.get('request')
    automation_level = data.get('automation', 50)  # Default to 50% automation
    
    if not user_request:
        return jsonify({"error": "Missing user request"}), 400
    
    workflow = orchestrator.generate_workflow(user_request)
    return jsonify({"workflow": workflow})

@app.route('/execute-workflow', methods=['POST'])
def execute_workflow():
    data = request.get_json()
    workflow = data.get('workflow')
    
    if not workflow:
        return jsonify({"error": "No workflow provided"}), 400
    
    run_id = orchestrator.execute_workflow(workflow)
    return jsonify({"status": f"Run {run_id} completed"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
