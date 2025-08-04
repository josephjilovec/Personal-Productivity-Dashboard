QuantumFlow Toolkit Setup Guide
This guide provides step-by-step instructions to set up and run the QuantumFlow Toolkit, a framework for managing hybrid quantum-classical workflows. It covers local setup for Python and Rust components, containerization with Docker, orchestration with Kubernetes, and deployment on AWS. The current date is August 3, 2025.
Prerequisites
Before starting, ensure you have the following installed:

Python: 3.9 or higher
Rust: 1.65 or higher (with cargo)
Docker: 20.10 or higher
kubectl: For Kubernetes deployment
AWS CLI: For AWS deployment
Node.js: 16.x or higher (for frontend)
Git: For cloning the repository
Quantum Cloud Credentials:
Google Quantum Engine API key (CIRQ_API_KEY)
IBM Quantum API key (QISKIT_API_KEY)
Xanadu Cloud API key (PENNYLANE_API_KEY)



Repository Structure
Clone the QuantumFlow Toolkit repository:
git clone https://github.com/quantumflow-toolkit/quantumflow.git
cd quantumflow

The repository is structured as follows:
quantumflow/
├── backend/
│   ├── python/
│   │   ├── workflow/
│   │   │   ├── engine.py
│   │   │   ├── scheduler.py
│   │   ├── quantum/
│   │   │   ├── cirq_backend.py
│   │   │   ├── qiskit_backend.py
│   │   │   ├── pennylane_backend.py
│   │   ├── monitor/
│   │   │   ├── performance.py
│   │   │   ├── cost_estimator.py
│   │   ├── cli.py
│   ├── rust/
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── scheduler.rs
│   │   ├── Cargo.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── App.js
│   │   │   ├── Navbar.js
│   │   │   ├── WorkflowDesigner.js
│   │   │   ├── Dashboard.js
│   │   ├── styles/
│   │   │   ├── tailwind.css
│   │   ├── index.js
├── tests/
│   ├── python/
│   │   ├── test_workflow.py
│   │   ├── test_quantum.py
│   │   ├── test_monitor.py
│   ├── frontend/
│   │   ├── test_designer.js
│   │   ├── test_dashboard.js
│   ├── rust/
│   │   ├── tests/
│   │   │   ├── scheduler.rs
├── docs/
│   ├── architecture.md
│   ├── api_endpoints.md
│   ├── setup_guide.md
├── Dockerfile
├── kubernetes/
│   ├── deployment.yaml
│   ├── service.yaml
├── README.md

Local Setup
1. Python Backend Setup

Create a Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Python Dependencies:Create a requirements.txt file in backend/python/ with the following:
fastapi==0.103.0
uvicorn==0.23.2
networkx==3.1
torch==2.0.1
cirq==1.2.0
qiskit==0.44.0
pennylane==0.31.0
pytest==7.4.0
axios==1.4.0

Install dependencies:
pip install -r backend/python/requirements.txt


Set Environment Variables:Export quantum backend API keys:
export CIRQ_API_KEY="your_google_quantum_key"
export QISKIT_API_KEY="your_ibm_quantum_key"
export PENNYLANE_API_KEY="your_xanadu_cloud_key"


Run FastAPI Server:Start the FastAPI server for the backend:
cd backend/python
uvicorn main:app --host 0.0.0.0 --port 8000

Note: Ensure main.py exists to initialize FastAPI with imports from workflow, monitor, etc. Example:
from fastapi import FastAPI
from backend.python.monitor.performance import app as performance_app

app = FastAPI()
app.mount("/api/performance", performance_app)


Run CLI:Use the CLI to manage workflows:
python cli.py create-workflow --name "Test Workflow" --tasks-file tasks.json

Example tasks.json:
[
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



2. Rust Scheduler Setup

Install Rust:Install Rust using rustup:
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env


Build Rust Scheduler:Navigate to the Rust directory and build the PyO3 module:
cd backend/rust
cargo build --release


Install PyO3 Module:Copy the compiled library to the Python backend:
cp target/release/libpyo3_runtime.so ../python/pyo3_runtime.so  # On Linux
# On macOS: cp target/release/libpyo3_runtime.dylib ../python/pyo3_runtime.dylib
# On Windows: cp target/release/pyo3_runtime.dll ../python/pyo3_runtime.dll


Test Rust Scheduler:Run unit tests:
cargo test



3. Frontend Setup

Install Node.js Dependencies:Navigate to the frontend directory and install dependencies:
cd frontend
npm install react@18.2.0 react-dom@18.2.0 react-router-dom@6.14.2 axios@1.4.0 react-beautiful-dnd@13.1.1 chart.js@4.3.0 react-chartjs-2@5.2.0


Run Frontend:Start the React development server:
npm start

The frontend will be available at http://localhost:3000.


4. Running Tests

Python Tests:Run pytest for backend tests:
cd tests/python
pytest test_workflow.py test_quantum.py test_monitor.py


Frontend Tests:Run Jest for frontend tests:
cd frontend
npm test


Rust Tests:Run Cargo tests for the scheduler:
cd backend/rust
cargo test



Docker Setup

Create Dockerfile:Create a Dockerfile in the project root:
FROM python:3.9-slim

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy backend and frontend
COPY backend/python /app/backend/python
COPY backend/rust /app/backend/rust
COPY frontend /app/frontend

# Install Python dependencies
COPY backend/python/requirements.txt /app/backend/python/
RUN pip install --no-cache-dir -r /app/backend/python/requirements.txt

# Build Rust scheduler
RUN cd /app/backend/rust && cargo build --release
RUN cp /app/backend/rust/target/release/libpyo3_runtime.so /app/backend/python/pyo3_runtime.so

# Install frontend dependencies
RUN cd /app/frontend && npm install

# Expose ports
EXPOSE 8000 3000

# Start FastAPI and React
CMD ["sh", "-c", "cd /app/frontend && npm start & cd /app/backend/python && uvicorn main:app --host 0.0.0.0 --port 8000"]


Build and Run Docker Container:Build the Docker image:
docker build -t quantumflow-toolkit .

Run the container with environment variables:
docker run -p 8000:8000 -p 3000:3000 \
  -e CIRQ_API_KEY="your_google_quantum_key" \
  -e QISKIT_API_KEY="your_ibm_quantum_key" \
  -e PENNYLANE_API_KEY="your_xanadu_cloud_key" \
  quantumflow-toolkit



Kubernetes Deployment

Create Kubernetes Manifests:Create a kubernetes/deployment.yaml:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quantumflow-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: quantumflow
  template:
    metadata:
      labels:
        app: quantumflow
    spec:
      containers:
      - name: quantumflow
        image: quantumflow-toolkit:latest
        ports:
        - containerPort: 8000
        - containerPort: 3000
        env:
        - name: CIRQ_API_KEY
          value: "your_google_quantum_key"
        - name: QISKIT_API_KEY
          value: "your_ibm_quantum_key"
        - name: PENNYLANE_API_KEY
          value: "your_xanadu_cloud_key"

Create a kubernetes/service.yaml:
apiVersion: v1
kind: Service
metadata:
  name: quantumflow-service
spec:
  selector:
    app: quantumflow
  ports:
  - name: backend
    port: 8000
    targetPort: 8000
  - name: frontend
    port: 3000
    targetPort: 3000
  type: LoadBalancer


Deploy to Kubernetes:Apply the manifests:
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml


Access the Application:Get the external IP:
kubectl get services

Access the frontend at http://<external-ip>:3000 and the API at http://<external-ip>:8000.


AWS Deployment

Push Docker Image to Amazon ECR:Create an ECR repository:
aws ecr create-repository --repository-name quantumflow-toolkit

Authenticate Docker to ECR:
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

Tag and push the image:
docker tag quantumflow-toolkit:latest <account-id>.dkr.ecr.<region>.amazonaws.com/quantumflow-toolkit:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/quantumflow-toolkit:latest


Deploy with Elastic Beanstalk:Create a Dockerrun.aws.json in the project root:
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "<account-id>.dkr.ecr.<region>.amazonaws.com/quantumflow-toolkit:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": 8000,
      "HostPort": 8000
    },
    {
      "ContainerPort": 3000,
      "HostPort": 3000
    }
  ],
  "Environment": [
    {
      "Name": "CIRQ_API_KEY",
      "Value": "your_google_quantum_key"
    },
    {
      "Name": "QISKIT_API_KEY",
      "Value": "your_ibm_quantum_key"
    },
    {
      "Name": "PENNYLANE_API_KEY",
      "Value": "your_xanadu_cloud_key"
    }
  ]
}

Initialize and deploy with Elastic Beanstalk CLI:
eb init -p docker quantumflow-app --region <region>
eb create quantumflow-env
eb deploy


Access the Application:Get the Elastic Beanstalk URL:
eb open



Troubleshooting

Python Dependency Issues: Ensure requirements.txt matches the specified versions. Use pip install --force-reinstall if needed.
Rust Build Errors: Verify Rust version (rustc --version) and PyO3 compatibility. Run cargo clean and rebuild.
Docker Build Failures: Check for missing dependencies or incorrect paths in the Dockerfile.
Kubernetes Issues: Verify kubectl configuration with kubectl cluster-info. Check pod logs with kubectl logs.
AWS Deployment Errors: Ensure AWS CLI is configured (aws configure) and IAM roles allow ECR/EB access.

Next Steps

Explore the API endpoints in docs/api_endpoints.md.
Review the architecture in docs/architecture.md.
Run the CLI or frontend to create and monitor workflows.
Use the test suites in tests/ to verify functionality.

This setup guide enables you to run the QuantumFlow Toolkit locally or deploy it to a scalable cloud environment.
