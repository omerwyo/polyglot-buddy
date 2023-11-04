import json
import random

question_dict = {
    "English": [386, 336, 431, 42, 266],
    # "French": [2, 262, 265, 256, 1, 237],
    "French": [2],
    "German": [253, 598, 224, 517, 143],
    "Italian": [73, 36, 194, 25, 159],
    "Spanish": [410, 129, 273, 362, 415],
}

# random.seed(some_seed_value)

def load_random_question(language):
    question_list = question_dict[language]    
    chosen_id = question_list.pop(0)
    question_list.append(chosen_id)

    filename = f'/common/home/projectgrps/CS425/CS425G6/polyglot-buddy/feat2/clean/{language}_short_answer.json'

    with open(filename, 'r') as file:
        data = json.load(file)
    
    chosen_question = data[chosen_id - 1]
    
    return chosen_question
