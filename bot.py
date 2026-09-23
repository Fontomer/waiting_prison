"""
Telegram-бот — счётчик дней.

Что делает бот:
  • каждый день в заданное время (по умолчанию 00:00) присылает в чат
    сообщение со статистикой: сколько дней прошло и сколько осталось;
  • отвечает на несколько команд по запросу (см. /help).

Как запустить:
  1) pip install -r requirements.txt
  2) Заполните раздел "НАСТРОЙКИ" ниже своими данными
  3) python bot.py

Как получить BOT_TOKEN:
  Напишите в Telegram боту @BotFather команду /newbot и следуйте инструкциям.
  Он выдаст токен вида "123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx".

Как узнать CHAT_ID:
  1) Впишите сюда токен и любое временное значение в CHAT_ID (например 0)
  2) Запустите бота и напишите ему в нужном чате команду /chatid
  3) Он пришлёт число — впишите его в CHAT_ID ниже и перезапустите бота
"""

import random
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


# ============================================================
#  НАСТРОЙКИ — здесь можно менять всё под себя
# ============================================================

# Токен бота, полученный от @BotFather
BOT_TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"

# ID чата, куда бот будет присылать ежедневное сообщение.
# Как узнать — см. инструкцию в самом верху файла (команда /chatid).
CHAT_ID = 0

# Часовой пояс в формате IANA, например:
# "Europe/Moscow", "Europe/Kiev", "Asia/Almaty", "Europe/Warsaw", "Europe/Berlin"
# Полный список: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE = "Europe/Moscow"

# Время ежедневной отправки сообщения (час и минута по указанному TIMEZONE)
DAILY_HOUR = 0
DAILY_MINUTE = 0

# Дата, с которой начинается отсчёт (год, месяц, день)
START_DATE = date(2024, 1, 1)

# Планируемая дата освобождения (год, месяц, день).
# Если дата неизвестна — напишите None (без кавычек) вместо date(...),
# тогда бот будет считать только количество прошедших дней.
RELEASE_DATE = date(2027, 1, 1)  # либо: RELEASE_DATE = None

# Текст ежедневного сообщения (используется и в команде /status).
# Доступные плейсхолдеры (менять названия нельзя, но текст вокруг — можно):
#   {days_served} — сколько дней уже прошло
#   {days_left}   — сколько дней осталось (или "неизвестно", если RELEASE_DATE = None)
#   {percent}     — процент отбытого срока (или "—", если RELEASE_DATE = None)
#   {bar}         — прогресс-бар из символов █ и ░
DAILY_MESSAGE = (
    "📅 Доброе утро.\n\n"
    "Прошло дней: {days_served}\n"
    "Осталось дней: {days_left}\n"
    "Прогресс: {percent}% {bar}"
)

# Фразы для команды /motivate — свободно добавляйте, удаляйте, меняйте местами
MOTIVATE_QUOTES = [
    "Каждый прошедший день — на один день ближе к встрече. 💪",
    "Время идёт своим чередом, и это уже хорошая новость.",
    "Ты не один: мы считаем эти дни вместе.",
    "Ещё один день позади — уже что-то.",
]

# ============================================================
#  Дальше — логика бота. Менять не обязательно, но можно.
# ============================================================


def calculate_stats() -> dict:
    """Считает текущую статистику: сколько дней прошло, сколько осталось,
    процент срока и прогресс-бар. Возвращает словарь для подстановки в текст."""
    today = datetime.now(ZoneInfo(TIMEZONE)).date()
    days_served = max((today - START_DATE).days, 0)

    if RELEASE_DATE is not None:
        total_days = (RELEASE_DATE - START_DATE).days
        days_left_num = (RELEASE_DATE - today).days

        if total_days > 0:
            percent = round(min(days_served, total_days) / total_days * 100)
        else:
            percent = 100

        filled_blocks = int(percent / 10)
        bar = "█" * filled_blocks + "░" * (10 - filled_blocks)
        days_left = str(days_left_num) if days_left_num > 0 else "0 (срок истёк)"
    else:
        percent = "—"
        bar = ""
        days_left = "неизвестно"

    return {
        "days_served": days_served,
        "days_left": days_left,
        "percent": percent,
        "bar": bar,
    }


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start — приветствие."""
    await update.message.reply_text(
        f"Привет! Я бот-счётчик дней.\n"
        f"Каждый день в {DAILY_HOUR:02d}:{DAILY_MINUTE:02d} ({TIMEZONE}) "
        f"буду присылать сюда статистику.\n\n"
        f"Список команд — /help"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help — список всех команд."""
    await update.message.reply_text(
        "Доступные команды:\n"
        "/status — показать текущую статистику\n"
        "/release — дата освобождения и сколько до неё осталось\n"
        "/motivate — случайная подбадривающая фраза\n"
        "/chatid — показать ID этого чата (нужно один раз при настройке)\n"
        "/help — это сообщение"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status — статистика по запросу (тот же текст, что в ежедневной рассылке)."""
    stats = calculate_stats()
    await update.message.reply_text(DAILY_MESSAGE.format(**stats))


async def release_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /release — отдельно про дату освобождения."""
    if RELEASE_DATE is None:
        await update.message.reply_text("Дата освобождения не указана в настройках бота.")
        return
    stats = calculate_stats()
    await update.message.reply_text(
        f"Дата освобождения: {RELEASE_DATE.strftime('%d.%m.%Y')}\n"
        f"Осталось дней: {stats['days_left']}"
    )


async def chatid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /chatid — показывает ID текущего чата.
    Используйте один раз, чтобы узнать, какой CHAT_ID указать в настройках."""
    await update.message.reply_text(f"ID этого чата: {update.effective_chat.id}")


async def motivate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /motivate — случайная фраза из списка MOTIVATE_QUOTES."""
    await update.message.reply_text(random.choice(MOTIVATE_QUOTES))


async def send_daily_message(context: ContextTypes.DEFAULT_TYPE):
    """Вызывается автоматически каждый день в DAILY_HOUR:DAILY_MINUTE по TIMEZONE."""
    stats = calculate_stats()
    await context.bot.send_message(chat_id=CHAT_ID, text=DAILY_MESSAGE.format(**stats))


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем команды. Чтобы добавить свою — напишите новую async-функцию
    # по образцу выше и добавьте сюда ещё одну строку CommandHandler(...).
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("release", release_command))
    app.add_handler(CommandHandler("chatid", chatid_command))
    app.add_handler(CommandHandler("motivate", motivate_command))

    # Ежедневная отправка сообщения в заданное время
    app.job_queue.run_daily(
        send_daily_message,
        time=time(hour=DAILY_HOUR, minute=DAILY_MINUTE, tzinfo=ZoneInfo(TIMEZONE)),
    )

    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
