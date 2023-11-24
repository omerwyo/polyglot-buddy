import language_tool_python
from langchain.prompts import PromptTemplate
import json
import requests
from sentence_similarity import sentence_similarity

feedback_template = """Given a passage in {language}, a question, a correct answer and my response to the question, come up with some feedback for me.

Apart from giving you the above information, you have some analysis from a rule-based grammar checker, as well as the semantic similarity score between the correct answer and my answer. Do not mention the explicit similarity score. Give the feedback in English, as that is my native language, and quote my mistakes in {language}.

Passage: {passage}
Question: {question}
User's Answer: {user_answer}
Correct Answer: {correct_answer}

Grammar Check Analysis: 
{grammar_matches}

Semantic Similarity Score: {semantic_similarity_score}
"""

feedback_prompt_template = PromptTemplate(
    input_variables=["language", "passage", "question", "user_answer", "correct_answer", "semantic_similarity_score", "grammar_matches"],
    template=feedback_template
)

language_tool_map = {
    'Spanish': language_tool_python.LanguageTool('es'),
    'German': language_tool_python.LanguageTool('de'),
    'English': language_tool_python.LanguageTool('en'),
    'Italian': language_tool_python.LanguageTool('it'),
    'French': language_tool_python.LanguageTool('fr'),
}

def get_from_ollama(prompt, model="llama2"):
    url = "http://localhost:11434/api/generate"
    print(prompt)

    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        # "temperature": 0.7,
        "options": {
            "temperature": 0.7,
            "seed": 42,
            # "num_predict": 100,
            "top_k": 30,
            "top_p": 1,
            # "repeat_last_n": 64,
            # "num_gpu": 2,
        }
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    generated_dict = response.json()

    if 'total_duration' in generated_dict.keys(): print(f"Total Duration: {generated_dict['total_duration']}")
    if 'eval_duration' in generated_dict.keys(): print(f"Eval Duration: {generated_dict['eval_duration']}")
    if 'prompt_eval_duration' in generated_dict.keys(): print(f"Prompt Eval Duration: {generated_dict['prompt_eval_duration']}")    

    # Remove redundant keys
    redundant_keys = ['total_duration', 'context', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration', 'model', 'created_at']
    for key in redundant_keys:
        generated_dict.pop(key, None)

    return generated_dict['response'] if generated_dict['done'] == True else "Unable to provide feedback :/"

def get_from_llama_cpp(prompt):
    url = "http://localhost:8912/completion"

    print(prompt)

    data = {
        "prompt": prompt,
        "stream": False,
        "temperature": 0.8,
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    generated_dict = response.json()

    print(generated_dict)

    return generated_dict['content']

def get_grammar_matches(language, user_answer):
    tool = language_tool_map[language]
    return tool.check(user_answer)

def compare_sentences(sentence_1=str, sentence_2=str, model_name="sentence-transformers/distiluse-base-multilingual-cased-v1", embedding_type="cls_token_embedding", metric="cosine") -> str:
    model = sentence_similarity(model_name=model_name, embedding_type=embedding_type)
    score = model.get_score(sentence_1, sentence_2, metric=metric)
    return score

def process_matches(matches):
    # Process each match separately
    processed_matches = []
    for match in matches:
        # Split the match into lines and remove the first line
        match = str(match)
        lines = match.strip().split('\n')
        if len(lines) > 2:
            processed_match = '\n'.join(lines[1:-2])  # Skip the first and last line
        else:
            processed_match = match
        processed_matches.append(processed_match.strip())

    # Add numbering and combine all matches
    result = '\n\n'.join(f"{i+1}.\n{match}" for i, match in enumerate(processed_matches))
    return result

def clean_string(s):
    # Replace curly apostrophes with straight ones
    s = s.replace('‘', "'").replace('’', "'")
    # Replace other typographic quotes if necessary
    s = s.replace('“', '"').replace('”', '"')
    return s

def get_answer_feedback(language, question_id, user_answer):
    matches = get_grammar_matches(language, user_answer)
    
    filename = f'/common/home/projectgrps/CS425/CS425G6/polyglot-buddy/feat2/clean/{language}_short_answer.json'

    formatted_matches = process_matches(matches)

    with open(filename, 'r') as file:
        data = json.load(file)

    passage_question_answer = data[question_id - 1]
    
    # Get semantic similarity score between user's answer and our answer, TODO: Uncomment
    # semantic_similarity_score = compare_sentences(user_answer, passage_question_answer['answer'])
    # print(f"Semantic Similarity score: {semantic_similarity_score}")

    prompt = """Given a passage in French, a question, a correct answer and my response to the question, come up with some feedback for me.

Apart from giving you the above information, you have some analysis from a rule-based grammar checker, as well as the semantic similarity score between the correct answer and my answer. Do not mention the explicit similarity score. Give the feedback in English, as that is my native language, and quote my mistakes in French.

Passage: Les colonisateurs, ayant repéré cette activité, avaient également appelé des renforts. Les troupes renforçant les positions avancées comprenaient les 1er et 3e régiments du New Hampshire de 200 hommes, sous les ordres des colonels John Stark et James Reed (tous deux devenus généraux par la suite). Les hommes de Stark ont pris position le long de la clôture, à l'extrémité nord de la position du colon. Lorsque la marée basse a creusé un écart le long de la Mystic River dans le nord-est de la presqu'île, on a rapidement agrandi la barrière par un muret de pierre au nord se terminant au bord de l'eau sur une petite plage. Gridley ou Stark a placé un pieu à environ 30 mètres devant la clôture et a ordonné que personne ne tire avant que les habitués ne la franchissent.
Question: Où étaient les troupes du colonel Stark situées ?
User's Answer: Les troupe du colonel Stark était situé à l'extrémitée nord, le long de la clôture.
Correct Answer: Les troupes du colonel Stark étaient situées à l'extrémité nord, le long de la clôture.

Grammar Check Analysis:
1. 
Message: 'Les' et le nom 'troupe' ne semblent pas bien accordés.
Suggestion: La troupe; Les troupes

2. 
Message: Le mot masculin « situé » n'est pas accordé en genre avec le mot féminin « ».
Suggestion: située

3.
Message: Faute de frappe possible trouvée.
Suggestion: extrémité; extrémités; extrémisée; extrémité e

Semantic Similarity Score: 0.944
"""

    # prompt = feedback_prompt_template.format(
    #     language = language,
    #     passage = passage_question_answer['passage'],
    #     question = passage_question_answer['question'],
    #     user_answer = user_answer,
    #     correct_answer = passage_question_answer['answer'],
    #     semantic_similarity_score = semantic_similarity_score,
    #     grammar_matches = formatted_matches,
    # )

    # prompt = clean_string(prompt)

    return get_from_ollama(prompt, model="vicuna")