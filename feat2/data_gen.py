import json
import os
import requests
from langchain.prompts import PromptTemplate

template = """Create an short-answer question in {target_language} and the corresponding answer in {target_language} based on the following context
1) A reading comprehension passage, 
2) A sample multiple choice question (MCQ)
3) Options for the MCQ 
4) Answer to the MCQ

The short-answer question has to be abled to be answered using just the passage provided.

Reading Comprehension Passage: {passage}

Sample Multiple Choice Question: {question}

Options for the MCQ:
1: {option_1}
2: {option_2}
3: {option_3}
4: {option_4}

Answer to the MCQ: {correct_option}

The format of your response should be exactly as follows:
Question: <Generated Short-answer Question in target language>
Answer: <Corresponding Answer to generated Short-answer Question>
"""

prompt_template = PromptTemplate(
    input_variables=["target_language", "passage", "question", "option_1", "option_2", "option_3", "option_4", "correct_option"],
    template=template
)

class DataLoader:
    def __init__(self, languages_map, directory, limit=None):
        self.languages_map = languages_map
        self.directory = directory
        self.limit = limit
        self.data = {}
        self._load_data()
    
    def _load_data(self):
        for lang, files in self.languages_map.items():
            if self.limit:
                self.data[lang] = self._read_jsonl(os.path.join(self.directory, files))[:self.limit]
            else:
                self.data[lang] = self._read_jsonl(os.path.join(self.directory, files))

    @staticmethod
    def _read_jsonl(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return [json.loads(line) for line in file]

    def get_language_data(self, lang):
        return self.data.get(lang, [])

class OpenEndedQuestionGenerator:
    def __init__(self, data_loader, output_directory='/common/home/projectgrps/CS425/CS425G6/polyglot-buddy/feat2/output'):
        self.data_loader = data_loader
        self.output_directory = output_directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    def extract_data_from_language(self, lang):
        data = self.data_loader.get_language_data(lang)
        extracted_data = []
        for row in data:
            passage = row['flores_passage']
            question = row['question']
            correct_answer_num = row['correct_answer_num']
            options = [row['mc_answer1'], row['mc_answer2'], row['mc_answer3'], row['mc_answer4']]
            
            extracted_data.append({
                "passage": passage,
                "question": question,
                "options": options,
                "correct_answer_num": correct_answer_num
            })
        return extracted_data

    def convert_to_open_ended(self, passage, question, options, correct_option, language):
        url = "http://localhost:11434/api/generate"

        prompt = prompt_template.format(
            target_language = language,
            passage = passage,
            question = question,
            option_1 = options[0],
            option_2 = options[1],
            option_3 = options[2],
            option_4 = options[3],
            correct_option = correct_option,
        )

        data = {
            "model": "llama2",
            "prompt": prompt,
            "stream": False,
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        generated_dict = response.json()

        # Remove redundant keys
        redundant_keys = ['total_duration', 'context', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration', 'model', 'created_at', 'done']
        for key in redundant_keys:
            generated_dict.pop(key, None)

        # Save the passage its tied to as well
        generated_dict["passage"] = passage
        
        return generated_dict

    def save_to_file(self, data, lang):
        output_file_path = os.path.join(self.output_directory, f'{lang}_short_answer.json')
        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data saved to {output_file_path}")

    def generate(self, lang):
        data = self.extract_data_from_language(lang)
        open_ended_data = []
        for item in data:
            open_ended_data.append(self.convert_to_open_ended(item['passage'], item['question'], item['options'], item['correct_answer_num'], lang))
        print(f"Number of questions and answers for {lang}: {len(open_ended_data)}")
        self.save_to_file(open_ended_data, lang)
        return open_ended_data
    
# Example usage:
languages_map = {
    "Spanish": "spa_Latn.jsonl",
    "French": "fra_Latn.jsonl",
    "German": "deu_Latn.jsonl",
    "Italian": "ita_Latn.jsonl",
    "Mandarin": "zho_Hans.jsonl",
    "English": "eng_Latn.jsonl"
}
directory = "/common/home/projectgrps/CS425/CS425G6/polyglot-buddy/feat2/Belebele"

data_loader = DataLoader(languages_map, directory)
question_generator = OpenEndedQuestionGenerator(data_loader)

for language in languages_map.keys():
    question_generator.generate(language)
