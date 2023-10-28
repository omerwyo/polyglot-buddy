import json
import os
import requests

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
    def __init__(self, data_loader, output_directory='./output'):
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
        data = {
            "model": "llama2",
            "prompt": f"Passage: {passage}\nQuestion: {question}\nMultiple Choices:\n 1:{options[0]}\n2:{options[1]}\n3:{options[2]}\n4:{options[3]}\nCorrect Answer: {correct_option}\nGiven the above, convert the question to an open-ended question in {language} that can be answered by a user based on only information provided in the passage. Then, also provide the corresponding answer in {language}.The format of your response should be exactly\nQuestion: <Generated Question in target language>\nAnswer: <Corresponding Answer to generated question>",
            "stream": False,
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        generated_dict = response.json()

        # Remove redundant keys
        redundant_keys = ['total_duration', 'context', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration', 'model']
        for key in redundant_keys:
            generated_dict.pop(key, None)
        
        return generated_dict

    def save_to_file(self, data, lang):
        output_file_path = os.path.join(self.output_directory, f'{lang}_open_ended.json')
        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data saved to {output_file_path}")

    def generate(self, lang):
        data = self.extract_data_from_language(lang)
        open_ended_data = []
        for item in data:
            open_ended_data.append(self.convert_to_open_ended(item['passage'], item['question'], item['options'], item['correct_answer_num'], lang))
        self.save_to_file(open_ended_data, lang)
        return open_ended_data
    
# Example usage:
languages_map = {
    "Spanish": "spa_Latn.jsonl",
    "French": "fra_Latn.jsonl",
    "German": "deu_Latn.jsonl",
    "Italian": "ita_Latn.jsonl",
    "Chinese": "zho_Hans.jsonl",
    "English": "eng_Latn.jsonl"
}
directory = "./Belebele"

data_loader = DataLoader(languages_map, directory, limit=10)
question_generator = OpenEndedQuestionGenerator(data_loader)

for language in languages_map.keys():
    question_generator.generate(language)
