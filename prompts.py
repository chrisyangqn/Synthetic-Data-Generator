"""
Prompt templates and system instructions for the Synthetic Data Generator
"""

# System instructions for different tasks
SYSTEM_INSTRUCTIONS = {
    "synthetic_generation": (
        "You generate realistic, diverse synthetic data answers for contract-like or enterprise datasets. "
        "Focus on creating highly varied and random responses with different formats, styles, and approaches. "
        "Return strictly JSON only, no code fences, no commentary."
    ),
    "text_enhancement": (
        "You enhance text with realistic contract-style filler sentences. "
        "Maintain the original meaning while adding contextually appropriate content. "
        "Learn from the existing text patterns and maintain consistency in style, tone, and format. "
        "The enhanced text should be approximately 300 to 400 tokens long."
    ),
    "batch_enhancement": (
        "You enhance multiple texts with contract-style filler sentences. "
        "Learn from the existing text patterns and maintain consistency in style, tone, and format. "
        "Each enhanced text should be approximately 300 to 400 tokens long. "
        "Return exactly the requested number of responses in the specified format."
    )
}

# Prompt templates
PROMPT_TEMPLATES = {
    "synthetic_generation": (
        "{system_instructions}\n\n"
        "Task: Generate {num_rows} diverse synthetic answers for the question below.\n"
        "Each item must be a JSON object with keys: 'answer' (a short label) and 'text' (a detailed explanation derived directly from the answer). "
        "The 'text' should be a natural, coherent expansion of the 'answer', and must be approximately 300 to 400 tokens long.\n\n"
        "IMPORTANT: Ensure maximum diversity and randomness in both 'answer' and 'text' fields. "
        "Use different formats, styles, and approaches for each response. "
        "Vary the length, tone, and structure of both answers and descriptions. "
        "Include realistic variations, edge cases, and unexpected but valid responses.\n\n"
        "Question (field_name={field_name}): {field_question}\n\n"
        "Return a JSON array with exactly {num_rows} items."
    ),
    
    "text_enhancement": (
        "Add contract-style sentences before and after this text to make it a complete paragraph: \"{original_text}\"\n\n"
        "Learn from the existing text patterns and maintain consistency in style, tone, and format. "
        "The enhanced text should be approximately 300 to 400 tokens long.\n\n"
        "Output only the enhanced paragraph:"
    ),
    
    "batch_enhancement": (
        "Enhance these {batch_size} texts with contract-style filler sentences. "
        "Learn from the existing text patterns and maintain consistency in style, tone, and format. "
        "Each enhanced text should be approximately 300 to 400 tokens long.\n\n"
        "Return exactly {batch_size} numbered responses:\n\n"
        "{texts_list}\n\n"
        "Enhanced:"
    )
}

# Fallback templates for when generation fails
FALLBACK_TEMPLATES = {
    "synthetic_row": {
        "answer": "value_{index}",
        "text": "Synthetic response {index} for {field_name}: {field_question}"
    },
    "enhanced_text": (
        "Pursuant to the terms and conditions outlined in this healthcare policy document, {original_text}. "
        "This provision shall remain in effect for the duration of the policy period and may be subject to "
        "review and modification as deemed necessary by the policy administrator."
    )
}

# Unwanted patterns to clean from responses
UNWANTED_PATTERNS = [
    "I'm sorry for misunderstanding",
    "I'm sorry for any confusion",
    "as an AI model",
    "as an AI Programming Assistant",
    "designed to assist with computer science",
    "specializing in computer science",
    "Please note",
    "(Note:",
    "(Please note",
    "Enhanced paragraph:",
    "Enhanced text:",
    "Output:",
    "Result:"
]

# Configuration constants
CONFIG = {
    "batch_size": 5,  # Number of texts to process in a single batch
    "default_rows_per_question": 100,
    "max_retries": 3
}

def get_synthetic_generation_prompt(field_name: str, field_question: str, num_rows: int) -> str:
    """
    Generate the prompt for synthetic data generation
    
    Args:
        field_name: The field name identifier
        field_question: The question to generate answers for
        num_rows: Number of rows to generate
        
    Returns:
        Formatted prompt string
    """
    return PROMPT_TEMPLATES["synthetic_generation"].format(
        system_instructions=SYSTEM_INSTRUCTIONS["synthetic_generation"],
        num_rows=num_rows,
        field_name=field_name,
        field_question=field_question
    )

def get_text_enhancement_prompt(original_text: str) -> str:
    """
    Generate the prompt for text enhancement
    
    Args:
        original_text: The original text to enhance
        
    Returns:
        Formatted prompt string
    """
    return PROMPT_TEMPLATES["text_enhancement"].format(
        original_text=original_text
    )

def get_batch_enhancement_prompt(texts_list: str, batch_size: int) -> str:
    """
    Generate the prompt for batch text enhancement
    
    Args:
        texts_list: Formatted list of texts to enhance
        batch_size: Number of texts in the batch
        
    Returns:
        Formatted prompt string
    """
    return PROMPT_TEMPLATES["batch_enhancement"].format(
        batch_size=batch_size,
        texts_list=texts_list
    )

def get_fallback_synthetic_row(index: int, field_name: str, field_question: str) -> dict:
    """
    Get a fallback synthetic row when generation fails
    
    Args:
        index: Row index
        field_name: Field name
        field_question: Field question
        
    Returns:
        Dictionary with answer and text
    """
    template = FALLBACK_TEMPLATES["synthetic_row"]
    return {
        "answer": template["answer"].format(index=index),
        "text": template["text"].format(index=index, field_name=field_name, field_question=field_question)
    }

def get_fallback_enhanced_text(original_text: str) -> str:
    """
    Get a fallback enhanced text when generation fails
    
    Args:
        original_text: Original text
        
    Returns:
        Enhanced text with fallback template
    """
    return FALLBACK_TEMPLATES["enhanced_text"].format(original_text=original_text)
