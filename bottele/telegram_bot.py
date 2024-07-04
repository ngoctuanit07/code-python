import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Thay thế 'YOUR_TELEGRAM_BOT_TOKEN' và 'YOUR_OPENAI_API_KEY' bằng token của bạn
#bot tele 7438287146:AAE8bwvAiStW4cZk-XA8AijxvMuSMCn-y-g
TELEGRAM_BOT_TOKEN = ''
OPENAI_API_KEY = ''

client = openai.OpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Chào bạn! Hãy gửi cho tôi một câu hỏi và tôi sẽ trả lời bạn.')

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Bạn là một trợ lý AI."},
            {"role": "user", "content": user_message},
        ]
    )
    reply = response.choices[0].message.content.strip()
    await update.message.reply_text(reply)

def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()