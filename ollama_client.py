# ollama serve

"""
Ollama Client
A simple Python script to interact with Ollama models for text processing
"""

import requests
import json
import sys
import csv
import os
import glob
from typing import Optional, List, Dict


class OllamaClient:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model_name: str = "llama2:7b"):
        """
        Initialize the Ollama client for text processing
        
        Args:
            base_url: Ollama server URL (default: http://127.0.0.1:11434)
            model_name: Name of the model in Ollama (default: llama2:7b)
        """
        self.base_url = base_url
        self.model_name = model_name
        self.api_url = f"{base_url}/api/generate"
    
    def generate_response(self, prompt: str, stream: bool = False) -> str:
        """
        Generate a response from the Ollama model
        
        Args:
            prompt: The input prompt
            stream: Whether to stream the response (default: False)
            
        Returns:
            The generated response text
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            full_response += data['response']
                        if data.get('done', False):
                            break
                return full_response
            else:
                # Handle non-streaming response
                data = response.json()
                return data.get('response', '')
                
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama: {e}")
            return ""
        except json.JSONDecodeError as e:
            print(f"Error parsing response: {e}")
            return ""
    
    def test_connection(self) -> bool:
        """Test if Ollama is running and the model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get('models', [])
            
            for model in models:
                if self.model_name in model.get('name', ''):
                    return True
            
            print(f"Model '{self.model_name}' not found. Available models:")
            for model in models:
                print(f"  - {model.get('name', 'Unknown')}")
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama: {e}")
            print("Make sure Ollama is running and accessible at", self.base_url)
            return False
    
    def process_csv_with_filler_sentences(self, input_csv_path: str, output_csv_path: str = None) -> str:
        """
        Process a CSV file and add realistic contract-style filler sentences to the 'text' column
        
        Args:
            input_csv_path: Path to the input CSV file
            output_csv_path: Path to the output CSV file (optional, will auto-generate if None)
            
        Returns:
            Path to the output CSV file
        """
        if not os.path.exists(input_csv_path):
            raise FileNotFoundError(f"Input CSV file not found: {input_csv_path}")
        
        if output_csv_path is None:
            base_name = os.path.splitext(input_csv_path)[0]
            output_csv_path = f"{base_name}_with_filler.csv"
        
        # Read the CSV file
        rows = []
        with open(input_csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            
            if 'text' not in fieldnames:
                raise ValueError("CSV file must contain a 'text' column")
            
            rows = list(reader)
        
        print(f"Processing {len(rows)} rows from {input_csv_path}")
        
        # Extract all non-empty texts
        texts_to_process = []
        text_indices = []
        
        for i, row in enumerate(rows):
            original_text = row['text'].strip()
            if original_text:
                texts_to_process.append(original_text)
                text_indices.append(i)
        
        print(f"Found {len(texts_to_process)} texts to enhance")
        
        if texts_to_process:
            # Process all texts in a single API call
            print("Generating enhanced texts for all rows...")
            enhanced_texts = self._generate_enhanced_texts_batch(texts_to_process)
            
            # Update the rows with enhanced texts
            for i, enhanced_text in zip(text_indices, enhanced_texts):
                rows[i]['text'] = enhanced_text
        
        # Write the processed data back to CSV
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Processed CSV saved to: {output_csv_path}")
        return output_csv_path
    
    def process_folder(self, input_folder: str = "field_name", output_folder: str = "field_name_final") -> List[str]:
        """
        Process all CSV files in the input folder and save to output folder
        
        Args:
            input_folder: Folder containing input CSV files (default: "field_name")
            output_folder: Folder to save processed CSV files (default: "field_name_final")
            
        Returns:
            List of processed output file paths
        """
        # Check if input folder exists
        if not os.path.exists(input_folder):
            raise FileNotFoundError(f"Input folder not found: {input_folder}")
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Find all CSV files in input folder
        csv_pattern = os.path.join(input_folder, "*.csv")
        csv_files = glob.glob(csv_pattern)
        
        if not csv_files:
            print(f"No CSV files found in {input_folder}")
            return []
        
        print(f"Found {len(csv_files)} CSV files in {input_folder}")
        
        processed_files = []
        
        for csv_file in csv_files:
            # Get just the filename (without path)
            filename = os.path.basename(csv_file)
            output_path = os.path.join(output_folder, filename)
            
            print(f"\n{'='*60}")
            print(f"Processing: {filename}")
            print(f"{'='*60}")
            
            try:
                processed_path = self.process_csv_with_filler_sentences(csv_file, output_path)
                processed_files.append(processed_path)
                print(f"✅ Successfully processed: {filename}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
                continue
        
        return processed_files
    
    def _generate_enhanced_texts_batch(self, original_texts: List[str]) -> List[str]:
        """
        Generate enhanced text for multiple texts in a single API call
        
        Args:
            original_texts: List of original texts from the CSV
            
        Returns:
            List of enhanced texts with filler sentences
        """
        # Process in smaller batches to avoid token limits
        batch_size = 5  # Process 5 texts at a time
        all_enhanced_texts = []
        
        for i in range(0, len(original_texts), batch_size):
            batch_texts = original_texts[i:i+batch_size]
            batch_numbers = list(range(i+1, min(i+batch_size+1, len(original_texts)+1)))
            
            texts_list = "\n".join([f"{batch_numbers[j]}. {text}" for j, text in enumerate(batch_texts)])
            
            prompt = f"""Enhance these {len(batch_texts)} texts with contract-style filler sentences. Return exactly {len(batch_texts)} numbered responses:

{texts_list}

Enhanced:"""
            
            print(f"Processing batch {i//batch_size + 1}/{(len(original_texts) + batch_size - 1)//batch_size} ({len(batch_texts)} texts)...")
            
            response = self.generate_response(prompt)
            
            if response:
                # Parse this batch
                batch_enhanced = self._parse_batch_response(response, len(batch_texts))
                if len(batch_enhanced) == len(batch_texts):
                    all_enhanced_texts.extend(batch_enhanced)
                else:
                    print(f"Batch parsing failed, processing individually...")
                    # Fall back to individual processing for this batch
                    for text in batch_texts:
                        enhanced = self._generate_enhanced_text(text)
                        all_enhanced_texts.append(enhanced)
            else:
                # Fall back to individual processing for this batch
                for text in batch_texts:
                    enhanced = self._generate_enhanced_text(text)
                    all_enhanced_texts.append(enhanced)
        
        return all_enhanced_texts
    
    def _parse_batch_response(self, response: str, expected_count: int) -> List[str]:
        """
        Parse the batch response to extract individual enhanced texts
        
        Args:
            response: The batch response from the model
            expected_count: Expected number of enhanced texts
            
        Returns:
            List of enhanced texts
        """
        # Clean up the response
        response = response.strip()
        
        # Remove unwanted patterns
        unwanted_patterns = [
            "I'm sorry for misunderstanding",
            "I'm sorry for any confusion",
            "as an AI model",
            "as an AI Programming Assistant",
            "designed to assist with computer science",
            "specializing in computer science",
            "Please note",
            "(Note:",
            "(Please note",
            "Enhanced paragraphs:",
            "Enhanced texts:",
            "Output:",
            "Result:"
        ]
        
        # Remove lines with unwanted patterns
        lines = response.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and not any(pattern.lower() in line.lower() for pattern in unwanted_patterns):
                cleaned_lines.append(line)
        
        # Try to parse numbered responses
        enhanced_texts = []
        current_text = ""
        
        for line in cleaned_lines:
            # Check if line starts with a number (new response)
            if line and line[0].isdigit() and '.' in line[:3]:
                if current_text:
                    enhanced_texts.append(current_text.strip())
                current_text = line.split('.', 1)[1].strip() if '.' in line else line
            else:
                if current_text:
                    current_text += " " + line
        
        # Add the last text
        if current_text:
            enhanced_texts.append(current_text.strip())
        
        # If we got the right number, return it
        if len(enhanced_texts) == expected_count:
            return enhanced_texts
        
        # Try alternative parsing - split by double newlines
        enhanced_texts = [text.strip() for text in response.split('\n\n') if text.strip()]
        if len(enhanced_texts) == expected_count:
            return enhanced_texts
        
        # Try splitting by "Enhanced:" or similar markers
        if "Enhanced:" in response:
            parts = response.split("Enhanced:")
            if len(parts) > 1:
                enhanced_part = parts[1].strip()
                enhanced_texts = [text.strip() for text in enhanced_part.split('\n') if text.strip()]
                if len(enhanced_texts) == expected_count:
                    return enhanced_texts
        
        # If we didn't get the expected number, try alternative parsing
        if len(enhanced_texts) != expected_count:
            # Split by double newlines or other separators
            enhanced_texts = [text.strip() for text in response.split('\n\n') if text.strip()]
            
            # If still not right, split by single newlines and group
            if len(enhanced_texts) != expected_count:
                enhanced_texts = []
                lines = [line.strip() for line in response.split('\n') if line.strip()]
                current_group = []
                
                for line in lines:
                    if line and line[0].isdigit() and '.' in line[:3]:
                        if current_group:
                            enhanced_texts.append(' '.join(current_group))
                        current_group = [line.split('.', 1)[1].strip() if '.' in line else line]
                    else:
                        current_group.append(line)
                
                if current_group:
                    enhanced_texts.append(' '.join(current_group))
        
        return enhanced_texts
    
    def _generate_enhanced_text(self, original_text: str) -> str:
        """
        Generate enhanced text with realistic contract-style filler sentences
        
        Args:
            original_text: The original text from the CSV
            
        Returns:
            Enhanced text with filler sentences
        """
        prompt = f"""Add contract-style sentences before and after this text to make it a complete paragraph: "{original_text}"

Output only the enhanced paragraph:"""
        
        response = self.generate_response(prompt)
        
        # Clean up the response
        if response:
            # Remove any quotes or extra formatting
            response = response.strip().strip('"').strip("'")
            
            # Remove common unwanted patterns
            unwanted_patterns = [
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
            
            # Remove lines containing unwanted patterns
            lines = response.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line and not any(pattern.lower() in line.lower() for pattern in unwanted_patterns):
                    cleaned_lines.append(line)
            
            # Join back into a single paragraph
            cleaned_response = ' '.join(cleaned_lines)
            
            # If still empty or problematic, use fallback
            if not cleaned_response or len(cleaned_response) < 20:
                return f"Pursuant to the terms and conditions outlined in this healthcare policy document, {original_text}. This provision shall remain in effect for the duration of the policy period and may be subject to review and modification as deemed necessary by the policy administrator."
            
            return cleaned_response
        else:
            # Fallback if generation fails
            return f"Pursuant to the terms and conditions outlined in this healthcare policy document, {original_text}. This provision shall remain in effect for the duration of the policy period and may be subject to review and modification as deemed necessary by the policy administrator."


def main():
    """Main function with CSV processing capabilities"""
    
    # Initialize the client
    client = OllamaClient()
    
    # Test connection
    print("Testing connection to Ollama...")
    if not client.test_connection():
        print("Failed to connect to Ollama or model not found.")
        print("Please make sure:")
        print("1. Ollama is running (ollama serve)")
        print("2. Llama2 model is pulled (ollama pull llama2:7b)")
        sys.exit(1)
    
    print("✅ Connected to Ollama successfully!")
    
    # Check if folder processing is requested
    if len(sys.argv) > 1 and sys.argv[1] == "--folder":
        input_folder = sys.argv[2] if len(sys.argv) > 2 else "field_name"
        output_folder = sys.argv[3] if len(sys.argv) > 3 else "field_name_final"
        
        try:
            processed_files = client.process_folder(input_folder, output_folder)
            print(f"\n🎉 Folder processing completed successfully!")
            print(f"Processed {len(processed_files)} files")
            print(f"Output folder: {output_folder}")
        except Exception as e:
            print(f"❌ Error processing folder: {e}")
            sys.exit(1)
    # Check if single CSV file is provided as command line argument
    elif len(sys.argv) > 1:
        input_csv = sys.argv[1]
        output_csv = sys.argv[2] if len(sys.argv) > 2 else None
        
        try:
            output_path = client.process_csv_with_filler_sentences(input_csv, output_csv)
            print(f"\n🎉 CSV processing completed successfully!")
            print(f"Output file: {output_path}")
        except Exception as e:
            print(f"❌ Error processing CSV: {e}")
            sys.exit(1)
    else:
        # Interactive mode
        print("\n" + "="*60)
        print("CSV PROCESSING MODE")
        print("="*60)
        print("This script will process CSV files and add realistic contract-style filler sentences")
        print("to the 'text' column for healthcare policy documents.")
        print("\nUsage:")
        print("  python ollama_client.py --folder [input_folder] [output_folder]")
        print("  python ollama_client.py input.csv [output.csv]")
        print("  or run interactively below")
        
        # Interactive CSV processing
        while True:
            try:
                choice = input("\nChoose mode (1 for folder processing, 2 for single file, 3 for quick defaults, 'quit' to exit): ").strip()
                
                if choice.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if choice == '1':
                    # Folder processing mode
                    input_folder = input("Enter input folder path (or press Enter for 'field_name'): ").strip()
                    if not input_folder:
                        input_folder = "field_name"
                        print(f"Using default input folder: {input_folder}")
                    
                    output_folder = input("Enter output folder path (or press Enter for 'field_name_final'): ").strip()
                    if not output_folder:
                        output_folder = "field_name_final"
                        print(f"Using default output folder: {output_folder}")
                    
                    try:
                        processed_files = client.process_folder(input_folder, output_folder)
                        print(f"\n🎉 Folder processing completed successfully!")
                        print(f"Processed {len(processed_files)} files")
                        print(f"Output folder: {output_folder}")
                    except Exception as e:
                        print(f"❌ Error processing folder: {e}")
                
                elif choice == '2':
                    # Single file processing mode
                    input_csv = input("Enter CSV file path: ").strip()
                    
                    if not input_csv:
                        continue
                    
                    output_csv = input("Enter output CSV path (or press Enter for auto-generated name): ").strip()
                    if not output_csv:
                        output_csv = None
                    
                    try:
                        output_path = client.process_csv_with_filler_sentences(input_csv, output_csv)
                        print(f"\n🎉 CSV processing completed successfully!")
                        print(f"Output file: {output_path}")
                    except Exception as e:
                        print(f"❌ Error processing CSV: {e}")
                
                elif choice == '3':
                    # Quick defaults mode - use field_name and field_name_final
                    print("Using default folders: field_name → field_name_final")
                    try:
                        processed_files = client.process_folder("field_name", "field_name_final")
                        print(f"\n🎉 Folder processing completed successfully!")
                        print(f"Processed {len(processed_files)} files")
                        print(f"Output folder: field_name_final")
                    except Exception as e:
                        print(f"❌ Error processing folder: {e}")
                
                else:
                    print("Invalid choice. Please enter 1, 2, 3, or 'quit'.")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main() 