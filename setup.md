# Project Setup Guide

This project runs on Python and uses a Groq API key for the LLM workflow. The base app can run locally without Redis or Kafka, but those services are recommended for full feature parity.

## 1. Required tools

Install the following before running the project:

- Git
- Python 3.11.x
- pip
- virtual environment support (`venv`)
- Docker Desktop (recommended for Redis and Kafka)
- Optional: Docker Compose
- Optional: Redis and Kafka services
- Optional for AWS deployment: AWS CLI v2 and Terraform 1.6+

### Windows

Install Git and Python from:

- Git: https://git-scm.com/download/win
- Python: https://www.python.org/downloads/windows/
- Docker Desktop: https://www.docker.com/products/docker-desktop/

Verify installation:

```powershell
git --version
python --version
pip --version
docker --version
```

### macOS

```bash
xcode-select --install
brew install git python@3.11 docker
```

Verify:

```bash
git --version
python3.11 --version
docker --version
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y git python3.11 python3.11-venv python3-pip docker.io docker-compose-plugin
```

Verify:

```bash
git --version
python3.11 --version
pip --version
docker --version
```

## 2. Clone the repository

```bash
git clone https://github.com/Ayush-Singh986/Agentic-Ai-Resolution-Plateform.git
cd Agentic-Ai-Resolution-Plateform
```

## 3. Create a Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

## 4. Install Python dependencies

From the project root:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The project dependencies include:

- FastAPI
- Uvicorn
- LangChain / LangGraph
- Groq SDK
- Sentence Transformers
- FAISS
- Redis
- Kafka client
- Streamlit
- Prometheus client
- Pydantic
- Presidio
- Pandas / NumPy / Tiktoken

## 5. Create your environment file

Copy the sample environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then update `.env` and set your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
```

You can also set the optional values for Redis, Kafka, logging, and model thresholds in the same file.

## 6. Get the Groq API key

Create an account at:

- https://console.groq.com

Then generate an API key and paste it into `.env`.

This app uses Groq as the LLM backend for triage, retrieval validation, RCA, and remediation planning.

## 7. Start optional infrastructure services

The app can run without Redis and Kafka because the code falls back to in-memory storage and local event logging if those services are unavailable. However, if you want the full runtime experience, start them locally.

### Redis

```bash
docker run -d --name incident-redis -p 6379:6379 redis:7-alpine
```

### Kafka

A local Kafka broker requires a bit more setup. The easiest way is to run it with Docker:

```bash
docker run -d --name incident-kafka \
  -p 9092:9092 \
  -e KAFKA_CFG_NODE_ID=1 \
  -e KAFKA_CFG_PROCESS_ROLES=broker,controller \
  -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 \
  -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT \
  -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -e KAFKA_CFG_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  -e KAFKA_CFG_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1 \
  -e KAFKA_CFG_TRANSACTION_STATE_LOG_MIN_ISR=1 \
  bitnami/kafka:latest
```

If Kafka is not running, the application will still start, but events will be logged locally instead of being published to Kafka.

## 8. Build the local FAISS index

This project contains a local knowledge base and a FAISS index. Build it before starting the API:

```bash
python ingest_data.py
```

This step may take a few minutes the first time because it downloads the embedding model and prepares the local index.

## 9. Start the FastAPI backend

From the project root:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Check the health endpoint:

```bash
curl http://localhost:8000/health
```

Swagger docs:

```text
http://localhost:8000/docs
```

## 10. Start the Streamlit UI

Open a second terminal, activate the same virtual environment, and run:

```bash
streamlit run ui/streamlit_app.py
```

Then open:

```text
http://localhost:8501
```

## 11. Test the app

Submit a sample incident through the UI or with cURL:

```bash
curl -X POST http://localhost:8000/incident \
  -H "Content-Type: application/json" \
  -d '{"incident_id":"INC-1005","title":"Payment API Failure","description":"Payment API timeout after deployment."}'
```

## 12. Optional: run the project with Docker

The repository includes a Dockerfile. You can build and run it with:

```bash
docker build -t incident-resolution .
docker run -d --name incident-resolution-app -p 8000:8000 -p 8501:8501 incident-resolution
```

If you want to run the API and UI as separate containers, use the commands described in the README and set the required environment variables.

## 13. Optional: AWS deployment tools

If you plan to deploy to AWS with Terraform, install:

- AWS CLI v2
- Terraform 1.6+
- Docker Desktop

Check installation:

```bash
aws --version
terraform --version
```

## Troubleshooting

- If the app cannot connect to Groq, verify `GROQ_API_KEY` is set correctly in `.env`.
- If the embedding model download fails, confirm internet access and enough disk space.
- If Redis or Kafka are not running, the app will still start, but those features will be degraded.
- If the UI fails to open, make sure the backend is running on port 8000 and the UI is running on port 8501.
- If Python package installation fails, recreate the virtual environment and reinstall dependencies.

## Summary

To run this project locally, the minimum setup is:

1. Install Git + Python 3.11 + Docker Desktop
2. Clone the repo
3. Create a virtual environment
4. Install dependencies from `requirements.txt`
5. Copy `.env.example` to `.env` and add your Groq API key
6. Build the FAISS index via `python ingest_data.py`
7. Start the backend with `uvicorn main:app --host 0.0.0.0 --port 8000`
8. Start the UI with `streamlit run ui/streamlit_app.py`

This is enough to run the incident-analysis workflow locally.
