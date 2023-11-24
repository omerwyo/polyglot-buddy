import json
import re
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from language_tool_python import LanguageTool

# Set seed for langdetect for reproducibility
DetectorFactory.seed = 0

# File names and their corresponding languages for LanguageTool
files_languages = {
    'Spanish_short_answer.json': 'es',
    'German_short_answer.json': 'de',
    'English_short_answer.json': 'en',
    'Italian_short_answer.json': 'it',
    'French_short_answer.json': 'fr',
}

question_pattern = re.compile(r"Question:\s*(.+?)\n")
answer_pattern = re.compile(r"Answer:\s*(.+?)(?=\n|$)")

# Function to validate text in a specified language
def is_valid_text(text, expected_language, language_tool):
    try:
        # Check if the text is detected as the expected language
        if detect(text) != expected_language:
            return False
    except LangDetectException:
        return False

    # Check for grammar issues with LanguageTool
    matches = language_tool.check(text)
    return len(matches) == 0

for file_name, language_code in files_languages.items():
    print(f"\nProcessing {file_name} for language {language_code}")

    # Initialize LanguageTool context manager for the specific language
    with LanguageTool(language_code) as language_tool:
        # Load the JSON data from the file
        with open(f'./output/{file_name}', 'r', encoding='utf-8') as file:
            data = json.load(file)

        transformed_data = []
        valid_pairs_count = 0
        total = len(data)

        for idx, item in enumerate(data, 1):
            print(f"Processing item {idx}/{total}...")
            response = item['response']
            passage = item.get('passage', '')  # Retrieve the passage

            # Extract the question and answer using regular expressions
            question_match = question_pattern.search(response)
            answer_match = answer_pattern.search(response)

            if question_match and answer_match:
                question = question_match.group(1).strip()
                answer = answer_match.group(1).strip()

                # Check if both the question and the answer are valid in the specified language, and no grammar issues in the question and correct answer
                if is_valid_text(question, language_code, language_tool) and is_valid_text(answer, language_code, language_tool):
                    # Add a cleaned, valid question and answer with the passage to the transformed data list
                    transformed_data.append({
                        "id": valid_pairs_count + 1,
                        "passage": passage,
                        "question": question,
                        "answer": answer
                    })
                    valid_pairs_count += 1
                    print(f"Added pair {valid_pairs_count} to transformed data.")

    # Save the transformed data back to a JSON file
    transformed_file_name = f"./clean/{file_name}"
    with open(transformed_file_name, 'w', encoding='utf-8') as file:
        json.dump(transformed_data, file, ensure_ascii=False, indent=4)

    print(f"Transformation complete for {file_name}. {valid_pairs_count} valid pairs created.")
