import os
import threading
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, CallbackContext, Filters, ConversationHandler

from feat1.inference import retrieve_document

from feat2.retrieve import load_random_question
from feat2.feedback import get_answer_feedback

os.environ['TOKENIZERS_PARALLELISM'] = "true"

# Define states
SELECTING_ACTION, SELECTING_LANGUAGE_QUESTION, SELECTING_LANGUAGE_COMPREHENSION, AWAITING_QUESTION, AWAITING_COMPREHENSION_RESPONSE, ASKING_QUESTION_AGAIN, ASKING_COMPREHENSION_AGAIN = range(7)

# Define the callback function for the '/start' command
def start(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.first_name
    message1 = f"Hi there {username}! I am Polyglot Travel Buddy. I am able to help you with:\n"\
               "1) Real-time language assistance - Give me a query and your preferred language and I will provide you with some solutions\n"\
               "2) Interactive Language Learning - Let me know which language you would like to learn and I will provide you with some short comprehension questions as well as the feedback to your responses"
    message2 = "How may I assist you today?"

    keyboard = [
        [InlineKeyboardButton("Real-time language assistance", callback_data='real_time')],
        [InlineKeyboardButton("Interactive Language Learning", callback_data='language_learning')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(message1)
    update.message.reply_text(message2, reply_markup=reply_markup)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# FEATURE 1: Define the callback function for real-time language assistance
def real_time_language_assistance(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    # Display language options as buttons
    keyboard = [
        [InlineKeyboardButton("Spanish", callback_data='Spanish')],
        [InlineKeyboardButton("French", callback_data='French')],
        [InlineKeyboardButton("Mandarin", callback_data='Mandarin')],
        [InlineKeyboardButton("German", callback_data='German')],
        [InlineKeyboardButton("Italian", callback_data='Italian')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=update.effective_chat.id, text="Great! First, please choose a language", reply_markup=reply_markup)

    return SELECTING_LANGUAGE_QUESTION

def ask_question(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    context.user_data['language'] = query.data  # Store chosen language for future reference

    context.bot.send_message(chat_id=update.effective_chat.id, text="What question would you like me to help you with?")

    return AWAITING_QUESTION

def handle_question_response(update: Update, context: CallbackContext) -> None:
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    # Assume the user's response is the text of the message
    user_response = update.message.text
    language = context.user_data.get('language', 'the chosen language')

    follow_up = retrieve_document(user_response, language)

    # Send the follow-up message as a new message
    update.message.reply_text(follow_up)

    # Ask the user if they would like to ask another question with a new message
    question_followup = "Would you like to ask another question?"

    keyboard = [
        [InlineKeyboardButton("Yes, same language", callback_data=language)],
        [InlineKeyboardButton("Yes, different language", callback_data='real_time')],
        [InlineKeyboardButton("Done", callback_data='done')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=update.effective_chat.id, text=question_followup, reply_markup=reply_markup)

    return ASKING_QUESTION_AGAIN

# Callback handler to handle the user's choice to ask another question or not
def handle_second_chance_question(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Directly use the callback data as the language
    if query.data in ['Spanish', 'French', 'Mandarin', 'German', 'Italian']:
        context.user_data['language'] = query.data
        ask_question(update, context)
        return AWAITING_QUESTION

    elif query.data == 'real_time':
        # The user wants to change the language
        real_time_language_assistance(update, context)
        return SELECTING_LANGUAGE_QUESTION

    elif query.data == 'done':
        # The user is done, send the final message
        done(update, context)
        return SELECTING_ACTION

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# FEATURE 2
# Callback handler for 'Interactive Language Learning' button
def interactive_language_learning(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton("Spanish", callback_data='Spanish')],
        [InlineKeyboardButton("French", callback_data='French')],
        [InlineKeyboardButton("Mandarin", callback_data='Mandarin')],
        [InlineKeyboardButton("German", callback_data='German')],
        [InlineKeyboardButton("Italian", callback_data='Italian')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Great! First, please choose a language", reply_markup=reply_markup)

    return SELECTING_LANGUAGE_COMPREHENSION

# Callback handler to display comprehension question
def display_comprehension_question(update: Update, context: CallbackContext) -> None:
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    query = update.callback_query
    query.answer()
    language = query.data
    context.user_data['language_learning'] = language  # Store the language for future reference

    passage_question_answer = load_random_question(language)

    # Store the id of the question for future reference
    context.user_data['feat2_curr_question_id'] = passage_question_answer['id']

    question_text = f"Here is a comprehension passage and a question for {language}\nPassage: {passage_question_answer['passage']}\n\nQuestion: {passage_question_answer['question']}"

    context.bot.send_message(chat_id=update.effective_chat.id, text=question_text)

    return AWAITING_COMPREHENSION_RESPONSE

def send_typing_action(context, chat_id, stop_event):
    while not stop_event.is_set():
        context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(3)  # Sleep for the duration of the 'typing' action visibility

# Handler for user's response to the comprehension question
def handle_comprehension_response(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    stop_typing_event = threading.Event()
    typing_thread = threading.Thread(target=send_typing_action, args=(context, chat_id, stop_typing_event))
    typing_thread.start()

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    user_response = update.message.text
    language = context.user_data.get('language_learning')

    # This question ID is required to retrieve the correct answer from the stored data so that we can give feedback based off of it
    curr_qn_id = context.user_data['feat2_curr_question_id']

    feedback_text = get_answer_feedback(language, curr_qn_id, user_response.strip())

    # Stop the typing action
    stop_typing_event.set()
    typing_thread.join()

    # Ask if the user wants to try another question
    question_followup = "Would you like to try another comprehension question?"

    keyboard = [
        [InlineKeyboardButton("Yes, same language", callback_data=language)],
        [InlineKeyboardButton("Yes, different language", callback_data='interactive_language_learning')],
        [InlineKeyboardButton("Done", callback_data='done')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(feedback_text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=question_followup, reply_markup=reply_markup)

    return ASKING_COMPREHENSION_AGAIN

# Callback handler to handle the user's choice to try another comprehension question or not
def handle_second_chance_comprehension(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Directly use the callback data as the language
    if query.data in ['Spanish', 'French', 'Mandarin', 'German', 'Italian']:
        context.user_data['language_learning'] = query.data
        display_comprehension_question(update, context)
        return AWAITING_COMPREHENSION_RESPONSE

    elif query.data == 'interactive_language_learning':
        # The user wants to change the language
        interactive_language_learning(update, context)
        return SELECTING_LANGUAGE_COMPREHENSION

    elif query.data == 'done':
        # The user is done, send the final message
        done(update, context)
        return SELECTING_ACTION

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Changes to be made: write a conditional to return either SELECTING_LANGUAGE_QUESTION or SELECTING_LANGUAGE_COMPREHENSION
def done(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    message = "Great! Let me know if you need anything else."

    keyboard = [
        [InlineKeyboardButton("Real-time language assistance", callback_data='real_time')],
        [InlineKeyboardButton("Interactive Language Learning", callback_data='language_learning')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup)

    return SELECTING_ACTION

def after_done(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Directly use the callback data as the language
    if query.data == 'real_time':
        real_time_language_assistance(update, context)
        return SELECTING_LANGUAGE_QUESTION

    elif query.data == 'language_learning':
        # The user wants to change the language
        interactive_language_learning(update, context)
        return SELECTING_LANGUAGE_COMPREHENSION

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ 

# Define your ConversationHandler
conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', start),
        CallbackQueryHandler(real_time_language_assistance, pattern='^real_time$'),
        CallbackQueryHandler(interactive_language_learning, pattern='^language_learning$')
    ],
    states={
        SELECTING_ACTION: [
            CallbackQueryHandler(after_done, pattern='^(real_time|language_learning)$')
        ],
        SELECTING_LANGUAGE_QUESTION: [
            CallbackQueryHandler(ask_question, pattern='^(Spanish|French|Mandarin|German|Italian)$'),
            CallbackQueryHandler(done, pattern='^done$'),  # Allow "done" to be called here
        ],
        SELECTING_LANGUAGE_COMPREHENSION: [
            CallbackQueryHandler(display_comprehension_question, pattern='^(Spanish|French|Mandarin|German|Italian)$'),
            CallbackQueryHandler(done, pattern='^done$'),  # Allow "done" to be called here
        ],
        AWAITING_QUESTION: [
            MessageHandler(Filters.text & ~Filters.command, handle_question_response)
        ],
        AWAITING_COMPREHENSION_RESPONSE: [
            MessageHandler(Filters.text & ~Filters.command, handle_comprehension_response)
        ],
        ASKING_QUESTION_AGAIN: [
            CallbackQueryHandler(handle_second_chance_question, pattern='^(Spanish|French|Mandarin|German|Italian|real_time|done)$')
        ],
        ASKING_COMPREHENSION_AGAIN: [
            CallbackQueryHandler(handle_second_chance_comprehension, pattern='^(Spanish|French|Mandarin|German|Italian|interactive_language_learning|done)$')
        ]
    },
    fallbacks=[
        CommandHandler('start', start)
    ],
)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Main function to set up the bot
def main() -> None:
    # Jian Yi bot token
    # updater = Updater("6623692052:AAEr6l5YByR5mr0LPdLryNCG1JuwhtakcfY")

    # Khai Soon bot token
    updater = Updater("6702133422:AAHWL7IDtrh9N6RNS1iUp4N-FogK7Ye9YhM")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(conv_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
