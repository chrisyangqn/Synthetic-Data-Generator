# Prompt Configuration Guide

This guide explains how to customize and extend the prompt templates in the Synthetic Data Generator.

## Overview

The project now uses a modular prompt configuration system with the following files:

- `prompts.py` - Main prompt configuration file
- `ollama_client.py` - Updated to use the new prompt system

## File Structure

```
Synthetic-Data-Generator/
├── prompts.py                    # Main prompt configuration
├── PROMPT_CONFIGURATION.md       # This guide
├── ollama_client.py             # Updated client code
└── ...
```

## Main Prompt Configuration (`prompts.py`)

### System Instructions

```python
SYSTEM_INSTRUCTIONS = {
    "synthetic_generation": (
        "You generate realistic, diverse synthetic data answers for contract-like or enterprise datasets. "
        "Return strictly JSON only, no code fences, no commentary."
    ),
    "text_enhancement": (
        "You enhance text with realistic contract-style filler sentences. "
        "Maintain the original meaning while adding contextually appropriate content."
    ),
    # ... more instructions
}
```

### Prompt Templates

```python
PROMPT_TEMPLATES = {
    "synthetic_generation": (
        "{system_instructions}\n\n"
        "Task: Generate {num_rows} diverse synthetic answers for the question below.\n"
        "Each item must be a JSON object with keys: 'answer' (short label) and 'text' (1-2 sentence description).\n"
        "Question (field_name={field_name}): {field_question}\n\n"
        "Return a JSON array with exactly {num_rows} items."
    ),
    # ... more templates
}
```

### Helper Functions

```python
def get_synthetic_generation_prompt(field_name: str, field_question: str, num_rows: int) -> str:
    """Generate the prompt for synthetic data generation"""
    return PROMPT_TEMPLATES["synthetic_generation"].format(
        system_instructions=SYSTEM_INSTRUCTIONS["synthetic_generation"],
        num_rows=num_rows,
        field_name=field_name,
        field_question=field_question
    )
```

## Customizing Prompts

### 1. Domain-Specific Prompts

You can create domain-specific prompts by modifying the system instructions:

```python
# In prompts.py
SYSTEM_INSTRUCTIONS["healthcare"] = (
    "You generate realistic, diverse synthetic data answers for healthcare and medical datasets. "
    "Return strictly JSON only, no code fences, no commentary. "
    "Ensure all medical terms are accurate and appropriate."
)
```



### 3. Custom Fallback Templates

Define custom fallback templates for different domains:

```python
# In prompts.py
FALLBACK_TEMPLATES["healthcare"] = {
    "synthetic_row": {
        "answer": "medical_value_{index}",
        "text": "Synthetic medical response {index} for {field_name}: {field_question}"
    },
    "enhanced_text": (
        "According to standard medical protocols and healthcare guidelines, {original_text}. "
        "This information is subject to clinical review and may be updated based on the latest "
        "medical research and regulatory requirements."
    )
}
```

## Configuration Options

### Batch Processing

```python
CONFIG = {
    "batch_size": 5,  # Number of texts to process in a single batch
    "default_rows_per_question": 100,
    "max_retries": 3
}
```



## Usage Examples

### Basic Usage

The updated `ollama_client.py` automatically uses the new prompt system:

```bash
python ollama_client.py field_name/sample_data.csv
```





## Best Practices

### 1. Keep Templates Simple

- Use clear, concise language
- Avoid complex formatting
- Maintain consistent structure

### 2. Test Your Prompts

- Always test new prompts with small datasets
- Verify JSON output format
- Check for unwanted patterns in responses

### 3. Use Fallback Templates

- Always provide fallback templates
- Ensure fallbacks are domain-appropriate
- Test fallback scenarios

### 4. Document Changes

- Document any prompt modifications
- Include examples of expected output
- Note any domain-specific requirements

## Troubleshooting

### Common Issues

1. **JSON Parsing Errors**
   - Check prompt format
   - Verify system instructions
   - Test with simpler prompts

2. **Unwanted Patterns**
   - Review `UNWANTED_PATTERNS` list
   - Add new patterns as needed
   - Test pattern removal

3. **Batch Processing Issues**
   - Adjust `batch_size` in CONFIG
   - Check token limits
   - Monitor API response times



## Migration from Old Code

If you're migrating from the old inline prompt system:

1. **Backup your current prompts**
2. **Move prompts to `prompts.py`**
3. **Update imports in `ollama_client.py`**
4. **Test with existing data**
5. **Update any custom scripts**



## Support

For questions or issues with prompt configuration:

1. Check the example files
2. Review the troubleshooting section
3. Test with simple prompts first
4. Consult the main README.md
