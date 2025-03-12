import unittest
import requests
import time

BASE_URL = "https://orange-broccoli-54776gp7wv7379g6-5000.app.github.dev"  # Adjust if running in GitHub Codespaces

class BackendAPITestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Runs once before all tests."""
        print("\n🚀 Starting Backend API Tests...")

    def test_generate_workflow(self):
        """Test workflow generation."""
        data = {"request": "Run RNA-seq analysis"}
        response = requests.post(f"{BASE_URL}/generate-workflow", json=data)
        self.assertEqual(response.status_code, 200, f"Failed: {response.json()}")

    def test_generate_workflow_missing_request(self):
        """Test missing request error in workflow generation."""
        data = {}
        response = requests.post(f"{BASE_URL}/generate-workflow", json=data)
        self.assertEqual(response.status_code, 400)
    
    def test_fetch_modules_before_server(self):
        """Test if fetching module data before server starts causes failure."""
        try:
            response = requests.get(f"{BASE_URL}/module-database")
            response.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            print("\n🔥 ERROR: Connection refused when trying to fetch module data before server starts!")
            self.fail(f"Failed with error: {e}")

    def test_add_module(self):
        """Test adding a new module."""
        data = {
            "name": "FastQC",
            "description": "Quality control for high throughput sequence data",
            "input_format": "fastq",
            "output_format": "html, zip",
            "environment": "Python"
        }
        response = requests.post(f"{BASE_URL}/module-database", json=data)
        self.assertIn(response.status_code, [200, 201, 400])  # 400 if module exists

    def test_get_modules(self):
        """Test retrieving available modules."""
        response = requests.get(f"{BASE_URL}/module-database")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list, "Expected list of modules")

    def test_add_duplicate_module(self):
        """Test adding the same module twice (should fail)."""
        data = {
            "name": "FastQC",
            "description": "Quality control for high throughput sequence data",
            "input_format": "fastq",
            "output_format": "html, zip",
            "environment": "Python"
        }
        response = requests.post(f"{BASE_URL}/module-database", json=data)
        self.assertEqual(response.status_code, 400, "Expected 400 for duplicate module")

    def test_add_module_ticket(self):
        """Test adding a missing module ticket."""
        data = {
            "module_name": "CellRanger",
            "reason": "Required for single-cell RNA-seq"
        }
        response = requests.post(f"{BASE_URL}/module-tickets", json=data)
        self.assertIn(response.status_code, [200, 201, 400])  # 400 if ticket exists

    def test_get_module_tickets(self):
        """Test retrieving module tickets."""
        response = requests.get(f"{BASE_URL}/module-tickets")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list, "Expected list of module tickets")

    def test_add_duplicate_module_ticket(self):
        """Test adding a duplicate module ticket (should fail)."""
        data = {
            "module_name": "CellRanger",
            "reason": "Required for single-cell RNA-seq"
        }
        response = requests.post(f"{BASE_URL}/module-tickets", json=data)
        self.assertEqual(response.status_code, 400, "Expected 400 for duplicate module ticket")

if __name__ == "__main__":
    unittest.main()
