import os
import sys
import logging
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Add src to path just in case
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from agent import Agent

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global Scheduler
scheduler = AsyncIOScheduler()
active_job_ids = set()

# Load env variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = os.getenv("TELEGRAM_USER_ID")

# Pairing Code Logic
PAIRING_PATH = os.path.join(os.path.dirname(__file__), ".pairing")
is_verified = os.path.exists(PAIRING_PATH)

import random
def generate_pairing_code():
    return "".join(random.choices("0123456789", k=6))

# Define states for the /setsoul conversation
SOUL_NAME, SOUL_TITLE, SOUL_PERSONALITY = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    if str(user.id) != AUTHORIZED_USER_ID:
        logger.warning(f"Unauthorized access attempt by {user.id}")
        await update.message.reply_html(
            f"🔒 <b>Access Denied</b>\n\n"
            f"Sili is locked to a specific user. Your Telegram ID is: <code>{user.id}</code>\n\n"
            f"If this is you, please run <code>sili-setup</code> and provide this ID."
        )
        return

    global is_verified
    if not is_verified:
        pairing_code = generate_pairing_code()
        context.user_data['pairing_code'] = pairing_code
        await update.message.reply_html(
            f"✨ <b>SILI Security Sync Initiated</b>\n\n"
            f"Please verify your identity. Your pairing code is:\n"
            f"<code>{pairing_code}</code>\n\n"
            f"Send this code now to finalize the neural link."
        )
        return

    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Sili V16 is active. Send me a goal or use /setsoul to define me."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Takes the user's message, runs it through the Sili agent loop, and returns the final response."""
    user = update.effective_user
    user_id = str(user.id)
    
    if user_id != AUTHORIZED_USER_ID:
        return

    global is_verified
    if not is_verified:
        provided_code = update.message.text
        expected_code = context.user_data.get('pairing_code')
        if provided_code == expected_code:
            is_verified = True
            with open(PAIRING_PATH, "w") as f:
                f.write("verified")
            await update.message.reply_html("✅ <b>Identity Verified.</b> Neural link established. How can I assist you today?")
        else:
            await update.message.reply_text("❌ Invalid pairing code. Send /start to try again.")
        return

    message_text = update.message.text
    processing_message = await update.message.reply_text(f"🧠 Processing goal: '{message_text}'...")

    try:
        loop = asyncio.get_running_loop()
        agent = Agent(user_id=user_id)
        result = await loop.run_in_executor(None, agent.run, message_text, None)
        await processing_message.edit_text(result)
    except Exception as e:
        logger.error(f"Error executing agent task: {e}")
        await processing_message.edit_text(f"❌ Critical error: {str(e)}")

async def list_tools(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lists all available tools and skills to the user."""
    user = update.effective_user
    if str(user.id) != AUTHORIZED_USER_ID: return

    agent = Agent(user_id=str(user.id))
    
    text = "⚒ <b>SILI Master Toolkit & Neural Skillset</b>\n\n"
    
    text += "<b>Core Tools:</b>\n"
    for name in sorted(agent.master_tools.keys()):
        text += f"• <code>/{name}</code>\n"
        
    text += "\n<b>Neural Skills:</b>\n"
    # Group skills by first letter or show top ones if too many
    all_skills = sorted(agent.dynamic_skills.keys())
    for name in all_skills:
        text += f"• <code>/{name}</code>\n"
        
    text += "\n<i>Just send me any instruction in plain English, and I will use these tools automatically.</i>"
    
    # Split message if it's too long for Telegram (4096 chars)
    if len(text) > 4000:
        chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]
        for chunk in chunks:
            await update.message.reply_html(chunk)
    else:
        await update.message.reply_html(text)

async def sync_commands(application: Application):
    """Dynamically updates the Telegram bot menu based on available tools."""
    commands = [
        ("start", "Initialize/Verify the neural link"),
        ("setsoul", "Configure agent's identity"),
        ("tools", "List all 75+ autonomous capabilities"),
        ("help", "Show system usage guide")
    ]
    
    # Add top 20 skills to the menu for quick access
    agent = Agent()
    top_skills = sorted(agent.dynamic_skills.keys())[:20]
    for skill in top_skills:
        commands.append((skill, f"Execute skill: {skill}"))
        
    await application.bot.set_my_commands(commands)
    logger.info(f"Bot commands synchronized. Total: {len(commands)}")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Downloads voice notes and passes the path to the agent for transcription/processing."""
    user_id = str(update.effective_user.id)
    if user_id != AUTHORIZED_USER_ID: return
    
    processing_message = await update.message.reply_text("🎤 Downloading and processing your voice note...")
    try:
        voice_file = await update.message.voice.get_file()
        temp_dir = os.path.join(os.path.dirname(__file__), "tmp")
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, f"{user_id}_voice.ogg")
        await voice_file.download_to_drive(file_path)
        goal = f"I just sent you a voice note located at '{file_path}'. Please use the 'transcribe_audio' tool to listen to it, and then fulfill whatever instruction I gave you in the audio."
        loop = asyncio.get_running_loop()
        agent = Agent(user_id=user_id)
        result = await loop.run_in_executor(None, agent.run, goal, None)
        if os.path.exists(file_path): os.remove(file_path)
        await processing_message.edit_text(result)
    except Exception as e:
        logger.error(f"Error processing voice note: {e}")
        await processing_message.edit_text(f"❌ Failed to process voice note: {str(e)}")

# --- SOUL CONFIGURATION HANDLERS ---
async def setsoul_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversational setup for the Agent's Soul."""
    await update.message.reply_html(
        "🧠 <b>Welcome to the Soul Configurator!</b>\n\n"
        "Let's build your agent's identity. First, what should be the agent's <b>Name</b>?\n"
        "<i>(Send /cancel at any time to abort)</i>"
    )
    return SOUL_NAME

async def setsoul_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['soul_name'] = update.message.text
    await update.message.reply_html(
        f"Got it. The agent is named <b>{context.user_data['soul_name']}</b>.\n\n"
        "What is the agent's <b>Title/Role</b>? (e.g., 'Supreme Commander', 'Cybersecurity Analyst')"
    )
    return SOUL_TITLE

async def setsoul_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['soul_title'] = update.message.text
    await update.message.reply_html(
        f"Role set as <b>{context.user_data['soul_title']}</b>.\n\n"
        "Finally, describe the agent's <b>Personality and Core Directives</b>. How should it behave, talk, and reason?"
    )
    return SOUL_PERSONALITY

async def setsoul_personality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['soul_personality'] = update.message.text
    soul_data = {"name": context.user_data['soul_name'], "title": context.user_data['soul_title'], "personality": context.user_data['soul_personality']}
    soul_path = os.path.join(os.path.dirname(__file__), "soul.json")
    try:
        with open(soul_path, "w") as f: json.dump(soul_data, f, indent=4)
        await update.message.reply_html("✅ <b>Soul Successfully Injected!</b>\n\nSili has been fully reconfigured.")
    except Exception as e: await update.message.reply_text(f"❌ Failed to save soul: {e}")
    return ConversationHandler.END

async def setsoul_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Soul configuration cancelled.")
    return ConversationHandler.END

# --- TEMPORAL SCHEDULER LOGIC ---
async def execute_scheduled_job(job_id: str, goal: str, user_id: str):
    """Executes a cron job by spawning an agent and sending the result back to the user."""
    logger.info(f"Executing scheduled job {job_id}: {goal}")
    try:
        loop = asyncio.get_running_loop()
        agent = Agent(user_id=user_id)
        directive = f"[CRON JOB TRIGGERED] Act autonomously to fulfill the following scheduled goal. Be extremely brief in your final summary.\n\nGOAL: {goal}"
        result = await loop.run_in_executor(None, agent.run, directive, None)
        bot_app = Application.builder().token(TELEGRAM_TOKEN).build()
        async with bot_app.bot:
             await bot_app.bot.send_message(chat_id=user_id, text=f"⏰ <b>Scheduled Agent Task Completed!</b>\n\nGoal: {goal}\n\nResult:\n{result}", parse_mode="HTML")
    except Exception as e: logger.error(f"Failed to execute scheduled job {job_id}: {e}")

def sync_jobs_from_disk():
    """Reads jobs.json and adds any new jobs to the APScheduler."""
    jobs_file = os.path.join(os.path.dirname(__file__), "jobs.json")
    if not os.path.exists(jobs_file): return
    try:
        with open(jobs_file, "r") as f: jobs = json.load(f)
        current_disk_ids = set()
        for j in jobs:
            job_id = j.get("id")
            current_disk_ids.add(job_id)
            if job_id not in active_job_ids:
                cron_str = j.get("cron"); goal = j.get("goal"); user_id = j.get("user_id")
                scheduler.add_job(execute_scheduled_job, CronTrigger.from_crontab(cron_str), id=job_id, args=[job_id, goal, user_id])
                active_job_ids.add(job_id)
                logger.info(f"Added scheduled job: {job_id}")
        for active_id in list(active_job_ids):
             if active_id not in current_disk_ids:
                  scheduler.remove_job(active_id)
                  active_job_ids.remove(active_id)
    except Exception as e: logger.error(f"Error syncing background jobs: {e}")

def main() -> None:
    """Start the bot."""
    if not TELEGRAM_TOKEN or not AUTHORIZED_USER_ID:
        print("\n[ERROR] Telegram Token or User ID missing! Run 'python3 setup.py'.")
        sys.exit(1)
        
    from branding import print_banner
    print_banner()
    print(f"Starting Sili V16 Heartbeat. Target User: {AUTHORIZED_USER_ID}")
    
    # Init application first
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Create a separate function for the startup sequence
    async def post_init(app: Application):
        # Start Scheduler here when loop is definitely running
        if not scheduler.running:
            scheduler.start()
            scheduler.add_job(sync_jobs_from_disk, 'interval', seconds=15)
        await sync_commands(app)

    # Use application's post_init
    application.post_init = post_init

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("tools", list_tools))

    soul_handler = ConversationHandler(
        entry_points=[CommandHandler("setsoul", setsoul_start)],
        states={
            SOUL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, setsoul_name)],
            SOUL_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, setsoul_title)],
            SOUL_PERSONALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, setsoul_personality)],
        },
        fallbacks=[CommandHandler("cancel", setsoul_cancel)],
    )
    application.add_handler(soul_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # run_polling handles the event loop and signal handling
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
