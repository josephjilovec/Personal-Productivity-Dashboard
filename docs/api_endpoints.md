QuantumFlow Toolkit REST API Endpoints
This document details the REST API endpoints provided by the QuantumFlow Toolkit for managing workflows, monitoring performance, and interacting with quantum backends. The API is built using FastAPI and integrates with the Python workflow engine, Rust scheduler, and quantum backends. All endpoints are prefixed with /api.
Overview
The API supports operations for defining and executing hybrid quantum-classical workflows, retrieving workflow status, and accessing performance metrics. It uses JSON for request and response bodies and follows standard HTTP status codes for success and error conditions.
Endpoints
1. Workflow Management
Create Workflow

URL: /api/workflows
Method: POST
Description: Defines a new hybrid workflow and saves it to the SQLite database.
Parameters (JSON body):
name (string, required): Name of the workflow.
tasks (array of objects, required): List of tasks, each with:
type (string, required): Either classical or quantum.
config (object, required): Task configuration (e.g., operation for classical, circuit/shots/backend for quantum).




Response:
Success (200 OK):{
  "workflow_id": 1,
  "name": "Test Workflow",
  "status": "pending"
}


Error (400 Bad Request):{
  "detail": "Invalid task configuration: missing 'config' key"
}




Example Request:{
  "name": "Test Workflow",
  "tasks": [
    {
      "type": "classical",
      "config": {
        "operation": "preprocess",
        "data": [1.0, 2.0, 3.0]
      }
    },
    {
      "type": "quantum",
      "config": {
        "circuit": "simple_x",
        "shots": 100,
        "backend": "cirq"
      }
    }
  ]
}



Run Workflow

URL: /api/workflows/run
Method: POST
Description: Executes a workflow by ID, running tasks in topological order.
Parameters (JSON body):
workflow_id (integer, required): ID of the workflow to execute.


Response:
Success (200 OK):{
  "workflow_id": 1,
  "name": "Test Workflow",
  "results": {
    "0": 2.0,
    "1": {"0": 50, "1": 50}
  }
}


Error (404 Not Found):{
  "detail": "Workflow ID 999 not found"
}




Example Request:{
  "workflow_id": 1
}



Get Workflow Status

URL: /api/workflows/{workflow_id}
Method: GET
Description: Retrieves the status of a workflow by ID.
Parameters (URL):
workflow_id (integer, required): ID of the workflow.


Response:
Success (200 OK):{
  "workflow_id": 1,
  "name": "Test Workflow",
  "status": "completed"
}


Error (404 Not Found):{
  "detail": "Workflow ID 999 not found"
}




Example Request:GET /api/workflows/1



2. Performance Monitoring
Get Workflow Metrics

URL: /api/performance/{workflow_id}
Method: GET
Description: Retrieves performance metrics for all tasks in a workflow.
Parameters (URL):
workflow_id (integer, required): ID of the workflow.


Response:
Success (200 OK):[
  {
    "workflow_id": 1,
    "task_id": 0,
    "runtime": 2.5,
    "circuit_depth": 5,
    "shots": 100,
    "timestamp": "2025-08-03T16:33:00"
  },
  {
    "workflow_id": 1,
    "task_id": 1,
    "runtime": 3.2,
    "circuit_depth": null,
    "shots": null,
    "timestamp": "2025-08-03T16:34:00"
  }
]


Error (404 Not Found):{
  "detail": "No metrics found for workflow 999"
}




Example Request:GET /api/performance/1



Get Task Metrics

URL: /api/performance/{workflow_id}/{task_id}
Method: GET
Description: Retrieves performance metrics for a specific task in a workflow.
Parameters (URL):
workflow_id (integer, required): ID of the workflow.
task_id (integer, required): ID of the task.


Response:
Success (200 OK):{
  "workflow_id": 1,
  "task_id": 0,
  "runtime": 2.5,
  "circuit_depth": 5,
  "shots": 100,
  "timestamp": "2025-08-03T16:33:00"
}


Error (404 Not Found):{
  "detail": "No metrics found for workflow 1, task 999"
}




Example Request:GET /api/performance/1/0



3. Quantum Backend Execution
Execute Quantum Circuit

URL: /api/quantum/execute
Method: POST
Description: Executes a quantum circuit on a specified backend (Cirq, Qiskit, or PennyLane).
Parameters (JSON body):
backend (string, required): Quantum backend (cirq, qiskit, or pennylane).
config (object, required): Circuit configuration, including:
circuit (string, required): Circuit type (e.g., simple_x, simple_variational).
shots (integer, optional): Number of shots (default: 100).
backend_type (string, optional): simulator or cloud (default: simulator).
params (array, optional): Variational parameters (for PennyLane).
processor_id (string, optional): Cloud processor ID (for Cirq/Qiskit).




Response:
Success (200 OK):{
  "backend": "cirq",
  "result": {
    "0": 50,
    "1": 50
  }
}


Error (400 Bad Request):{
  "detail": "Invalid backend or configuration"
}




Example Request:{
  "backend": "cirq",
  "config": {
    "circuit": "simple_x",
    "shots": 100,
    "backend_type": "simulator"
  }
}



Error Handling

All endpoints return appropriate HTTP status codes:
200 OK: Successful request.
400 Bad Request: Invalid input or configuration.
404 Not Found: Resource (workflow, task, or metrics) not found.
500 Internal Server Error: Unexpected server error.


Error responses include a detail field describing the issue.

Authentication

Currently, no authentication is required for these endpoints.
Future versions may integrate OAuth2 or API key authentication for secure access, especially for quantum backend API calls.

Notes

The API assumes the SQLite database is initialized with the required tables (workflows, schedules, performance_metrics).
Quantum backend execution requires valid API keys configured as environment variables (CIRQ_API_KEY, QISKIT_API_KEY, PENNYLANE_API_KEY).
The /api/workflows and /api/performance endpoints are integrated with the React frontend for real-time monitoring and workflow management.

This API provides a robust interface for managing hybrid quantum-classical workflows in the QuantumFlow Toolkit, ensuring seamless interaction between the frontend, workflow engine, and quantum backends.
