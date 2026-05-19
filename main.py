# ==========================================
# HAVRYLIV FINANCE AI V8
# AI LIFE OPERATING SYSTEM
# Powered by Havryliv Technologies
# ==========================================

from telegram import (
    Update,
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,
)

import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import random
import csv

# ==========================================
# CONFIG
# ==========================================

TOKEN = "8736027860:AAF_L9aVnN72VCeMFn6W30ocQKAlI5b-QQ8"

APP_NAME = "HAVRYLIV FINANCE AI"

VERSION = "V8 AI LIFE SYSTEM"

# ==========================================
# DATABASE
# ==========================================

conn = sqlite3.connect(
    "finance.db",
    check_same_thread=False
)

cursor = conn.cursor()

# USERS

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    streak INTEGER DEFAULT 0,
    life_score INTEGER DEFAULT 50,
    created_at TEXT
)
""")

# TRANSACTIONS

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    amount REAL,
    category TEXT,
    description TEXT,
    created_at TEXT
)
""")

# GOALS

cursor.execute("""
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    goal_name TEXT,
    target_amount REAL,
    current_amount REAL
)
""")

conn.commit()

# ==========================================
# KEYBOARD
# ==========================================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["💸 Expense", "💰 Income"],
        ["💳 Balance", "📊 Statistics"],
        ["📜 History", "📈 Graph"],
        ["🧠 AI Analysis", "🏆 Level"],
        ["🔥 Streak", "🎮 Missions"],
        ["🏅 Achievements", "🧬 Life Score"],
        ["🎯 Goals", "🎮 Gamer Stats"],
        ["📤 Export CSV", "⚙️ Settings"],
        ["🌙 Daily Report", "🤖 AI Chat"],
    ],
    resize_keyboard=True,
)

# ==========================================
# HELPERS
# ==========================================

def detect_category(text):

    text = text.lower()

    food = [
        "coffee",
        "pizza",
        "burger",
        "mcdonalds",
        "kfc",
        "food",
    ]

    gaming = [
        "steam",
        "cs2",
        "valorant",
        "skin",
        "case",
        "game",
    ]

    transport = [
        "uber",
        "bolt",
        "taxi",
        "bus",
    ]

    setup = [
        "monitor",
        "gpu",
        "keyboard",
        "mouse",
        "pc",
    ]

    if any(word in text for word in food):
        return "🍔 Food"

    if any(word in text for word in gaming):
        return "🎮 Gaming"

    if any(word in text for word in transport):
        return "🚕 Transport"

    if any(word in text for word in setup):
        return "🖥️ Setup"

    return "📦 Other"


def get_balance(user_id):

    cursor.execute(
        """
        SELECT type, amount
        FROM transactions
        WHERE user_id = ?
        """,
        (user_id,),
    )

    rows = cursor.fetchall()

    balance = 0

    for t_type, amount in rows:

        if t_type == "income":
            balance += amount

        else:
            balance -= amount

    return balance


def get_expenses(user_id):

    cursor.execute(
        """
        SELECT SUM(amount)
        FROM transactions
        WHERE user_id = ?
        AND type = 'expense'
        """,
        (user_id,),
    )

    result = cursor.fetchone()[0]

    return result or 0


def get_income(user_id):

    cursor.execute(
        """
        SELECT SUM(amount)
        FROM transactions
        WHERE user_id = ?
        AND type = 'income'
        """,
        (user_id,),
    )

    result = cursor.fetchone()[0]

    return result or 0


def add_xp(user_id, xp_amount):

    cursor.execute(
        """
        UPDATE users
        SET xp = xp + ?
        WHERE user_id = ?
        """,
        (xp_amount, user_id),
    )

    conn.commit()


def calculate_life_score(user_id):

    balance = get_balance(user_id)

    expenses = get_expenses(user_id)

    score = 50

    if balance > 10000:
        score += 20

    if expenses < 3000:
        score += 15

    if expenses > 10000:
        score -= 20

    return max(1, min(score, 100))

# ==========================================
# START
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (
            user_id,
            username,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            user.id,
            user.username,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        ),
    )

    conn.commit()

    text = (
        f"🔥 {APP_NAME}\n"
        f"⚡ {VERSION}\n\n"
        f"👋 Welcome, {user.first_name}\n\n"
        f"🧠 AI LIFE SYSTEM READY\n"
        f"🎮 Finance MMORPG Activated\n"
        f"🔥 Powered by Havryliv"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard,
    )

# ==========================================
# BALANCE
# ==========================================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    balance_amount = get_balance(user_id)

    income = get_income(user_id)

    expenses = get_expenses(user_id)

    text = (
        f"💳 Balance: {balance_amount:.2f} PLN\n\n"
        f"💰 Income: {income:.2f} PLN\n"
        f"💸 Expenses: {expenses:.2f} PLN"
    )

    await update.message.reply_text(text)

# ==========================================
# LIFE SCORE
# ==========================================

async def life_score(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    score = calculate_life_score(user_id)

    rank = "B"

    if score >= 90:
        rank = "S"

    elif score >= 75:
        rank = "A"

    elif score >= 60:
        rank = "B"

    else:
        rank = "C"

    text = (
        "🧬 LIFE SCORE SYSTEM\n\n"
        f"🏆 Score: {score}/100\n"
        f"📈 Rank: {rank}\n\n"
        "🧠 AI detected:\n"
        "Good financial stability.\n\n"
        "🔥 by Havryliv"
    )

    await update.message.reply_text(text)

# ==========================================
# LEVEL SYSTEM
# ==========================================

async def level(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    cursor.execute(
        """
        SELECT xp, level
        FROM users
        WHERE user_id = ?
        """,
        (user_id,),
    )

    xp, lvl = cursor.fetchone()

    text = (
        "🏆 LEVEL SYSTEM\n\n"
        f"⚡ Level: {lvl}\n"
        f"🔥 XP: {xp}\n\n"
        "🎮 Finance MMORPG Active"
    )

    await update.message.reply_text(text)

# ==========================================
# MISSIONS
# ==========================================

async def missions(update: Update, context: ContextTypes.DEFAULT_TYPE):

    missions_list = [
        "Do not buy skins today 😄",
        "Stay under 100 PLN",
        "Save 50 PLN",
        "No fast food today",
        "No impulsive purchases",
    ]

    mission = random.choice(missions_list)

    text = (
        "🎮 DAILY MISSION\n\n"
        f"🎯 {mission}\n\n"
        "🏆 Reward: +50 XP"
    )

    await update.message.reply_text(text)

# ==========================================
# ACHIEVEMENTS
# ==========================================

async def achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "🏅 ACHIEVEMENTS\n\n"
        "✅ First transaction\n"
        "🔥 7 day streak\n"
        "💰 First 10 000 PLN\n"
        "🎮 Gamer detected\n"
        "🧠 AI user\n"
        "📈 Smart spender\n\n"
        "🔥 Powered by Havryliv"
    )

    await update.message.reply_text(text)

# ==========================================
# AI ANALYSIS
# ==========================================

async def ai_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    balance = get_balance(user_id)

    expenses = get_expenses(user_id)

    text = (
        "🧠 HAVRYLIV AI ANALYSIS\n\n"
        f"💳 Balance: {balance:.2f} PLN\n"
        f"💸 Expenses: {expenses:.2f} PLN\n\n"
    )

    if expenses > 5000:

        text += (
            "⚠️ High spending detected\n"
        )

    if balance > 10000:

        text += (
            "🔥 Excellent balance stability\n"
        )

    text += (
        "\n💡 AI Advice:\n"
        "Reduce dopamine spending.\n\n"
        "🎮 Gamer spending patterns detected 😄"
    )

    await update.message.reply_text(text)

# ==========================================
# GAMER STATS
# ==========================================

async def gamer_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    cursor.execute(
        """
        SELECT SUM(amount)
        FROM transactions
        WHERE user_id = ?
        AND category = '🎮 Gaming'
        """,
        (user_id,),
    )

    result = cursor.fetchone()[0]

    gaming = result or 0

    text = (
        "🎮 GAMER ECONOMY SYSTEM\n\n"
        f"💸 Gaming Spending: {gaming:.2f} PLN\n\n"
        "🎯 Most expensive category:\n"
        "CS2 skins 😄"
    )

    await update.message.reply_text(text)

# ==========================================
# DAILY REPORT
# ==========================================

async def daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    balance = get_balance(user_id)

    expenses = get_expenses(user_id)

    text = (
        "🌙 DAILY AI REPORT\n\n"
        f"💳 Balance: {balance:.2f} PLN\n"
        f"💸 Expenses: {expenses:.2f} PLN\n\n"
        "🧠 AI Advice:\n"
        "Avoid emotional purchases.\n\n"
        "🔥 by Havryliv"
    )

    await update.message.reply_text(text)

# ==========================================
# HISTORY
# ==========================================

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    cursor.execute(
        """
        SELECT type, amount,
        category, description
        FROM transactions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 10
        """,
        (user_id,),
    )

    rows = cursor.fetchall()

    if not rows:

        await update.message.reply_text(
            "📭 No history"
        )

        return

    text = "📜 HISTORY\n\n"

    for row in rows:

        t_type, amount, category, desc = row

        emoji = (
            "➕"
            if t_type == "income"
            else "➖"
        )

        text += (
            f"{emoji} {amount:.2f} PLN\n"
            f"{category}\n"
            f"{desc}\n\n"
        )

    await update.message.reply_text(text)

# ==========================================
# STATS
# ==========================================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    cursor.execute(
        """
        SELECT category, SUM(amount)
        FROM transactions
        WHERE user_id = ?
        AND type = 'expense'
        GROUP BY category
        """,
        (user_id,),
    )

    rows = cursor.fetchall()

    if not rows:

        await update.message.reply_text(
            "📭 No stats"
        )

        return

    total = sum(amount for _, amount in rows)

    text = "📊 STATISTICS\n\n"

    for category, amount in rows:

        percent = (
            amount / total
        ) * 100

        text += (
            f"{category}\n"
            f"💰 {amount:.2f} PLN\n"
            f"📈 {percent:.1f}%\n\n"
        )

    await update.message.reply_text(text)

# ==========================================
# GRAPH
# ==========================================

async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    cursor.execute(
        """
        SELECT category, amount
        FROM transactions
        WHERE user_id = ?
        AND type = 'expense'
        """,
        (user_id,),
    )

    rows = cursor.fetchall()

    if not rows:

        await update.message.reply_text(
            "📭 No graph data"
        )

        return

    categories = [r[0] for r in rows]

    amounts = [r[1] for r in rows]

    plt.figure(figsize=(8, 8))

    plt.pie(
        amounts,
        labels=categories,
        autopct="%1.1f%%",
    )

    plt.title(
        "HAVRYLIV FINANCE AI"
    )

    path = "graph.png"

    plt.savefig(path)

    plt.close()

    with open(path, "rb") as photo:

        await update.message.reply_photo(photo)

# ==========================================
# EXPORT CSV
# ==========================================

async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    cursor.execute(
        """
        SELECT *
        FROM transactions
        WHERE user_id = ?
        """,
        (user_id,),
    )

    rows = cursor.fetchall()

    filename = (
        f"finance_{user_id}.csv"
    )

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerows(rows)

    with open(filename, "rb") as file:

        await update.message.reply_document(file)

# ==========================================
# MESSAGE HANDLER
# ==========================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    user_id = update.effective_user.id

    # BUTTONS

    if text == "💳 Balance":
        await balance(update, context)
        return

    if text == "🧬 Life Score":
        await life_score(update, context)
        return

    if text == "🏆 Level":
        await level(update, context)
        return

    if text == "🎮 Missions":
        await missions(update, context)
        return

    if text == "🏅 Achievements":
        await achievements(update, context)
        return

    if text == "🧠 AI Analysis":
        await ai_analysis(update, context)
        return

    if text == "🎮 Gamer Stats":
        await gamer_stats(update, context)
        return

    if text == "🌙 Daily Report":
        await daily_report(update, context)
        return

    if text == "📜 History":
        await history(update, context)
        return

    if text == "📊 Statistics":
        await stats(update, context)
        return

    if text == "📈 Graph":
        await graph(update, context)
        return

    if text == "📤 Export CSV":
        await export_csv(update, context)
        return

    if text == "💸 Expense":

        context.user_data["type"] = (
            "expense"
        )

        await update.message.reply_text(
            "💸 Enter expense:\n\n"
            "50 coffee"
        )

        return

    if text == "💰 Income":

        context.user_data["type"] = (
            "income"
        )

        await update.message.reply_text(
            "💰 Enter income:\n\n"
            "25000 salary"
        )

        return

    # TRANSACTION

    try:

        parts = text.split()

        amount = float(parts[0])

        description = " ".join(parts[1:])

        transaction_type = (
            context.user_data.get(
                "type",
                "expense"
            )
        )

        if transaction_type == "income":

            category = "💼 Income"

        else:

            category = detect_category(
                description
            )

        cursor.execute(
            """
            INSERT INTO transactions
            (
                user_id,
                type,
                amount,
                category,
                description,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                transaction_type,
                amount,
                category,
                description,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            ),
        )

        conn.commit()

        add_xp(
            user_id,
            25,
        )

        response = (
            "✅ TRANSACTION ADDED\n\n"
            f"💰 {amount:.2f} PLN\n"
            f"📂 {category}\n"
            f"📝 {description}\n\n"
            "⚡ +25 XP\n"
            "🔥 by Havryliv"
        )

        await update.message.reply_text(
            response
        )

    except:

        pass

# ==========================================
# APP
# ==========================================

app = (
    ApplicationBuilder()
    .token(TOKEN)
    .build()
)

app.add_handler(
    CommandHandler(
        "start",
        start,
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT,
        handle_message,
    )
)

# ==========================================
# START
# ==========================================

print(
    "🔥 HAVRYLIV FINANCE AI V8 STARTED"
)

app.run_polling()