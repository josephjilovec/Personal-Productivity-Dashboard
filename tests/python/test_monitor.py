import pytest
import sqlite3
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.python.monitor.performance import PerformanceMonitor, app
from backend.python.monitor.cost_estimator import CostEstimator

# Fixture to set up and tear down SQLite database
@pytest.fixture
def db_path(tmp_path):
    db_file = tmp_path / "test_workflows.db"
    yield str(db_file)
    if db_file.exists():
        db_file.unlink()

# Fixture to initialize PerformanceMonitor
@pytest.fixture
def performance_monitor(db_path):
    monitor = PerformanceMonitor(db_path=db_path)
    yield monitor
    monitor.close()

# Fixture to initialize TestClient for FastAPI
@pytest.fixture
def client():
    return TestClient(app)

# Test PerformanceMonitor
def test_track_metrics_success(performance_monitor):
    task_config = {
        "type": "quantum",
        "config": {"circuit": "simple_x", "shots": 100, "depth": 5}
    }
    workflow_id = 1
    task_id = 0
    
    performance_monitor.track_metrics(workflow_id, task_id, task_config)
    
    # Verify database entry
    conn = sqlite3.connect(performance_monitor.db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT workflow_id, task_id, runtime, circuit_depth, shots FROM performance_metrics WHERE workflow_id = ? AND task_id = ?",
        (workflow_id, task_id)
    )
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None
    assert result[0] == workflow_id
    assert result[1] == task_id
    assert result[2] >= 0  # Runtime should be non-negative
    assert result[3] == 5
    assert result[4] == 100

def test_get_metrics_workflow_success(performance_monitor):
    task_config = {
        "type": "quantum",
        "config": {"circuit": "simple_x", "shots": 100, "depth": 5}
    }
    workflow_id = 1
    task_id = 0
    performance_monitor.track_metrics(workflow_id, task_id, task_config)
    
    metrics = performance_monitor.get_metrics(workflow_id)
    
    assert metrics is not None
    assert len(metrics) == 1
    assert metrics[0]["workflow_id"] == workflow_id
    assert metrics[0]["task_id"] == task_id
    assert metrics[0]["circuit_depth"] == 5
    assert metrics[0]["shots"] == 100

def test_get_metrics_task_success(performance_monitor):
    task_config = {
        "type": "quantum",
        "config": {"circuit": "simple_x", "shots": 100, "depth": 5}
    }
    workflow_id = 1
    task_id = 0
    performance_monitor.track_metrics(workflow_id, task_id, task_config)
    
    metrics = performance_monitor.get_metrics(workflow_id, task_id)
    
    assert metrics is not None
    assert len(metrics) == 1
    assert metrics[0]["workflow_id"] == workflow_id
    assert metrics[0]["task_id"] == task_id
    assert metrics[0]["circuit_depth"] == 5
    assert metrics[0]["shots"] == 100

def test_get_metrics_not_found(performance_monitor):
    metrics = performance_monitor.get_metrics(999)
    assert metrics is None

# Test FastAPI endpoints
def test_api_get_workflow_metrics(client, performance_monitor):
    task_config = {
        "type": "quantum",
        "config": {"circuit": "simple_x", "shots": 100, "depth": 5}
    }
    workflow_id = 1
    task_id = 0
    performance_monitor.track_metrics(workflow_id, task_id, task_config)
    
    response = client.get(f"/api/performance/{workflow_id}")
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["workflow_id"] == workflow_id
    assert response.json()[0]["task_id"] == task_id
    assert response.json()[0]["circuit_depth"] == 5
    assert response.json()[0]["shots"] == 100

def test_api_get_task_metrics(client, performance_monitor):
    task_config = {
        "type": "quantum",
        "config": {"circuit": "simple_x", "shots": 100, "depth": 5}
    }
    workflow_id = 1
    task_id = 0
    performance_monitor.track_metrics(workflow_id, task_id, task_config)
    
    response = client.get(f"/api/performance/{workflow_id}/{task_id}")
    
    assert response.status_code == 200
    assert response.json()["workflow_id"] == workflow_id
    assert response.json()["task_id"] == task_id
    assert response.json()["circuit_depth"] == 5
    assert response.json()["shots"] == 100

def test_api_get_metrics_not_found(client):
    response = client.get("/api/performance/999")
    assert response.status_code == 404
    assert "No metrics found" in response.json()["detail"]

# Test CostEstimator
def test_estimate_task_cost_success():
    estimator = CostEstimator()
    task_config = {
        "type": "quantum",
        "config": {"circuit": "simple_x", "shots": 100, "depth": 5, "backend": "cirq", "backend_type": "simulator"}
    }
    
    cost = estimator.estimate_task_cost(task_config, "cirq", "simulator")
    
    assert cost is not None
    assert cost == (100 * 0.0001) + (5 * 0.001)  # Expected cost: shots * cost_per_shot + depth * cost_per_depth

def test_estimate_task_cost_invalid_config():
    estimator = CostEstimator()
    task_config = {"type": "classical"}  # Missing config
    cost = estimator.estimate_task_cost(task_config, "cirq", "simulator")
    assert cost is None

def test_estimate_workflow_cost_success():
    estimator = CostEstimator()
    tasks = [
        {"type": "quantum", "config": {"circuit": "simple_x", "shots": 100, "depth": 5, "backend": "cirq", "backend_type": "simulator"}},
        {"type": "quantum", "config": {"circuit": "variational", "shots": 200, "depth": 10, "backend": "qiskit", "backend_type": "cloud"}}
    ]
    
    result = estimator.estimate_workflow_cost(tasks)
    
    assert result is not None
    assert result["total_cost"] > 0
    assert len(result["breakdown"]) == 2
    assert result["breakdown"][0]["task_id"] == 0
    assert result["breakdown"][1]["task_id"] == 1

@patch("backend.python.workflow.scheduler.WorkflowScheduler")
def test_optimize_schedule_success(mock_scheduler):
    estimator = CostEstimator()
    tasks = [
        {"type": "quantum", "config": {"circuit": "simple_x", "shots": 100, "depth": 5, "backend": "cirq", "backend_type": "simulator"}}
    ]
    mock_scheduler_instance = mock_scheduler.return_value
    mock_scheduler_instance.rust_scheduler.schedule_tasks.return_value = json.dumps([
        {"id": 0, "type": "quantum", "backend": "cirq", "estimated_cost": 0.015}
    ])
    
    result = estimator.optimize_schedule(tasks, max_budget=1.0)
    
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == 0

@patch("backend.python.workflow.scheduler.WorkflowScheduler")
def test_optimize_schedule_failure(mock_scheduler):
    estimator = CostEstimator()
    tasks = [
        {"type": "quantum", "config": {"circuit": "simple_x", "shots": 100, "depth": 5, "backend": "cirq", "backend_type": "simulator"}}
    ]
    mock_scheduler_instance = mock_scheduler.return_value
    mock_scheduler_instance.rust_scheduler.schedule_tasks.side_effect = Exception("Rust scheduler error")
    
    result = estimator.optimize_schedule(tasks, max_budget=1.0)
    
    assert result is None
