import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from footballdata_io import Client

# Configure logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Read environment variables from Railway (critical: do not hardcode)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
FOOTBALL_API_KEY = os.environ.get("FOOTBALL_API_KEY")

# Initialize football data client
football_client = Client(FOOTBALL_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ Welcome to Match Alert Bot!\n\n"
        "I can help you check today's fixtures.\n"
        "Send /today to see today's matches."
    )

async def today_fixtures(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Query today's fixtures and return them to the user"""
    try:
        # Call SDK to get today's fixtures
        fixtures = football_client.fixtures.today()
        
        if not fixtures:
            await update.message.reply_text("No fixtures scheduled for today.")
            return

        # Format the first 5 matches for display (to avoid overly long messages)
        msg_lines = ["📅 *Today's Fixtures (first 5):*\n"]
        for f in fixtures[:5]:
            home = f.get('home_team', {}).get('name', 'Unknown')
            away = f.get('away_team', {}).get('name', 'Unknown')
            time = f.get('time', 'TBD')
            msg_lines.append(f"• {home} vs {away} @ {time}")
        
        await update.message.reply_text("\n".join(msg_lines), parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"API error: {e}")
        await update.message.reply_text("⚠️ Failed to fetch data. Please try again later.")

def main():
    if not TELEGRAM_TOKEN:
        logger.error("Missing TELEGRAM_BOT_TOKEN! Set it in Railway Variables.")
        return
    if not FOOTBALL_API_KEY:
        logger.error("Missing FOOTBALL_API_KEY! Set it in Railway Variables.")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today_fixtures))
    
    logger.info("Match Alert Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
