This is the model I use to generate synthetic training data. This version runs on DeepSeek R1 via Ollama. The backbone is swappable—if the task is lighter, I can switch to Meta Llama for a smaller, faster model. I’ve separated the Ollama client from the prompt logic to keep the code modular and easier to maintain.

The tool supports two modes:

1. generate synthetic data from question prompts, and
2. refine existing synthetic text to read more like real contract language or to increase length and detail.

Now I’ll walk through the first capability: generating synthetic data.

# Mode 1

The core function of this pipeline is synthetic data generation, and it follows a three-level call structure.

At the top level, we have **`generate_synthetic_from_questions()`**, which acts as the main controller. It reads the input CSV, typically structured with two columns: field_name and question. The CSV can contain multiple questions, though the sample shown here only includes three.

For each question, the top-level function calls a middle-level function, **`generate_synthetic_for_one_question()`**, which handles interaction with the AI model for that specific question.

Within **`generate_synthetic_for_one_question()`**, it calls the lowest-level function, **`get_synthetic_generation_prompt()`**, which is responsible for constructing the actual prompt used to generate realistic contract-style synthetic data.

So these are the three output files. Since the generation process takes quite a while to run, I pre-ran the model before this meeting. Ideally, we would have 100 rows of synthetic data per field, but to save time, I started with around 25 to 50 rows for each one. I can scale it up later as needed for training.

# Mode 2

The second capability of this pipeline is **text enhancement mode**, which refines existing synthetic text to read more like real contract language and increase length and detail. This mode follows a similar hierarchical structure but focuses on improving existing content rather than generating from scratch.

## Mode 2: Text Enhancement Pipeline

### **Top Level: `process_csv_with_filler_sentences()`**
This function acts as the main controller for text enhancement. It reads an input CSV file that must contain a `text` column with existing synthetic data. The function automatically expands datasets with fewer than 50 rows to meet the minimum requirement, ensuring sufficient data for training purposes.

### **Middle Level: `_generate_enhanced_texts_batch()`**
This function processes multiple texts in batches for efficiency. It analyzes existing text patterns to maintain consistency in style, tone, and format. The batch processing helps optimize API calls while preserving the original text characteristics.

### **Bottom Level: `_generate_enhanced_text()`**
This function handles individual text enhancement by calling `get_text_enhancement_prompt()` to construct prompts that instruct the AI model to add contract-style filler sentences while maintaining the original meaning.

### **Pattern Learning: `_analyze_text_patterns()`**
A key innovation in this mode is the pattern analysis function that examines existing text to identify:
- Common sentence starters and phrases
- Frequently used vocabulary
- Average sentence length and structure
- Writing style characteristics

This analysis ensures that enhanced texts maintain consistency with the original dataset's style and tone.

## Key Features of Mode 2

### **Automatic Data Expansion**
- Input files with fewer than 50 rows are automatically expanded
- Existing rows are duplicated to reach the minimum threshold
- Maintains data integrity while ensuring sufficient training samples

### **Style Consistency**
- Analyzes existing text patterns before enhancement
- Ensures new content matches the original writing style
- Preserves domain-specific terminology and tone

### **Length Standardization**
- All enhanced texts are standardized to 300-400 tokens
- Matches the length requirements of the generation mode
- Provides consistent detail level across all outputs

### **Intelligent Enhancement**
- Adds contract-style filler sentences before and after original text
- Maintains the core meaning while expanding context
- Creates more realistic and comprehensive contract language

## Usage Example

**Input CSV:**
```
text
"The contract expires on December 31, 2024."
"Payment is due within 30 days."
```

**Enhanced Output:**
```
text
"Pursuant to the terms and conditions outlined in this agreement, the contract expires on December 31, 2024. This provision shall remain in effect for the duration of the contract period and may be subject to review and modification as deemed necessary by the contracting parties."
"In accordance with the payment terms specified herein, payment is due within 30 days. This timeline is established to ensure timely processing and may be adjusted based on mutual agreement between the parties involved."
```

This enhancement mode is particularly useful for refining existing synthetic datasets to better match real-world contract language patterns and provide more comprehensive training data for NLP models.