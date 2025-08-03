import os
import logging
from typing import Dict, Any, Optional
from qiskit import QuantumCircuit, Aer, IBMQ
from qiskit.execute import execute
from qiskit.providers.ibmq import IBMQError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QiskitBackend:
    """Integrates with IBM's Qiskit for executing quantum circuits."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('QISKIT_API_KEY')
        self.backend = None
        self.provider = None
        if self.api_key:
            try:
                IBMQ.save_account(self.api_key, overwrite=True)
                self.provider = IBMQ.load_account()
                logger.info("Initialized QiskitBackend with IBM Quantum provider")
            except Exception as e:
                logger.error(f"Failed to initialize IBM Quantum provider: {str(e)}")
                self.provider = None
        else:
            logger.warning("No Qiskit API key provided, using local simulator only")
    
    def execute_qiskit_circuit(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a quantum circuit defined in the workflow config."""
        try:
            # Validate config
            if 'circuit' not in config:
                raise ValueError("Circuit configuration is required")

            # Parse circuit (example: simple X gate circuit)
            circuit_type = config.get('circuit', 'simple_x')
            shots = config.get('shots', 100)
            backend_name = config.get('backend', 'simulator')

            # Build example circuit
            circuit = QuantumCircuit(1, 1)
            if circuit_type == 'simple_x':
                circuit.x(0)
                circuit.measure(0, 0)
            else:
                raise ValueError(f"Unsupported circuit type: {circuit_type}")

            # Execute based on backend
            if backend_name == 'simulator':
                result = self._run_simulator(circuit, shots)
            elif backend_name == 'cloud' and self.provider:
                result = self._run_cloud(circuit, shots, config.get('backend_id', 'ibmq_qasm_simulator'))
            else:
                raise ValueError(f"Invalid backend or missing cloud provider: {backend_name}")

            logger.info(f"Executed circuit '{circuit_type}' with {shots} shots on {backend_name}")
            return {'result': result.get_counts(), 'backend': backend_name}
        except Exception as e:
            logger.error(f"Error executing circuit: {str(e)}")
            return None
    
    def _run_simulator(self, circuit: QuantumCircuit, shots: int) -> Any:
        """Run circuit on Qiskit's Aer simulator."""
        try:
            backend = Aer.get_backend('qasm_simulator')
            job = execute(circuit, backend, shots=shots)
            result = job.result()
            return result
        except Exception as e:
            logger.error(f"Simulator execution error: {str(e)}")
            raise
    
    def _run_cloud(self, circuit: QuantumCircuit, shots: int, backend_id: str) -> Any:
        """Run circuit on IBM Quantum cloud QPU or simulator."""
        try:
            if not self.provider:
                raise ValueError("IBM Quantum provider not initialized")

            backend = self.provider.get_backend(backend_id)
            job = execute(circuit, backend, shots=shots)
            result = job.result()
            return result
        except IBMQError as e:
            logger.error(f"IBM Quantum API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Cloud execution error: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    backend = QiskitBackend()
    config = {
        'circuit': 'simple_x',
        'shots': 100,
        'backend': 'simulator'
    }
    result = backend.execute_qiskit_circuit(config)
    print(result)
