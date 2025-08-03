QuantumFlow Toolkit

QuantumFlow Toolkit is an open-source framework designed to streamline the development, deployment, and monitoring of hybrid quantum-classical applications. It enables seamless integration of classical tasks (e.g., AI preprocessing with PyTorch) and quantum tasks (e.g., variational algorithms with Cirq, Qiskit, or PennyLane) in distributed environments. Aligned with xAI's mission to accelerate scientific discovery, QuantumFlow provides a modular workflow engine, quantum backend integrations, resource orchestration, and an intuitive CLI and web dashboard. The toolkit is containerized with Docker and deployable on AWS, ensuring scalability and reliability.

Project Overview

QuantumFlow Toolkit facilitates hybrid quantum-classical workflows by orchestrating tasks, optimizing resource usage, and monitoring performance. Key features include:

Workflow Engine: Defines and executes hybrid workflows using a directed acyclic graph (DAG) model, combining classical and quantum tasks.
Quantum Backend Integration: Supports Cirq/qsim, Qiskit, and PennyLane for flexible quantum task execution.
Resource Management: Monitors performance metrics (e.g., circuit depth, shots) and schedules tasks to minimize latency or cost.
User Interface: Provides a Python CLI and React-based dashboard for workflow design and monitoring.
Scalability: Handles distributed environments with Docker and Kubernetes.
Security: Securely manages API keys for quantum cloud providers.

The repository is structured for modularity, with comprehensive tests (>90% coverage) using pytest, Cargo, and Jest, and a CI/CD pipeline via GitHub Actions.

Setup Instructions
Prerequisites

Python: 3.9+
Rust: Latest stable version (via rustup)
Node.js: v18 (for frontend)
Docker: Latest version (optional for containerized deployment)
Git: For cloning the repository

Installation

Clone the Repository:
git clone https://github.com/josephjilovec/QuantumFlow-Toolkit.git
cd QuantumFlow-Toolkit


Install Python Dependencies:
pip install -r deploy/requirements.txt

Dependencies include cirq, qiskit, pennylane, pytorch, fastapi, sqlite, and pytest.

Install Rust Dependencies:
cd backend/rust
cargo build


Install Frontend Dependencies:
cd frontend
npm install


Set Up Environment Variables:

Create a .env file in the root directory:CIRQ_API_KEY=<your_cirq_api_key>
QISKIT_API_KEY=<your_qiskit_api_key>
PENNYLANE_API_KEY=<your_pennylane_api_key>
PORT=8000

Obtain API keys from quantum providers (Google, IBM, Xanadu) or leave empty for local simulation.


Run Locally:

Start the backend (FastAPI server):cd backend/python
uvicorn cli:app --host 0.0.0.0 --port 8000


In a new terminal, start the frontend:cd frontend
npm start


Access the dashboard at http://localhost:3000.


Run with Docker:

Build the Docker image:docker build -t quantumflow-toolkit -f deploy/Dockerfile .


Run the container:docker run -p 8000:8000 -e CIRQ_API_KEY=<key> -e QISKIT_API_KEY=<key> -e PENNYLANE_API_KEY=<key> quantumflow-toolkit


Access at http://localhost:8000.



Deploying to the Cloud
To deploy QuantumFlow Toolkit for public access, use AWS Elastic Beanstalk:

Install AWS CLI: pip install awscli.
Configure AWS credentials:aws configure

Enter AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and set region to us-east-1.
Build and push Docker image:docker build -t quantumflow-toolkit -f deploy/Dockerfile .
docker tag quantumflow-toolkit:latest your_docker_username/quantumflow-toolkit:latest
docker push your_docker_username/quantumflow-toolkit:latest


Deploy to Elastic Beanstalk:eb init -p docker quantumflow-toolkit --region us-east-1
eb create quantumflow-toolkit-env --single --instance_type t3.medium
eb deploy quantumflow-toolkit-env


Set environment variables:eb setenv CIRQ_API_KEY=<key> QISKIT_API_KEY=<key> PENNYLANE_API_KEY=<key> PORT=8000


Access at http://quantumflow-toolkit-env.<random-id>.us-east-1.elasticbeanstalk.com.

Live Demo
A live demo is not currently hosted. To test QuantumFlow Toolkit, follow the setup instructions above to run locally or deploy to AWS. Deployment may incur costs (~$12-$50/month).
Usage Examples
1. Define a Workflow (CLI)
Create a hybrid workflow:
python backend/python/cli.py create-workflow --name "Hybrid AI-QC" --tasks classical:preprocess.json,quantum:variational_circuit.py

2. Run a Workflow
Execute a workflow:
python backend/python/cli.py run-workflow --id <workflow_id>

3. Monitor Performance
Check performance metrics:
python backend/python/cli.py monitor --id <workflow_id>

4. View Dashboard

Run the app locally:cd frontend
npm start


Navigate to http://localhost:3000 to design workflows and view metrics.

Testing
Run tests for all components:
# Python tests
pytest tests/python/ -v
# Rust tests
cd backend/rust
cargo test
# Frontend tests
cd frontend
npm test

Contributing
Contributions are welcome under the MIT License. Please:

Fork the repository and create a pull request to the main branch.
Ensure tests pass and add new tests for features.
Follow code style (flake8 for Python, rustfmt for Rust, ESLint for JavaScript).

License
QuantumFlow Toolkit is licensed under the MIT License. See LICENSE for details.
Contact
For questions or issues, contact Joseph Jilovec or open an issue on GitHub.
