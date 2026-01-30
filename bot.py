import json
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ===== CONFIG =====
BOT_TOKEN = "8006015641:AAHMiqhkmtvRmdLMN1Rbz2EnwsIrsGfH8qU"
ADMIN_ID = 1858324638
VIDEO_DB = "video_map.json"

# ===== LOGGING =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ===== LOAD VIDEO MAP =====
if os.path.exists(VIDEO_DB):
    with open(VIDEO_DB, "r") as f:
        VIDEO_MAP = json.load(f)
else:
    VIDEO_MAP = {}

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Welcome to Cineflix! 🎬")
        return

    code = context.args[0]

    if code not in VIDEO_MAP:
        await update.message.reply_text("❌ Video not found. Contact admin.")
        return

    await update.message.reply_video(
        video=VIDEO_MAP[code],
        caption=f"🎬 Cineflix Streaming\nShortcode: {code}"
    )

async def save_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Not authorized.")
        return

    if not update.message.video or not context.args:
        await update.message.reply_text("Usage: send video + /save SHORTCODE")
        return

    code = context.args[0]
    VIDEO_MAP[code] = update.message.video.file_id

    with open(VIDEO_DB, "w") as f:
        json.dump(VIDEO_MAP, f)

    await update.message.reply_text(f"✅ Saved video for shortcode: {code}")

# ===== OPTIONAL =====
async def list_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not VIDEO_MAP:
        await update.message.reply_text("No videos saved yet.")
        return
    msg = "\n".join([f"{k} → {v}" for k,v in VIDEO_MAP.items()])
    await update.message.reply_text(f"Saved videos:\n{msg}")

async def delete_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /delete SHORTCODE")
        return
    code = context.args[0]
    if code in VIDEO_MAP:
        VIDEO_MAP.pop(code)
        with open(VIDEO_DB, "w") as f:
            json.dump(VIDEO_MAP, f)
        await update.message.reply_text(f"✅ Deleted video {code}")
    else:
        await update.message.reply_text("❌ Shortcode not found.")

# ===== MAIN =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("save", save_video))
    app.add_handler(CommandHandler("list", list_videos))
    app.add_handler(CommandHandler("delete", delete_video))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
