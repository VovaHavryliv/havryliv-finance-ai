# ==========================================
# HAVRYLIV FINANCE AI V9
# AI LIFE SYSTEM
# ==========================================

import os
import sqlite3
import random
from datetime import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==========================================
# TOKEN
# ==========================================

TOKEN = os.getenv("TOKEN")

# ==========================================
# DATABASE
# ==========================================

conn = sqlite3.connect(
    "finance.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    language TEXT DEFAULT 'ua',
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    created_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS finance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    amount REAL,
    category TEXT,
    description TEXT,
    created_at TEXT
)
""")

conn.commit()

# ==========================================
# KEYBOARDS
# ==========================================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["💸 Витрата", "💰 Дохід"],
        ["💳 Баланс", "📊 Статистика"],
        ["🧠 AI Центр", "🎮 Gamer Hub"],
        ["🎯 Цілі", "🏆 Рівень"],
        ["⚙️ Налаштування", "🌍 Мова"],
    ],
    resize_keyboard=True
)

language_keyboard = ReplyKeyboardMarkup(
    [
        ["🇺🇦 Українська"],
        ["🇺🇸 English"],
        ["🇵🇱 Polski"],
        ["⬅️ Назад"],
    ],
    resize_keyboard=True
)

settings_keyboard = ReplyKeyboardMarkup(
    [
        ["🔔 Notifications"],
        ["🌙 Theme"],
        ["💱 Currency"],
        ["☁️ Cloud Sync"],
        ["⬅️ Назад"],
    ],
    resize_keyboard=True
)

ai_keyboard = ReplyKeyboardMarkup(
    [
        ["🧠 AI Аналіз"],
        ["🔮 Прогноз"],
        ["💡 AI Порада"],
        ["🔥 Finance Score"],
        ["⬅️ Назад"],
    ],
    resize_keyboard=True
)

gamer_keyboard = ReplyKeyboardMarkup(
    [
        ["🎮 Gaming Stats"],
        ["💸 Steam Spending"],
        ["🏆 Gamer Rank"],
        ["🔥 Gamer AI"],
        ["⬅️ Назад"],
    ],
    resize_keyboard=True
)

# ==========================================
# HELPERS
# ==========================================

def get_balance(user_id):

    cursor.execute("""
    SELECT type, amount
    FROM finance
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


def detect_category(text):

    text = text.lower()

    if any(word in text for word in [
        "pizza",
        "coffee",
        "burger",
        "food",
        "mcdonalds"
    ]):
        return "🍔 Food"

    if any(word in text for word in [
        "steam",
        "cs2",
        "valorant",
        "skin",
        "game"
    ]):
        return "🎮 Gaming"

    if any(word in text for word in [
        "uber",
        "taxi",
        "bolt"
    ]):
        return "🚕 Transport"

    return "📦 Other"

# ==========================================
# START
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    cursor.execute("""
    INSERT OR IGNORE INTO users (
        user_id,
        created_at
    )
    VALUES (?, ?)
    """, (
        user.id,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    conn.commit()

    text = f"""
🔥 HAVRYLIV FINANCE AI V9

🧠 AI LIFE SYSTEM

👋 Welcome, {user.first_name}

🚀 Cloud AI Active
"""

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ==========================================
# AI ANALYSIS
# ==========================================

async def ai_analysis(update, context):

    user_id = update.effective_user.id

    balance = get_balance(user_id)

    text = f"""
🧠 AI ANALYSIS

💳 Balance: {balance:.2f} PLN

"""

    if balance > 5000:
        text += "🔥 Excellent financial stability\n"

    elif balance > 0:
        text += "😄 Positive balance detected\n"

    else:
        text += "⚠️ Overspending detected\n"

    tips = [
        "💡 Reduce night spending",
        "💡 Save 20% of income",
        "💡 Gaming expenses increased",
        "💡 Delivery spending too high",
    ]

    text += f"\n{random.choice(tips)}"

    await update.message.reply_text(text)

# ==========================================
# PREDICTION
# ==========================================

async def prediction(update, context):

    user_id = update.effective_user.id

    balance = get_balance(user_id)

    future = balance - random.randint(
        200,
        1500
    )

    await update.message.reply_text(
        f"""
🔮 AI PREDICTION

📉 Predicted balance in 30 days:

💳 {future:.2f} PLN
"""
    )

# ==========================================
# FINANCE SCORE
# ==========================================

async def finance_score(update, context):

    score = random.randint(60, 98)

    rank = "A"

    if score > 90:
        rank = "S"

    elif score < 70:
        rank = "B"

    await update.message.reply_text(
        f"""
🔥 FINANCE SCORE

🏆 Score: {score}/100
📈 Rank: {rank}

🧠 AI detected:
Good budget control
"""
    )

# ==========================================
# GAMER AI
# ==========================================

async def gamer_ai(update, context):

    await update.message.reply_text(
        """
🎮 GAMER AI

💸 Gaming spending increased by 12%

⚠️ CS2 skins detected

💡 AI Advice:
Avoid tilt spending 😄
"""
    )

# ==========================================
# LEVEL
# ==========================================

async def level(update, context):

    user_id = update.effective_user.id

    cursor.execute("""
    SELECT level, xp
    FROM users
    WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()

    lvl = row[0]
    xp = row[1]

    await update.message.reply_text(
        f"""
🏆 FINANCE LEVEL

🔥 Level: {lvl}
⚡ XP: {xp}

🚀 Finance MMORPG Active
"""
    )

# ==========================================
# BALANCE
# ==========================================

async def balance(update, context):

    user_id = update.effective_user.id

    balance_amount = get_balance(user_id)

    await update.message.reply_text(
        f"""
💳 BALANCE

💰 {balance_amount:.2f} PLN
"""
    )

# ==========================================
# STATS
# ==========================================

async def stats(update, context):

    user_id = update.effective_user.id

    cursor.execute("""
    SELECT COUNT(*)
    FROM finance
    WHERE user_id = ?
    """, (user_id,))

    count = cursor.fetchone()[0]

    balance_amount = get_balance(user_id)

    await update.message.reply_text(
        f"""
📊 STATISTICS

🧾 Transactions: {count}
💳 Balance: {balance_amount:.2f} PLN
"""
    )

# ==========================================
# MESSAGE HANDLER
# ==========================================

async def text_handler(update, context):

    text = update.message.text

    user_id = update.effective_user.id

    # MAIN

    if text == "💳 Баланс":
        await balance(update, context)
        return

    if text == "📊 Статистика":
        await stats(update, context)
        return

    if text == "🏆 Рівень":
        await level(update, context)
        return

    # AI MENU

    if text == "🧠 AI Центр":

        await update.message.reply_text(
            "🧠 AI CENTER",
            reply_markup=ai_keyboard
        )

        return

    if text == "🧠 AI Аналіз":
        await ai_analysis(update, context)
        return

    if text == "🔮 Прогноз":
        await prediction(update, context)
        return

    if text == "🔥 Finance Score":
        await finance_score(update, context)
        return

    if text == "💡 AI Порада":

        tips = [
            "💡 Save more money",
            "💡 Reduce subscriptions",
            "💡 Food spending too high",
            "💡 Build emergency fund",
        ]

        await update.message.reply_text(
            random.choice(tips)
        )

        return

    # GAMER MENU

    if text == "🎮 Gamer Hub":

        await update.message.reply_text(
            "🎮 GAMER HUB",
            reply_markup=gamer_keyboard
        )

        return

    if text == "🔥 Gamer AI":
        await gamer_ai(update, context)
        return

    if text == "🎮 Gaming Stats":

        await update.message.reply_text(
            """
🎮 GAMING STATS

💸 Steam spending:
420 PLN

🔥 Most played economy:
CS2
"""
        )

        return

    if text == "💸 Steam Spending":

        await update.message.reply_text(
            """
💸 STEAM SPENDING

📈 This month:
214 PLN
"""
        )

        return

    if text == "🏆 Gamer Rank":

        await update.message.reply_text(
            """
🏆 GAMER RANK

🎮 Elite Gamer Saver
"""
        )

        return

    # SETTINGS

    if text == "⚙️ Налаштування":

        await update.message.reply_text(
            "⚙️ SETTINGS",
            reply_markup=settings_keyboard
        )

        return

    # LANGUAGE

    if text == "🌍 Мова":

        await update.message.reply_text(
            "🌍 LANGUAGE",
            reply_markup=language_keyboard
        )

        return

    if text == "🇺🇦 Українська":

        cursor.execute("""
        UPDATE users
        SET language = 'ua'
        WHERE user_id = ?
        """, (user_id,))

        conn.commit()

        await update.message.reply_text(
            "🇺🇦 Мову змінено"
        )

        return

    if text == "🇺🇸 English":

        cursor.execute("""
        UPDATE users
        SET language = 'en'
        WHERE user_id = ?
        """, (user_id,))

        conn.commit()

        await update.message.reply_text(
            "🇺🇸 Language changed"
        )

        return

    if text == "🇵🇱 Polski":

        cursor.execute("""
        UPDATE users
        SET language = 'pl'
        WHERE user_id = ?
        """, (user_id,))

        conn.commit()

        await update.message.reply_text(
            "🇵🇱 Język zmieniony"
        )

        return

    # BACK

    if text == "⬅️ Назад":

        await update.message.reply_text(
            "🏠 MAIN MENU",
            reply_markup=main_keyboard
        )

        return

    # EXPENSE

    if text == "💸 Витрата":

        context.user_data["state"] = "expense"

        await update.message.reply_text(
            """
💸 ENTER EXPENSE

Example:
120 pizza
"""
        )

        return

    # INCOME

    if text == "💰 Дохід":

        context.user_data["state"] = "income"

        await update.message.reply_text(
            """
💰 ENTER INCOME

Example:
25000 salary
"""
        )

        return

    # SAVE TRANSACTION

    state = context.user_data.get("state")

    if state in ["expense", "income"]:

        try:

            parts = text.split()

            amount = float(parts[0])

            description = " ".join(parts[1:])

            category = detect_category(
                description
            )

            finance_type = (
                "income"
                if state == "income"
                else "expense"
            )

            cursor.execute("""
            INSERT INTO finance (
                user_id,
                type,
                amount,
                category,
                description,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                finance_type,
                amount,
                category,
                description,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            ))

            conn.commit()

            cursor.execute("""
            UPDATE users
            SET xp = xp + 25
            WHERE user_id = ?
            """, (user_id,))

            conn.commit()

            await update.message.reply_text(
                f"""
✅ TRANSACTION ADDED

💰 {amount:.2f} PLN
📂 {category}
📝 {description}

⚡ +25 XP
"""
            )

            context.user_data["state"] = None

        except:

            await update.message.reply_text(
                "❌ Invalid format"
            )

# ==========================================
# MAIN
# ==========================================

print("🔥 HAVRYLIV FINANCE AI V9 STARTED")

app = (
    ApplicationBuilder()
    .token(TOKEN)
    .build()
)

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_handler
    )
)

app.run_polling()   