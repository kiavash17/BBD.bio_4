import os
import sqlite3
from flask import Flask, request, jsonify
from src.ai_orchestrator import AIOrchestrator
import logging
import traceback

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", force=True)

print("✅ Logging Initialized...")  # Ensure this prints
logging.debug("Backend API is starting...")

app = Flask(__name__)
DB_PATH = "module_database.db"

# Initialize AI Orchestrator
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("🚨 Missing OpenAI API Key! Set it with 'export OPENAI_API_KEY=your_key'")

orchestrator = AIOrchestrator(API_KEY)


def init_db():
    """Initialize the database to store module information and tickets."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT,
                input_format TEXT,
                output_format TEXT,
                environment TEXT  -- Python, R, Shell, Docker, Conda
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS module_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_name TEXT UNIQUE,
                reason TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        conn.commit()


@app.route('/generate-workflow', methods=['POST'])
def generate_workflow():
    data = request.get_json()
    user_request = data.get('request')
    
    if not user_request:
        return jsonify({"error": "Missing user request"}), 400
    
    try:
        workflow = orchestrator.generate_workflow(user_request)
        return jsonify({"workflow": workflow})
    except Exception as e:
        return jsonify({"error": f"Failed to generate workflow: {str(e)}"}), 500


@app.route('/execute-workflow', methods=['POST'])
def execute_workflow():
    data = request.get_json()
    workflow = data.get('workflow')
    base_path = data.get('base_path', "/tmp")  # Default to /tmp if not specified
    
    if not workflow:
        return jsonify({"error": "No workflow provided"}), 400
    
    try:
        run_id = orchestrator.execute_workflow(workflow, base_path)
        return jsonify({"status": f"Run {run_id} completed"})
    except Exception as e:
        return jsonify({"error": f"Workflow execution failed: {str(e)}"}), 500


@app.route('/module-database', methods=['GET', 'POST'])
def module_database():
    """Handle module retrieval (GET) and module addition (POST)."""
    if request.method == 'GET':
        if not orchestrator.module_database:
            try:
                logging.debug("Fetching module data...")
                orchestrator.module_database = orchestrator.fetch_module_data()
            except Exception as e:
                logging.error(f"⚠️ Error fetching module data: {str(e)}")
                traceback.print_exc()  # Prints full stack trace
                orchestrator.module_database = {}  # Prevents further failures
        
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT name, description, input_format, output_format, environment FROM modules")
            modules = [{"name": row[0], "description": row[1], "input_format": row[2], "output_format": row[3], "environment": row[4]} for row in c.fetchall()]
        return jsonify(modules)

    elif request.method == 'POST':
        data = request.get_json()
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO modules (name, description, input_format, output_format, environment) VALUES (?, ?, ?, ?, ?)",
                          (data["name"], data["description"], data["input_format"], data["output_format"], data["environment"]))
                conn.commit()
            return jsonify({"message": "Module added successfully"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Module already exists"}), 400
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route('/module-tickets', methods=['GET', 'POST'])
def module_tickets():
    """Handle module ticket retrieval (GET) and ticket creation (POST)."""
    if request.method == 'GET':
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT module_name, reason, status FROM module_tickets")
            tickets = [{"module_name": row[0], "reason": row[1], "status": row[2]} for row in c.fetchall()]
        return jsonify(tickets)

    elif request.method == 'POST':
        data = request.get_json()
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO module_tickets (module_name, reason, status) VALUES (?, ?, ?)",
                          (data["module_name"], data["reason"], "pending"))
                conn.commit()
            return jsonify({"message": "Module ticket created successfully"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Module ticket already exists"}), 400
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route('/init-db', methods=['POST'])
def initialize_database():
    """Manually initialize the database via API call."""
    try:
        init_db()
        return jsonify({"message": "Database initialized successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Database initialization failed: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
