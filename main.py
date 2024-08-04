from flask import Flask, request
import requests
import logging
from telegram import Update
from telegram.constants import ParseMode  # Correct import for ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, Dispatcher
import config  # Import the configuration

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

# Initialize Telegram Updater
updater = Updater(config.TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! I am your Gemini AI bot. Send me any message and I will respond!')

def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    chat_id = update.message.chat_id

    try:
        # Call the Google Gemini API
        response = requests.post(
            'https://api.google.com/gemini',  # Replace with the actual API endpoint
            headers={'Authorization': f'Bearer {config.GEMINI_API_KEY}'},
            json={'prompt': user_message}
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        ai_message = response.json().get('response', 'Sorry, I did not get a response.')

        # Send the response back to the user
        update.message.reply_text(ai_message, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        update.message.reply_text("Sorry, I encountered an error. Please try again later.")

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    json_update = request.get_json()
    update = Update.de_json(json_update, updater.bot)
    dispatcher.process_update(update)
    return 'OK'

def main() -> None:
    # Set webhook
    updater.bot.set_webhook(url=config.WEBHOOK_URL)

    # Start Flask app
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
