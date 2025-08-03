import pytest
from unittest.mock import patch
from backend.python.quantum.cirq_backend import CirqBackend
from backend.python.quantum.qiskit_backend import QiskitBackend
from backend.python.quantum.pennylane_backend import PennyLaneBackend

# Fixture to set up mock environment variables
@pytest.fixture
def mock_env():
    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key: {
            "CIRQ_API_KEY": "test_cirq_key",
            "QISKIT_API_KEY": "test_qiskit_key",
            "PENNYLANE_API_KEY": "test_pennylane_key"
        }.get(key)
        yield

# Test CirqBackend
@patch("backend.python.quantum.cirq_backend.quantum.QuantumEngineServiceClient")
def test_cirq_backend_simulator(mock_quantum_client, mock_env):
    backend = CirqBackend()
    config = {
        "circuit": "simple_x",
        "shots": 100,
        "backend": "simulator"
    }
    
    result = backend.execute_cirq_circuit(config)
    
    assert result is not None
    assert result["backend"] == "simulator"
    assert isinstance(result["result"], dict)
    assert "0" in result["result"] or "1" in result["result"]  # Expected histogram keys

@patch("backend.python.quantum.cirq_backend.quantum.QuantumEngineServiceClient")
def test_cirq_backend_cloud(mock_quantum_client, mock_env):
    mock_client = mock_quantum_client.return_value
    mock_client.get_quantum_result.return_value.histogram = {0: 50, 1: 50}
    
    backend = CirqBackend()
    config = {
        "circuit": "simple_x",
        "shots": 100,
        "backend": "cloud",
        "processor_id": "test_processor"
    }
    
    result = backend.execute_cirq_circuit(config)
    
    assert result is not None
    assert result["backend"] == "cloud"
    assert result["result"] == {"0": 50, "1": 50}
    mock_client.create_quantum_job.assert_called()

def test_cirq_backend_invalid_config(mock_env):
    backend = CirqBackend()
    config = {}  # Missing circuit
    result = backend.execute_cirq_circuit(config)
    
    assert result is None

# Test QiskitBackend
@patch("backend.python.quantum.qiskit_backend.IBMQ.load_account")
def test_qiskit_backend_simulator(mock_load_account, mock_env):
    backend = QiskitBackend()
    config = {
        "circuit": "simple_x",
        "shots": 100,
        "backend": "simulator"
    }
    
    result = backend.execute_qiskit_circuit(config)
    
    assert result is not None
    assert result["backend"] == "simulator"
    assert isinstance(result["result"], dict)
    assert "0" in result["result"] or "1" in result["result"]

@patch("backend.python.quantum.qiskit_backend.IBMQ.load_account")
@patch("backend.python.quantum.qiskit_backend.execute")
def test_qiskit_backend_cloud(mock_execute, mock_load_account, mock_env):
    mock_job = mock_execute.return_value
    mock_job.result.return_value.get_counts.return_value = {"0": 50, "1": 50}
    
    backend = QiskitBackend()
    config = {
        "circuit": "simple_x",
        "shots": 100,
        "backend": "cloud",
        "backend_id": "ibmq_qasm_simulator"
    }
    
    result = backend.execute_qiskit_circuit(config)
    
    assert result is not None
    assert result["backend"] == "cloud"
    assert result["result"] == {"0": 50, "1": 50}
    mock_execute.assert_called()

def test_qiskit_backend_invalid_config(mock_env):
    backend = QiskitBackend()
    config = {}  # Missing circuit
    result = backend.execute_qiskit_circuit(config)
    
    assert result is None

# Test PennyLaneBackend
@patch("backend.python.quantum.pennylane_backend.qml.device")
def test_pennylane_backend_simulator(mock_device, mock_env):
    mock_dev = mock_device.return_value
    mock_dev.name = "default.qubit"
    
    backend = PennyLaneBackend()
    config = {
        "circuit": "simple_variational",
        "shots": 100,
        "backend": "default.qubit",
        "params": [0.5]
    }
    
    result = backend.execute_pennylane_circuit(config)
    
    assert result is not None
    assert result["backend"] == "default.qubit"
    assert isinstance(result["result"], dict)
    mock_device.assert_called_with("default.qubit", wires=1, shots=100)

@patch("backend.python.quantum.pennylane_backend.qml.device")
def test_pennylane_backend_cloud(mock_device, mock_env):
    mock_dev = mock_device.return_value
    mock_dev.name = "xanadu.cloud"
    
    backend = PennyLaneBackend()
    config = {
        "circuit": "simple_variational",
        "shots": 100,
        "backend": "cloud",
        "params": [0.5]
    }
    
    result = backend.execute_pennylane_circuit(config)
    
    assert result is not None
    assert result["backend"] == "cloud"
    assert isinstance(result["result"], dict)
    mock_device.assert_called_with("xanadu.cloud", wires=1, shots=100, api_key="test_pennylane_key")

def test_pennylane_backend_invalid_config(mock_env):
    backend = PennyLaneBackend()
    config = {}  # Missing circuit
    result = backend.execute_pennylane_circuit(config)
    
    assert result is None
