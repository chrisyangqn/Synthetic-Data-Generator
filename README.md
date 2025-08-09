# Synthetic Data Generator (DeepSeek R1 via Ollama)

Generate high-quality synthetic data from zero using DeepSeek R1 models through Ollama. Provide a question list CSV and the tool will create per-question CSVs with realistic answers and short descriptions suitable for NLP training.

## What it does

- Input: a questions CSV with columns:
  - `field_name`: identifier for the field (e.g., `id`, `title`, `status`)
  - `field_question`: the question to synthesize answers for
- Output: per-question CSV files written to `synthetic_data/` with columns:
  - `field_name`, `field_question`, `answer` (short label), `text` (1–2 sentence description)
- Optional legacy mode: given a CSV with a `text` column, the script can enhance each `text` entry in place (backwards compatibility).

## Prerequisites

1. Ollama installed and running
   - Install from `https://ollama.ai`
   - Start the server: `ollama serve`
2. DeepSeek R1 model pulled
   ```bash
   ollama pull deepseek-r1
   # or another variant if available
   ollama pull deepseek-r1:7b
   ```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### A) Zero-shot synthetic generation (recommended)

Provide a questions CSV (example path: `field_name/sample_data.csv`) with headers `field_name,field_question`.

```bash
python ollama_client.py field_name/sample_data.csv
```

- Outputs will be written to `synthetic_data/` as multiple CSVs, one per question.
- Control the number of rows per question with env var `ROWS_PER_QUESTION` (default 100):

```bash
ROWS_PER_QUESTION=200 python ollama_client.py field_name/sample_data.csv
```

### B) Legacy enhancement mode (optional)

If you pass a CSV that contains a `text` column, the tool will enhance the text and write a processed file (compat behavior preserved):

```bash
python ollama_client.py input.csv  # must include a 'text' column
```

### Interactive mode

```bash
python ollama_client.py
```
Follow the prompts to run zero-shot generation from a questions CSV or use the legacy enhancement flow.

## Docker

You can run this tool in Docker. The container expects an Ollama server to be reachable at `OLLAMA_BASE_URL`. By default it uses `http://host.docker.internal:11434` (works on macOS/Windows).

### Build the image
```bash
docker build -t sdg-app .
```

### Run against a questions CSV
```bash
mkdir -p synthetic_data

docker run --rm -it \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e ROWS_PER_QUESTION=150 \
  -v "$PWD/field_name:/app/field_name" \
  -v "$PWD/synthetic_data:/app/synthetic_data" \
  sdg-app field_name/sample_data.csv
```

### Run interactive mode
```bash
docker run --rm -it \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -v "$PWD/field_name:/app/field_name" \
  -v "$PWD/synthetic_data:/app/synthetic_data" \
  sdg-app
```

Tip for Linux: replace `host.docker.internal` with your host IP (often `172.17.0.1`) or run Ollama in a sibling container and network them together (see `docker-compose.yml`).

## Docker Compose

A compose file is included to run Ollama and the app together.

```bash
docker compose up --build
```

- Ollama is exposed on `11434` and the app uses `http://ollama:11434` internally.
- Mounts: `./field_name` for inputs, `./synthetic_data` for outputs.
- Optionally pre-pull models by customizing the Ollama service command.

## Configuration

- `OLLAMA_BASE_URL`: URL of the Ollama server (default `http://127.0.0.1:11434` locally; Dockerfile default points to host).
- `ROWS_PER_QUESTION`: number of synthetic rows to generate per question (default `100`).

## Project structure (key files)

- `ollama_client.py`: main client and CLI (zero-shot generation and legacy enhancement)
- `field_name/`: put your questions CSV(s) here (e.g., `sample_data.csv`)
- `synthetic_data/`: generated outputs (created if missing)
- `Dockerfile`, `docker-compose.yml`: containerization assets
- `requirements.txt`: Python dependencies (minimal)

## Notes

- The tool is model-agnostic but defaults to `deepseek-r1`. You can pass a different model name when constructing `OllamaClient` programmatically.
- If the model returns non-JSON answers in zero-shot mode, the tool attempts robust parsing and falls back to reasonable defaults to ensure the requested number of rows.
