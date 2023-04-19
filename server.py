import logging
import aiohttp

from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config.config import BOT_TOKEN, SITE_URL, LOG_FILE, LOG_LEVEL


FIELDS = {"Boots": ["id", "name", "season", "origin", "appearance_year",
                    "popularity_start", "popularity_end",
                    "heel", "clasp", "features", "picture", "deleted"],
          "Brims": ["id", "name", "picture", "deleted"],
          "Clasps": ["id", "name", "picture", "deleted"],
          "Collars": ["id", "name", "picture", "deleted"],
          "Countries": ["id", "name", "deleted"],
          "Fabrics": ["id", "name", "warmth", "washing", "picture", "deleted"],
          "Fits": ["id", "name", "deleted"],
          "Hats": ["id", "name", "season", "origin", "appearance_year",
                   "popularity_start", "popularity_end", "brim", "features", "picture", "deleted"],
          "Heels": ["id", "name", "picture", "deleted"],
          "Lapels": ["id", "name", "picture", "deleted"],
          "Lower_body": ["id", "name", "season", "origin", "appearance_year",
                         "popularity_start", "popularity_end", "fit",
                         "clasp", "length", "features", "picture", "deleted"],
          "Patterns": ["id", "name", "picture", "deleted"],
          "Seasons": ["id", "name", "deleted"],
          "Sizes": ["id", "name", "deleted"],
          "Sleeves": ["id", "name", "picture", "deleted"],
          "Trouser_lengths": ["id", "name", "picture", "deleted"],
          "Types": ["id", "name", "deleted"],
          "Upper_body": ["id", "name", "season", "origin", "appearance_year",
                         "popularity_start", "popularity_end", "sleeves", "clasp", "collar",
                         "hood", "lapels", "pockets", "fitted", "features", "picture", "deleted"],
          "Wardrobe": ["id", "type", "name", "color", "size",
                       "fabric", "pattern", "picture", "deleted", "owner"],
          "users": ["id", "email", "hashed_password", "name", "access", "deleted"]}

RELATIONS = {"brim": "Brims", "clasp": "Clasps", "collar": "Collars",
             "origin": "Countries", "fabric": "Fabrics", "fit": "Fits",
             "heel": "Heels", "lapels": "Lapels", "pattern": "Patterns",
             "season": "Seasons", "size": "Sizes", "sleeves": "Sleeves",
             "length": "Trouser_lengths", "type": "Types", "owner": "User"}


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=LOG_LEVEL, filename=LOG_FILE
)

logger = logging.getLogger(__name__)


# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.
async def echo(update, context):
    # У объекта класса Updater есть поле message,
    # являющееся объектом сообщения.
    # У message есть поле text, содержащее текст полученного сообщения,
    # а также метод reply_text(str),
    # отсылающий ответ пользователю, от которого получено сообщение.
    if update.message.text.lower() == "Give battle advice".lower():
        await update.message.reply_text("Go for the eyes!")
    else:
        await update.message.reply_text("I'm sorry, currently I don't support texting, so please use only commands.")


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    reply_keyboard = [['/get Hats', '/get Boots'],
                      ['/get Lower_body', '/get Upper_body']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    user = update.effective_user
    await update.message.reply_html(
        rf"Hello {user.mention_html()}! I'm Wilson. I can help you accessing Design Helper", reply_markup=markup
    )


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("""Possibe commands:
    /start
    /get <table>    -  to get data from table""")


async def get_response(url, params=None):
    if params is None:
        params = {}
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


async def get_data(update, context):
    print(SITE_URL + "/api/" + context.args[0].lower())
    response = await get_response(SITE_URL + "/api/" + context.args[0].lower())
    answer = ""
    print(response)
    for i in response:
        for j in response[i]:
            for k in FIELDS[context.args[0]][1:-1]:
                if k in RELATIONS:
                    print(SITE_URL + "/api/" + RELATIONS[k].lower() + "/" + str(j[k]))
                    resp = await get_response(SITE_URL + "/api/" + RELATIONS[k].lower() + "/" + str(j[k]))
                    print(resp)
                    if "message" not in resp:
                        name = ""
                        for el in resp:
                            if isinstance(resp[el], dict):
                                name = resp[el]["name"]
                            else:
                                name = str(resp[el])
                            break
                    else:
                        name = ""
                    answer += str(k) + ": " + name + "\n"
                else:
                    answer += str(k) + ": " + str(j[k]) + "\n"
            answer += "\n"
        answer += "\n\n"
    answer = answer.strip()
    if not answer:
        answer = "There are none, sorry"
    await update.message.reply_text(answer)


def main():
    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token(BOT_TOKEN).build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    # Регистрируем обработчик в приложении.
    application.add_handler(text_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("get", get_data))

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
