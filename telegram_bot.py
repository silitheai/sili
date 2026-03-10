import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Add src to path just in case
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from agent import Agent

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load env variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I am OpenClaw. Send me a goal or task, and I will execute it autonomously."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Takes the user's message, runs it through the OpenClaw agent loop, and returns the final response."""
    user_id = str(update.effective_user.id)
    message_text = update.message.text
    
    # Notify user that the agent has started processing
    processing_message = await update.message.reply_text(f"🧠 Processing goal: '{message_text}'...")

    try:
        # Run agent synchronously in a separate thread/executor to avoid blocking the Telegram async loop
        # We pass user_id so memory works uniquely for different chat users
        loop = asyncio.get_running_loop()
        agent = Agent(user_id=user_id)
        
        # Note: The agent block can take a long time to run (multiple ReAct steps)
        result = await loop.run_in_executor(None, agent.run, message_text, None)
        
        # Return the final summary
        await processing_message.edit_text(result)
        
    except Exception as e:
        logger.error(f"Error executing agent task: {e}")
        await processing_message.edit_text(f"❌ Critical error while processing task: {str(e)}")


def main() -> None:
    """Start the bot."""
    if not TELEGRAM_TOKEN:
        print("\n[ERROR] Telegram Token not found! Please run 'python3 setup.py' to configure it, or add it to your .env file.")
        sys.exit(1)
        
    print("Starting OpenClaw Telegram Bot...")
    
    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))

    # on non command i.e message - pass to agent
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
