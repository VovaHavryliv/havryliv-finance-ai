import os
import sqlite3
from datetime import datetime

from telegram import (
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# TOKEN
# =========================

TOKEN = os.getenv("TOKEN")

# =========================
# DATABASE
# =========================

conn = sqlite3.connect("finance.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS finance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    amount REAL,
    category TEXT,
    created_at TEXT
)
""")

conn.commit()

# =========================
# KEYBOARD
# =========================

keyboard = [
    ["💸 Витрата", "💰 Дохід"],
    ["💳 Баланс", "📊 Статистика"],
    ["🧾 Історія", "🧠 AI Аналіз"],
    ["🌍 Мова", "⚙️ Налаштування"]
]

reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True
)

# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🔥 HAVRYLIV FINANCE AI

👋 Вітаю!

Ваш AI Finance Assistant готовий 🚀
"""

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )

# =========================
# BALANCE
# =========================

def get_balance(user_id):
    cursor.execute("""
    SELECT type, amount FROM finance
    WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()

    balance = 0

    for row in rows:
        if row[0] == "income":
            balance += row[1]
        else:
            balance -= row[1]

    return balance

# =========================
# ADD EXPENSE
# =========================

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["state"] = "expense"

    await update.message.reply_text(
        "💸 Введіть суму витрати:"
    )

# =========================
# ADD INCOME
# =========================

async def add_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["state"] = "income"

    await update.message.reply_text(
        "💰 Введіть суму доходу:"
    )

# =========================
# TEXT HANDLER
# =========================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user_id = update.message.from_user.id

    # =====================
    # BUTTONS
    # =====================

    if text == "💸 Витрата":
        await add_expense(update, context)
        return

    if text == "💰 Дохід":
        await add_income(update, context)
        return

    if text == "💳 Баланс":

        balance = get_balance(user_id)

        await update.message.reply_text(
            f"💳 Ваш баланс: {balance:.2f} PLN"
        )

        return

    if text == "📊 Статистика":

        cursor.execute("""
        SELECT COUNT(*)
        FROM finance
        WHERE user_id = ?
        """, (user_id,))

        count = cursor.fetchone()[0]

        balance = get_balance(user_id)

        await update.message.reply_text(
            f"""
📊 Статистика:

🧾 Операцій: {count}
💳 Баланс: {balance:.2f} PLN
"""
        )

        return

    if text == "🧾 Історія":

        cursor.execute("""
        SELECT type, amount, created_at
        FROM finance
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 10
        """, (user_id,))

        rows = cursor.fetchall()

        if not rows:
            await update.message.reply_text(
                "❌ Історія порожня"
            )
            return

        message = "🧾 Останні операції:\n\n"

        for row in rows:

            emoji = "💰" if row[0] == "income" else "💸"

            message += f"{emoji} {row[1]} PLN\n📅 {row[2]}\n\n"

        await update.message.reply_text(message)

        return

    if text == "🧠 AI Аналіз":

        balance = get_balance(user_id)

        if balance > 1000:
            advice = "🔥 Ви добре контролюєте фінанси!"
        elif balance > 0:
            advice = "😄 Баланс позитивний. Так тримати!"
        else:
            advice = "⚠️ Ви витрачаєте більше ніж заробляєте."

        await update.message.reply_text(
            f"""
🧠 AI Аналіз

💳 Баланс: {balance:.2f} PLN

💡 Порада:
{advice}
"""
        )

        return

    if text == "🌍 Мова":

        await update.message.reply_text(
            """
🌍 Languages:

🇺🇦 Українська
🇺🇸 English
🇵🇱 Polski
"""
        )

        return

    if text == "⚙️ Налаштування":

        await update.message.reply_text(
            """
⚙️ Налаштування

🔔 Push notifications
🌙 Dark mode
💱 Валюта
☁️ Cloud sync
"""
        )

        return

    # =====================
    # SAVE DATA
    # =====================

    state = context.user_data.get("state")

    if state in ["expense", "income"]:

        try:
            amount = float(text)

            finance_type = "income" if state == "income" else "expense"

            cursor.execute("""
            INSERT INTO finance (
                user_id,
                type,
                amount,
                category,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                finance_type,
                amount,
                "general",
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))

            conn.commit()

            context.user_data["state"] = None

            emoji = "💰" if finance_type == "income" else "💸"

            await update.message.reply_text(
                f"{emoji} Записано: {amount:.2f} PLN"
            )

        except:
            await update.message.reply_text(
                "❌ Введіть число"
            )

# =========================
# MAIN
# =========================

print("🔥 HAVRYLIV FINANCE AI STARTED")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)
)

app.run_polling()