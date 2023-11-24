# polyglot-buddy
Your buddy for language-learning 

# Directory Structure
- feat 1/
  - (contents of feat 1)
- feat 2/
  - (contents of feat 2)
- telebot.py
- README.md

### Telegram Bot and Feature Integration
**telebot.py**: This file connects the two features to the telegram bot and servers as the interface for the project.

### Feature 1
- **bard.py**: Build dataset corpus of language help documents through Google Bard API.
- **generate_documents.py**: Organised the dataset (from Bard's response) according to the type of queries. 
- **generate_queries.py**: Generate paraphrased versions of queries.
- **train_embed_model.py**: Training embedding LM.
- **eval_embed_model.py**: Evaluate the accuracy and f1-score of a selected embedding LM.
- **inference.py**: Return the language help text after supplying a new user query.
- **utils.py**: Document Retrieval for most similar documents based on query.

### Feature 2
- **data_gen.py**: Generate open-ended questions relevant to the passage based on Multiple-Choice Questions
- **retrieve.py**: Retrieve question randomly and return chosen question to the user.
- **check_grammar.py**: Check grammar of user's answer.
- **feedback.py**: Return feedback (on user's answer) to the user


