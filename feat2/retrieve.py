import json
import random

def load_random_question(language):
    filename = f'/common/home/projectgrps/CS425/CS425G6/polyglot-buddy/feat2/clean/{language}_short_answer.json'

    with open(filename, 'r') as file:
        data = json.load(file)

    chosen_question = random.choice(data)  # Pick a random question from the JSON object
    
    return chosen_question