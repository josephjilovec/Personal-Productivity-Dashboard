import pytest
import sqlite3
import json
from pathlib import Path
from unittest.mock import patch
from backend.python.workflow.engine import WorkflowEngine
from backend.python.workflow.scheduler import WorkflowScheduler
import torch

# Fixture to set up and tear down SQLite database
@pytest.fixture
def db_path(tmp_path):
    db_file = tmp_path / "test_workflows.db"
    yield str(db_file)
    if db_file.exists():
        db_file.unlink()

# Fixture to initialize WorkflowEngine
@pytest.fixture
def engine(db_path):
    engine = WorkflowEngine(db_path=db_path)
    yield engine
    engine.close()

# Fixture to initialize WorkflowScheduler
@pytest.fixture
def scheduler(db_path):
    scheduler = WorkflowScheduler(db_path=db_path)
    yield scheduler
    scheduler.close()

# Mock quantum backend execution
@pytest.fixture
def mock_quantum_backend():
    with patch("backend.python.workflow.scheduler.WorkflowScheduler._execute_quantum_task") as mock:
        mock.return_value = {"0": 50, "1": 50}  # Mock quantum circuit result
        yield mock

# Test WorkflowEngine
def test_define_workflow_success(engine):
    tasks = [
        {"type": "classical", "config": {"operation": "preprocess", "data": [1.0, 2.0, 3.0]}},
        {"type": "quantum", "config": {"circuit": "simple_x", "shots": 100}}
    ]
    workflow_id = engine.define_workflow("Test Workflow", tasks)
    assert workflow_id > 0

    # Verify database entry
    conn = sqlite3.connect(engine.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, tasks, status FROM workflows WHERE id = ?", (workflow_id,))
    result = cursor.fetchone()
    conn.close()
    assert result is not None
    assert result[0] == "Test Workflow"
    assert json.loads(result[1]) == tasks
    assert result[2] == "pending"

def test_define_workflow_invalid_tasks(engine):
    tasks = [{"type": "classical"}]  # Missing config
    workflow_id = engine.define_workflow("Invalid Workflow", tasks)
    assert workflow_id == -1

def test_execute_workflow_success(engine, mock_quantum_backend):
    tasks = [
        {"type": "classical", "config": {"operation": "preprocess", "data": [1.0, 2.0, 3.0]}},
        {"type": "quantum", "config": {"circuit": "simple_x", "shots": 100}}
    ]
    workflow_id = engine.define_workflow("Test Workflow", tasks)
    result = engine.execute_workflow(workflow_id)
    
    assert result is not None
    assert result["workflow_id"] == workflow_id
    assert result["name"] == "Test Workflow"
    assert len(result["results"]) == 2
    assert isinstance(result["results"][0], float)  # Classical task result (mean)
    assert result["results"][1] == {"0": 50, "1": 50}  # Mocked quantum result

def test_execute_workflow_not_found(engine):
    result = engine.execute_workflow(999)
    assert result is None

def test_get_workflow_status(engine):
    tasks = [{"type": "classical", "config": {"operation": "preprocess", "data": [1.0, 2.0, 3.0]}}]
    workflow_id = engine.define_workflow("Test Workflow", tasks)
    status = engine.get_workflow_status(workflow_id)
    
    assert status is not None
    assert status["workflow_id"] == workflow_id
    assert status["name"] == "Test Workflow"
    assert status["status"] == "pending"

def test_get_workflow_status_not_found(engine):
    status = engine.get_workflow_status(999)
    assert status is None

# Test WorkflowScheduler
def test_schedule_workflow_success(scheduler, mock_quantum_backend):
    tasks = [
        {"type": "classical", "config": {"operation": "preprocess", "data": [1.0, 2.0, 3.0], "backend": "local"}},
        {"type": "quantum", "config": {"circuit": "simple_x", "shots": 100, "backend": "cirq"}}
    ]
    workflow_id = 1
    schedule = scheduler.schedule_workflow(workflow_id, tasks)
    
    assert schedule is not None
    assert len(schedule) == 2
    assert all(task["id"] in [0, 1] for task in schedule)

    # Verify database entry
    conn = sqlite3.connect(scheduler.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT workflow_id, task_id, backend, status FROM schedules WHERE workflow_id = ?", (workflow_id,))
    results = cursor.fetchall()
    conn.close()
    assert len(results) == 2
    assert all(result[3] == "pending" for result in results)

def test_schedule_workflow_empty_tasks(scheduler):
    schedule = scheduler.schedule_workflow(1, [])
    assert schedule is None

def test_execute_scheduled_tasks_success(scheduler, mock_quantum_backend):
    tasks = [
        {"type": "classical", "config": {"operation": "preprocess", "data": [1.0, 2.0, 3.0], "backend": "local"}},
        {"type": "quantum", "config": {"circuit": "simple_x", "shots": 100, "backend": "cirq"}}
    ]
    workflow_id = 1
    scheduler.schedule_workflow(workflow_id, tasks)
    result = scheduler.execute_scheduled_tasks(workflow_id)
    
    assert result is not None
    assert result["workflow_id"] == workflow_id
    assert len(result["results"]) == 2
    assert isinstance(result["results"][0], float)  # Classical task result
    assert result["results"][1] == {"0": 50, "1": 50}  # Mocked quantum result

def test_execute_scheduled_tasks_not_found(scheduler):
    result = scheduler.execute_scheduled_tasks(999)
    assert result is None

def test_get_schedule_status(scheduler):
    tasks = [{"type": "classical", "config": {"operation": "preprocess", "data": [1.0, 2.0, 3.0], "backend": "local"}}]
    workflow_id = 1
    scheduler.schedule_workflow(workflow_id, tasks)
    status = scheduler.get_schedule_status(workflow_id)
    
    assert status is not None
    assert len(status) == 1
    assert status[0]["task_id"] == 0
    assert status[0]["status"] == "pending"

def test_get_schedule_status_not_found(scheduler):
    status = scheduler.get_schedule_status(999)
    assert status is None
