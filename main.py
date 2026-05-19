import os
import sqlite3
import random
from datetime import datetime

import matplotlib.pyplot as plt

from telegram import (
    Update,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# =========================
# HAVRYLIV FINANCE AI V8
# =========================

TOKEN = os.getenv("8736027860:AAF_L9aVnN72VCeMFn6W30ocQKAlI5b-QQ8")

DB_NAME = "finance.db"

# =========================
# DATABASE
# =========================

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    language TEXT DEFAULT 'ua',
    created_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
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

keyboard = ReplyKeyboardMarkup(
    [
        ["💸 Витрата", "💰 Дохід"],
        ["💳 Баланс", "📊 Статистика"],
        ["📜 Історія", "📈 Графік"],
        ["🧠 AI Аналіз", "🎯 Бюджет"],
        ["🌍 Мова", "⚙️ Налаштування"],
        ["ℹ️ Допомога"]
    ],
    resize_keyboard=True
)

# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    cursor.execute("""
    INSERT OR IGNORE INTO users (
        user_id,
        username,
        created_at
    )
    VALUES (?, ?, ?)
    """, (
        user.id,
        user.username,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()

    text = f"""
🔥 HAVRYLIV FINANCE AI
⚡ V8 Enterprise

👋 Вітаю, {user.first_name}!

Ваш AI Finance Assistant готовий.
"""

    await update.message.reply_text(
        text,
        reply_markup=keyboard
    )

# =========================
# BALANCE
# =========================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    cursor.execute("""
    SELECT SUM(amount)
    FROM transactions
    WHERE user_id = ?
    AND type = 'income'
    """, (user_id,))

    income = cursor.fetchone()[0] or 0

    cursor.execute("""
    SELECT SUM(amount)
    FROM transactions
    WHERE user_id = ?
    AND type = 'expense'
    """, (user_id,))

    expense = cursor.fetchone()[0] or 0

    balance_amount = income - expense

    text = f"""
💳 Баланс: {balance_amount:.2f} PLN

💰 Дохід: {income:.2f} PLN
💸 Витрати: {expense:.2f} PLN
"""

    await update.message.reply_text(text)

# =========================
# STATS
# =========================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM transactions
    WHERE user_id = ?
    AND type = 'expense'
    GROUP BY category
    """, (user_id,))

    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text(
            "📭 Немає статистики."
        )
        return

    text = "📊 Статистика:\n\n"

    for row in rows:
        text += f"• {row[0]} — {row[1]:.2f} PLN\n"

    await update.message.reply_text(text)

# =========================
# HISTORY
# =========================

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    cursor.execute("""
    SELECT type, amount, category, created_at
    FROM transactions
    WHERE user_id = ?
    ORDER BY id DESC
    LIMIT 10
    """, (user_id,))

    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text(
            "📭 Історія порожня."
        )
        return

    text = "📜 Останні операції:\n\n"

    for row in rows:

        emoji = "💸" if row[0] == "expense" else "💰"

        text += (
            f"{emoji} {row[1]:.2f} PLN\n"
            f"📂 {row[2]}\n"
            f"🕒 {row[3]}\n\n"
        )

    await update.message.reply_text(text)

# =========================
# GRAPH
# =========================

async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM transactions
    WHERE user_id = ?
    AND type = 'expense'
    GROUP BY category
    """, (user_id,))

    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text(
            "📭 Немає даних для графіка."
        )
        return

    labels = [row[0] for row in rows]
    amounts = [row[1] for row in rows]

    plt.figure(figsize=(6, 6))
    plt.pie(
        amounts,
        labels=labels,
        autopct='%1.1f%%'
    )

    plt.title("HAVRYLIV FINANCE AI")

    graph_file = "graph.png"

    plt.savefig(graph_file)
    plt.close()

    with open(graph_file, "rb") as photo:
        await update.message.reply_photo(photo)

# =========================
# AI ANALYSIS
# =========================

async def ai_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tips = [
        "💡 Спробуйте відкладати 20% доходу.",
        "💡 Витрати на їжу занадто високі.",
        "💡 Ви добре контролюєте бюджет.",
        "💡 Можна оптимізувати підписки.",
        "💡 Зменшіть імпульсивні покупки."
    ]

    await update.message.reply_text(
        f"🧠 AI Аналіз:\n\n{random.choice(tips)}"
    )

# =========================
# MESSAGE HANDLER
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user_id = update.effective_user.id

    # =====================
    # BUTTONS
    # =====================

    if text == "💳 Баланс":
        await balance(update, context)
        return

    if text == "📊 Статистика":
        await stats(update, context)
        return

    if text == "📜 Історія":
        await history(update, context)
        return

    if text == "📈 Графік":
        await graph(update, context)
        return

    if text == "🧠 AI Аналіз":
        await ai_analysis(update, context)
        return

    if text == "🌍 Мова":

        await update.message.reply_text(
            "🌍 Languages:\n\n"
            "🇺🇦 Українська\n"
            "🇺🇸 English\n"
            "🇵🇱 Polski"
        )

        return

    if text == "⚙️ Налаштування":

        await update.message.reply_text(
            "⚙️ Settings\n\n"
            "🔔 Notifications: ON\n"
            "💱 Currency: PLN\n"
            "🎮 Gamer Mode: ON"
        )

        return

    if text == "ℹ️ Допомога":

        await update.message.reply_text(
            "ℹ️ HELP\n\n"
            "💸 Витрата — додати витрату\n"
            "💰 Дохід — додати дохід\n"
            "📊 Статистика — аналітика\n"
            "📈 Графік — графік витрат\n"
            "🧠 AI Аналіз — AI поради\n\n"
            "🔥 HAVRYLIV FINANCE AI"
        )

        return

    # =====================
    # ADD EXPENSE
    # =====================

    if text == "💸 Витрата":

        context.user_data["mode"] = "expense"

        await update.message.reply_text(
            "💸 Введіть суму витрати:"
        )

        return

    # =====================
    # ADD INCOME
    # =====================

    if text == "💰 Дохід":

        context.user_data["mode"] = "income"

        await update.message.reply_text(
            "💰 Введіть суму доходу:"
        )

        return

    # =====================
    # HANDLE NUMBERS
    # =====================

    mode = context.user_data.get("mode")

    if mode in ["expense", "income"]:

        try:

            amount = float(text)

            transaction_type = mode

            category = (
                "Expense"
                if mode == "expense"
                else "Income"
            )

            cursor.execute("""
            INSERT INTO transactions (
                user_id,
                type,
                amount,
                category,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                transaction_type,
                amount,
                category,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()

            emoji = "💸" if mode == "expense" else "💰"

            await update.message.reply_text(
                f"{emoji} Додано: {amount:.2f} PLN"
            )

            context.user_data["mode"] = None

            return

        except:
            await update.message.reply_text(
                "❌ Введіть число."
            )
            return

# =========================
# NOTIFICATIONS
# =========================


# =========================
# MAIN
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

print("🔥 HAVRYLIV FINANCE AI V8 STARTED")

app.run_polling()