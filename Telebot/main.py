from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, CallbackContext, Filters

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
        [InlineKeyboardButton("Spanish", callback_data='spanish')],
        [InlineKeyboardButton("French", callback_data='french')],
        [InlineKeyboardButton("Mandarin", callback_data='mandarin')],
        [InlineKeyboardButton("German", callback_data='german')],
        [InlineKeyboardButton("Italian", callback_data='italian')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # query.edit_message_text(text="Great! First, please choose a language", reply_markup=reply_markup)
    # Send a new message instead of editing the old one
    context.bot.send_message(chat_id=update.effective_chat.id, text="Great! First, please choose a language", reply_markup=reply_markup)


def ask_question(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    context.user_data['language'] = query.data  # Store chosen language for future reference

    # query.edit_message_text(text="What question would you like me to help you with?")

    # Send a new message instead of editing the old one
    context.bot.send_message(chat_id=update.effective_chat.id, text="What question would you like me to help you with?")

def handle_question_response(update: Update, context: CallbackContext) -> None:
    # Assume the user's response is the text of the message
    user_response = update.message.text
    language = context.user_data.get('language', 'the chosen language')

    # Dummy response based on language
    responses = {
        "spanish": "Here are some ways you can do this in Spanish:",
        "french": "Here are some ways you can do this in French:",
        "mandarin": "Here are some ways you can do this in Mandarin:",
        "german": "Here are some ways you can do this in German:",
        "italian": "Here are some ways you can do this in Italian:",
    }

    response = responses.get(language, "Here are some ways you can do this:")
    # Add actual logic to generate response based on user question and language
    follow_up = response + "\n1) qwertyuiop\n2) asdfghjkl\n3) zxcvbnm"

    # Send the follow-up message as a new message
    update.message.reply_text(follow_up)

    # Ask the user if they would like to ask another question with a new message
    question_followup = "Would you like to ask another question?"

    keyboard = [
        [InlineKeyboardButton("Yes, same language", callback_data=f'repeat_{language}')],
        [InlineKeyboardButton("Yes, different language", callback_data='real_time')],
        [InlineKeyboardButton("Done", callback_data='done')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # update.message.reply_text(follow_up, reply_markup=reply_markup)
    # Send the question with buttons as a new message
    context.bot.send_message(chat_id=update.effective_chat.id, text=question_followup, reply_markup=reply_markup)

def done(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    message = "Great! Let me know if you need anything else."

    keyboard = [
        [InlineKeyboardButton("Real-time language assistance", callback_data='real_time')],
        [InlineKeyboardButton("Interactive Language Learning", callback_data='language_learning')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # query.edit_message_text(text=message, reply_markup=reply_markup)
    # Send a new message instead of editing the old one
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup)

# Handler for repeating the question in the same language
def repeat_question(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    language = query.data.split('_')[1]  # Extract the language from the callback data
    context.user_data['language'] = language  # Store the language again for reuse

    # Call the ask_question function directly or copy its contents here
    ask_question(update, context)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# FEATURE 2

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Main function to set up the bot
def main() -> None:
    # Insert your bot's token
    updater = Updater("6623692052:AAEr6l5YByR5mr0LPdLryNCG1JuwhtakcfY")

    dispatcher = updater.dispatcher

    # Handlers for commands and messages
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(real_time_language_assistance, pattern='^real_time$'))
    dispatcher.add_handler(CallbackQueryHandler(ask_question, pattern='^(spanish|french|mandarin|german|italian)$'))
    dispatcher.add_handler(CallbackQueryHandler(repeat_question, pattern='^repeat_(spanish|french|mandarin|german|italian)$'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_question_response))
    dispatcher.add_handler(CallbackQueryHandler(done, pattern='^done$'))
    # Add more handlers for other callback data patterns...

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
