# Llama Ollama Client

A Python script to interact with Llama models through Ollama, with specialized functionality for processing CSV files and generating enhanced text data for NLP training. The model is used to fulfill and expand text content based on given environments and contexts.

## Prerequisites

1. **Ollama installed and running**
   - Install Ollama from [https://ollama.ai](https://ollama.ai)
   - Start Ollama: `ollama serve`

2. **Llama model pulled**
   ```bash
   ollama pull llama2:7b
   ```
   
   Or for other Llama variants:
   ```bash
   ollama pull llama2:13b
   ollama pull llama2:70b
   ollama pull llama2:7b-chat
   ollama pull llama2:13b-chat
   ```

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### CSV Processing (Primary Function)

The script is designed to process CSV files containing text data and add realistic context-appropriate filler sentences to expand and fulfill the text content for NLP training purposes.

#### Command Line Usage

```bash
# Process a CSV file with auto-generated output name
python ollama_client.py input.csv

# Process a CSV file with custom output name
python ollama_client.py input.csv output.csv
```

#### Interactive Usage

```bash
python ollama_client.py
```

Then follow the prompts to enter input and output CSV file paths.

#### CSV Requirements

- Must contain a `text` column with the input text data
- All other columns will be preserved unchanged
- The script processes each row (excluding header) and updates only the `text` column

#### Example Input CSV Format

```csv
id,text,category,priority
1,Users must provide valid credentials before accessing the system,security,high
2,Data backup is required for all critical information exceeding 1GB,backup,high
```

#### Example Output

The script will transform text like:
```
"Users must provide valid credentials before accessing the system"
```

Into something like:
```
"Pursuant to the terms and conditions outlined in this security policy document, users must provide valid credentials before accessing the system. This provision shall remain in effect for the duration of the session and may be subject to review and modification as deemed necessary by the system administrator."
```

### Programmatic Usage

```python
from ollama_client import OllamaClient

# Initialize client
client = OllamaClient(model_name="llama2:7b")

# Process CSV file
output_path = client.process_csv_with_filler_sentences("input.csv", "output.csv")
print(f"Processed file saved to: {output_path}")

# Generate individual enhanced text
enhanced_text = client._generate_enhanced_text("Original policy text here")
print(enhanced_text)
```

### Custom Model Names

If you're using a different Llama model, specify it when initializing:

```python
client = OllamaClient(model_name="llama2:13b")
```

## Features

- ✅ CSV file processing with text enhancement and fulfillment
- ✅ Realistic context-appropriate filler sentence generation
- ✅ Preservation of all original CSV data (except `text` column)
- ✅ Connection testing to ensure Ollama is running
- ✅ Model availability checking
- ✅ Error handling for network issues and file operations
- ✅ Interactive mode for file processing
- ✅ Command line interface for batch processing

## Sample Data

A sample CSV file `field_name/sample_data.csv` is included to demonstrate the functionality. You can test the script using:

```bash
python ollama_client.py field_name/sample_data.csv
```

The sample data contains 3 rows with the following structure:
- `field_name`: The field identifier (e.g., risk_level)
- `field_question`: The question being asked about the field
- `answer`: The answer category (e.g., Low, Medium, High)
- `text`: The descriptive text that will be enhanced

## Troubleshooting

### "Model not found" error
Make sure you've pulled the correct model:
```bash
ollama list  # See available models
ollama pull llama2:7b  # Pull the model
```

### "Connection refused" error
Make sure Ollama is running:
```bash
ollama serve
```

### "CSV file must contain a 'text' column" error
Ensure your CSV file has a column named exactly `text` (case-sensitive).

### "Input CSV file not found" error
Check that the file path is correct and the file exists.

### Different Ollama URL
If Ollama is running on a different port or host:
```python
client = OllamaClient(base_url="http://localhost:11435")
``