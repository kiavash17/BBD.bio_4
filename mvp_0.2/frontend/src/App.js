import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [userRequest, setUserRequest] = useState('');
  const [workflow, setWorkflow] = useState(null);
  const [runStatus, setRunStatus] = useState(null);
  const [automationLevel, setAutomationLevel] = useState(50);

  const handleGenerateWorkflow = async () => {
    if (!userRequest) {
      alert('Please enter a request for the AI Orchestrator.');
      return;
    }

    try {
      const res = await axios.post('https://your-backend-api.com/generate-workflow', { request: userRequest, automation: automationLevel });
      setWorkflow(res.data.workflow);
    } catch (error) {
      console.error('Error generating workflow:', error);
    }
  };

  const handleExecuteWorkflow = async () => {
    if (!workflow) {
      alert('Please generate a workflow first.');
      return;
    }

    try {
      const res = await axios.post('https://your-backend-api.com/execute-workflow', { workflow });
      setRunStatus(res.data.status);
    } catch (error) {
      console.error('Error executing workflow:', error);
    }
  };

  return (
    <div className="app-container">
      <div className="card">
        <h1 className="title">AI Orchestrator</h1>

        {/* User Input Section */}
        <textarea
          value={userRequest}
          onChange={(e) => setUserRequest(e.target.value)}
          placeholder="Describe your analysis workflow..."
          rows="3"
          className="chat-input"
        />
        
        <button onClick={handleGenerateWorkflow} className="action-button">Generate Workflow</button>

        {/* Automation-Control Slider */}
        <div className="slider-container">
          <label>Automation Level:</label>
          <input
            type="range"
            min="0"
            max="100"
            value={automationLevel}
            onChange={(e) => setAutomationLevel(e.target.value)}
          />
          <span>{automationLevel}%</span>
        </div>

        {/* Workflow Preview */}
        {workflow && (
          <div className="workflow-preview">
            <h3>Generated Workflow:</h3>
            <pre>{JSON.stringify(workflow, null, 2)}</pre>
            <button onClick={handleExecuteWorkflow} className="action-button">Execute Workflow</button>
          </div>
        )}

        {/* Run Status */}
        {runStatus && (
          <div className="run-status">
            <h3>Run Status:</h3>
            <p>{runStatus}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
