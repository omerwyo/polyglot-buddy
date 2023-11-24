# polyglot-buddy
Your buddy for language-learning 

# Directory Structure
- feat 1/
  - (contents of feat 1)
- feat 2/
  - (contents of feat 2)
- telebot.py
- README.md
- requirements.txt

### Telegram Bot and Feature Integration
**telebot.py**: This file connects the two features to the telegram bot the interface for the Polyglot Buddy.

### To run this bot
- Install [Ollama](https://github.com/jmorganca/ollama/blob/main/docs/linux.md)
  - `curl https://ollama.ai/install.sh | sh`

- Install dependencies from `requirements.txt`

- In a Slurm environment (SMU's GPU Cluster), submit the `run_bot.sh` script 
  - Modify the absolute filepaths across the folder

### Feature 1
- **bard.py**: Builds dataset of language help documents through Google Bard API.
- **generate_documents.py**: Organises the dataset (from Bard's response) according to the type of queries. 
- **generate_queries.py**: Generates paraphrased versions of queries.
- **train_embed_model.py**: Trains embedding LM.
- **eval_embed_model.py**: Evaluate the accuracy and f1-score of a selected embedding LM.
- **inference.py**: Return the language help text after supplying a new user query.
- **utils.py**: Document Retrieval for most similar documents based on query.

### Feature 2
- **data_gen.py**: Generate open-ended questions relevant to the passage based on Multiple-Choice Questions
- **clean_qa_pairs.py**: Code to pre-process and clean the augmented dataset.
- **retrieve.py**: Retrieve question-answer pair randomly based on the user's target language.
- **feedback.py**: Various functions to collate and output feedback for the user based on their input response