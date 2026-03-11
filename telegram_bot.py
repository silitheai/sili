import os
import sys
import logging
import asyncio
import json
import html
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Add src to path just in case
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from agent import Agent
from brain.ollama_manager import OllamaManager

# Global Agent Instance (V16.7 Speed)
global_agent = None

def get_agent(user_id):
    global global_agent
    if global_agent is None:
        global_agent = Agent(user_id=user_id)
    return global_agent

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
    processing_message = await update.message.reply_text(f"🧠 Sili is reasoning...")

    try:
        # 1. Immediate Ollama Check (Async)
        om = OllamaManager()
        text_model = os.getenv("TEXT_MODEL", "llama3.1")
        if not await om.is_model_available(text_model):
            await processing_message.edit_text(f"⚠️ **Model '{text_model}' is missing.**\nPlease use /select_model to pick an available local model.")
            return

        # 2. Background Typing Indicator
        async def send_typing():
            while True:
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
                await asyncio.sleep(4)
        
        typing_task = asyncio.create_task(send_typing())
        
        # 3. Neural Step Callback (V16.15 Live Feedback Heartbeat)
        async def update_progress(current_step, max_steps, status="Neural Processing"):
            try:
                # Update on every step now that we have status awareness
                progress_bar = "".join(['●' if i < current_step % 5 else '◌' for i in range(5)])
                await processing_message.edit_text(
                    f"🧬 **Neural Activity: {status}**\n"
                    f"<code>[ {progress_bar} ] Sili Step {current_step}</code>\n"
                    f"<i>Core: {text_model}</i>",
                    parse_mode="HTML"
                )
            except: pass

        # 4. Neural Execution (Non-blocking Async with Global Watchdog)
        agent = get_agent(user_id=user_id)
        
        logger.info(f"Neural Loop Start: {message_text}")
        start_time = datetime.now()
        
        # V16.11: Global 60-minute watchdog (User requested "no limit", but 1h is a safe practical bound)
        try:
            result = await asyncio.wait_for(
                agent.run(message_text, None, step_callback=update_progress),
                timeout=3600.0
            )
        except asyncio.TimeoutError:
            result = "❌ **Neural Exhaustion**: The goal exceeded 60 minutes. This usually indicates a loop or extreme hardware latency."
        
        # Cleanup
        typing_task.cancel()
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Neural Loop Finished in {duration:.2f}s")
        
        # V16.14: Robust Delivery Singularity
        try:
            # Try sending as HTML first for markdown support
            await processing_message.edit_text(result, parse_mode="HTML")
        except Exception as e:
            if "Can't parse entities" in str(e) or "unsupported start tag" in str(e):
                logger.warning(f"HTML Parse failed, falling back to plaintext: {e}")
                # Fallback: Escape all HTML and send as plaintext
                safe_text = html.escape(result)
                try:
                    await processing_message.edit_text(result, parse_mode=None)
                except:
                    await processing_message.edit_text("⚠️ Neural Output was too complex for Telegram. Check terminal for details.")
            else:
                await processing_message.edit_text(f"❌ Neural Fault: {str(e)}")
    except Exception as e:
        logger.error(f"Error executing agent task: {e}")
        if 'typing_task' in locals(): typing_task.cancel()
        # Ensure we always provide feedback
        try:
            await processing_message.edit_text(f"❌ Neural Fault: {str(e)}")
        except: pass

async def list_tools(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lists all available tools and skills to the user."""
    user = update.effective_user
    if str(user.id) != AUTHORIZED_USER_ID: return

    agent = get_agent(user_id=str(user.id))
    
    # Check if this is a callback query or a direct command
    target = update.message if update.message else update.callback_query.message
    
    text = "⚒ <b>SILI Master Toolkit & Neural Skillset</b>\n\n"
    
    text += "<b>Core Tools:</b>\n"
    for name in sorted(agent.master_tools.keys()):
        text += f"• <code>/{name}</code>\n"
        
    text += "\n<b>Neural Skills:</b>\n"
    all_skills = sorted(agent.dynamic_skills.keys())
    for name in all_skills:
        text += f"• <code>/{name}</code>\n"
        
    text += "\n<i>Just send me any instruction in plain English, and I will use these tools automatically.</i>"
    
    if len(text) > 4000:
        chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]
        for chunk in chunks:
            await target.reply_html(chunk) if update.message else await target.edit_text(chunk, parse_mode="HTML")
    else:
        await target.reply_html(text) if update.message else await target.edit_text(text, parse_mode="HTML")

async def sync_commands(application: Application):
    """Dynamically updates the Telegram bot menu based on available tools."""
    commands = [
        ("start", "Initialize/Verify the neural link"),
        ("setsoul", "Configure agent's identity"),
        ("tools", "List all 75+ autonomous capabilities"),
        ("select_model", "Switch local Ollama models"),
        ("ollama", "Check LLM health & models"),
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
        
        agent = get_agent(user_id=user_id)
        result = await agent.run(goal, None)
        
        if os.path.exists(file_path): os.remove(file_path)
        await processing_message.edit_text(result)
    except Exception as e:
        logger.error(f"Error processing voice note: {e}")
        await processing_message.edit_text(f"❌ Failed to process voice note: {str(e)}")

async def select_model_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dynamic Model discovery and selection (V16.9)."""
    user = update.effective_user
    if str(user.id) != AUTHORIZED_USER_ID: return
    
    om = OllamaManager()
    models = await om.list_local_models()
    
    if not models:
        await update.message.reply_text("❌ No local models found. Run `ollama pull llama3.1` first.")
        return

    keyboard = []
    # Vision models grouped
    vision_models = [m for m in models if "vision" in m.lower() or "llava" in m.lower()]
    text_models = [m for m in models if m not in vision_models]

    for model in text_models[:8]:
        keyboard.append([InlineKeyboardButton(f"🧠 {model}", callback_data=f"sel_model:{model}")])
    
    for model in vision_models[:4]:
        keyboard.append([InlineKeyboardButton(f"👁 {model}", callback_data=f"sel_model:{model}")]) # Use sel_model for simplicity

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(
        "🧠 <b>Neural Hub: Model Selection</b>\n\n"
        f"Currently using: <code>{os.getenv('TEXT_MODEL', 'llama3.1')}</code>\n\n"
        "Select a core model to switch Sili's primary intelligence:",
        reply_markup=reply_markup
    )

async def ollama_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check local Ollama health and running models."""
    user = update.effective_user
    if str(user.id) != AUTHORIZED_USER_ID: return
    
    from src.skills.ollama_status import ollama_status
    # Wrap sync skill
    status = await asyncio.to_thread(ollama_status)
    
    target = update.message if update.message else update.callback_query.message
    if update.message:
        await target.reply_html(status)
    else:
        await target.edit_text(status, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]))

# --- SOUL CONFIGURATION HANDLERS ---
async def setsoul_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversational setup for the Agent's Soul."""
    target = update.message if update.message else update.callback_query.message
    await target.reply_html(
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

# --- INLINE KEYBOARD MENU HANDLERS ---
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays an interactive menu with buttons."""
    user = update.effective_user
    if str(user.id) != AUTHORIZED_USER_ID: return

    keyboard = [
        [
            InlineKeyboardButton("⚒ Master Tools", callback_data="list_tools"),
            InlineKeyboardButton("🧠 Neural Skills", callback_data="list_skills")
        ],
        [
            InlineKeyboardButton("🌀 Switch Model", callback_data="select_model_btn"),
            InlineKeyboardButton("🔌 Ollama Status", callback_data="ollama_status")
        ],
        [
            InlineKeyboardButton("👤 Soul Config", callback_data="set_soul"),
            InlineKeyboardButton("❓ Help & Usage", callback_data="show_help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(
        "🪐 <b>SILI NEURAL INTERACTIVE MENU</b>\n\n"
        "Welcome to the Infinite Mind command center. Select a module to explore your agent's capabilities.",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button presses from the interactive menu."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    if user_id != AUTHORIZED_USER_ID: return

    if query.data == "list_tools":
        agent = get_agent(user_id=user_id)
        text = "⚒ <b>Master Toolkit</b>\n\n"
        for name in sorted(agent.master_tools.keys()):
            text += f"• <code>/{name}</code>\n"
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif query.data == "list_skills":
        agent = get_agent(user_id=user_id)
        text = "🧠 <b>Neural Skillset</b>\n\n"
        for name in sorted(agent.dynamic_skills.keys()):
            text += f"• <code>/{name}</code>\n"
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "ollama_status":
        await ollama_status_command(update, context)
        
    elif query.data == "set_soul":
        await query.edit_message_text("Initiating Soul Configuration Wizard... Run /setsoul to begin.")
        
    elif query.data == "show_help":
        help_text = "📖 <b>SILI Help Guide</b>\n\n1. Send any goal in plain English.\n2. Use /menu for interactive exploration.\n3. Type /ollama to check connection."
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        await query.edit_message_text(help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif query.data == "select_model_btn":
        om = OllamaManager()
        models = await om.list_local_models()
        keyboard = []
        for model in models[:10]:
            keyboard.append([InlineKeyboardButton(f"🤖 {model}", callback_data=f"sel_model:{model}")])
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")])
        await query.edit_message_text("🧠 <b>Neural Hub</b>\nSelect model:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("sel_model:"):
        model_name = query.data.split(":")[1]
        os.environ["TEXT_MODEL"] = model_name
        global global_agent
        if global_agent:
            global_agent.llm.text_model = model_name
        
        try:
            with open(".env", "r") as f: lines = f.readlines()
            with open(".env", "w") as f:
                found = False
                for line in lines:
                    if line.startswith("TEXT_MODEL="):
                        f.write(f"TEXT_MODEL={model_name}\n")
                        found = True
                    else: f.write(line)
                if not found: f.write(f"TEXT_MODEL={model_name}\n")
        except: pass

        await query.answer(f"Model switched to {model_name}")
        await query.edit_message_text(f"✅ <b>Intelligence Shifted</b>\n\nSili is now running on: <code>{model_name}</code>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]))

    elif query.data == "back_to_menu":
        keyboard = [
            [InlineKeyboardButton("⚒ Master Tools", callback_data="list_tools"),
             InlineKeyboardButton("🧠 Neural Skills", callback_data="list_skills")],
            [InlineKeyboardButton("🌀 Switch Model", callback_data="select_model_btn"),
             InlineKeyboardButton("🔌 Ollama Status", callback_data="ollama_status")],
            [InlineKeyboardButton("👤 Soul Config", callback_data="set_soul")],
            [InlineKeyboardButton("❓ Help & Usage", callback_data="show_help")]
        ]
        await query.edit_message_text(
            "🪐 <b>SILI NEURAL INTERACTIVE MENU</b>\n\n"
            "Welcome to the Infinite Mind command center. Select a module to explore.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# --- TEMPORAL SCHEDULER LOGIC ---
async def execute_scheduled_job(job_id: str, goal: str, user_id: str):
    """Executes a cron job by spawning an agent and sending the result back to the user."""
    logger.info(f"Executing scheduled job {job_id}: {goal}")
    try:
        agent = get_agent(user_id=user_id)
        directive = f"[CRON JOB TRIGGERED] Act autonomously to fulfill the following scheduled goal. Be extremely brief in your final summary.\n\nGOAL: {goal}"
        result = await agent.run(directive, None)
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
    
    # Check Ollama Status for Terminal
    from brain.ollama_manager import OllamaManager
    om = OllamaManager()
    status_summary = om.get_status_summary_sync()
    print(f"\n[Sili Neural Heartbeat] {status_summary}")
    
    text_m = os.getenv("TEXT_MODEL", "llama3.1")
    vision_m = os.getenv("VISION_MODEL", "llama3.2-vision")
    print(f"[Neural Nodes] Text: {text_m} | Vision: {vision_m}\n")
    
    print(f"Starting Sili V16 Daemon. Target User: {AUTHORIZED_USER_ID}")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    async def post_init(app: Application):
        if not scheduler.running:
            scheduler.start()
            scheduler.add_job(sync_jobs_from_disk, 'interval', seconds=15)
        await sync_commands(app)

    application.post_init = post_init

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("tools", list_tools))
    application.add_handler(CommandHandler("ollama", ollama_status_command))
    application.add_handler(CommandHandler("select_model", select_model_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(button_callback))

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
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
