import pandas as pd
from poi_trialmerged import FINAL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, CallbackQueryHandler
from dotenv import load_dotenv
import os
from flask import Flask
from threading import Thread

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Define conversation states
VACATION_TYPE, DURATION, BUDGET, TRAVEL_TYPE, PRIORITY = range(5)

# Function to get hotel price from the CSV file
def get_hotel_price(hotel_name):
    try:
        hotel_data = pd.read_csv('data/chennai_Hotels.csv')
        hotel_row = hotel_data[hotel_data['Hotel'] == hotel_name]
        if not hotel_row.empty:
            price = hotel_row['Price'].values[0]
            return price
        else:
            return None
    except Exception as e:
        print(f"Error loading hotel data: {e}")
        return None

# Greet the user when they first open the bot, using their name
async def greet(update: Update, context: CallbackContext) -> None:
    user_name = update.effective_user.first_name  # Get the user's first name
    await update.message.reply_text(
        f"👋 *Welcome, {user_name}, to the TripSage Travelling Planning Bot made for Chennai City!*\n\n"
        "Plan your perfect vacation by typing /start to begin your journey.",
        parse_mode="Markdown"
    )

# Start the conversation
async def start(update: Update, context: CallbackContext) -> int:
    user_name = update.effective_user.first_name  # Get the user's first name
    await update.message.reply_text(
        f"👋 *Hello, {user_name}!*\n\n"
        "Let's start planning your perfect vacation in Chennai 🏖️. Please select your preferred vacation type from the options below:",
        parse_mode="Markdown"
    )

    # Show vacation types as inline buttons
    keyboard = [
        [InlineKeyboardButton("🏞 Adventure and Outdoors", callback_data='1')],
        [InlineKeyboardButton("🛕 Spiritual", callback_data='2')],
        [InlineKeyboardButton("🏙 City Life", callback_data='3')],
        [InlineKeyboardButton("🎭 Cultural", callback_data='4')],
        [InlineKeyboardButton("🏖 Relaxing", callback_data='5')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Please select your preferred vacation type:", 
        reply_markup=reply_markup
    )
    
    return VACATION_TYPE

# Handle vacation type selection
async def vacation_type(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    vacation_types = {
        '1': 'Adventure and Outdoors',
        '2': 'Spiritual',
        '3': 'City Life',
        '4': 'Cultural',
        '5': 'Relaxing'
    }
    context.user_data['Type'] = [vacation_types[query.data]]
    
    # Asking for duration
    keyboard = [[InlineKeyboardButton(f"{i} days", callback_data=str(i))] for i in range(1, 8)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        text="⏳ How many days do you plan to spend on vacation?",
        reply_markup=reply_markup
    )
    return DURATION

# Handle duration input
async def duration(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data['Duration'] = int(query.data)

    # Asking for budget
    await query.message.reply_text(
        "💰 Please enter your *budget* (INR) for this vacation (e.g., 1000 - 150000):", 
        parse_mode="Markdown"
    )
    return BUDGET

# Handle budget input
async def budget(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    try:
        budget = int(user_input)
        if budget < 1000 or budget > 150000:
            raise ValueError
        context.user_data['Budget'] = budget
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid budget between 1000 and 150000.")
        return BUDGET

    # Asking for travel type
    keyboard = [
        [InlineKeyboardButton("Family", callback_data='1')],
        [InlineKeyboardButton("Friends", callback_data='2')],
        [InlineKeyboardButton("Individual", callback_data='3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🧑‍🤝‍🧑 Who are you traveling with?", 
        reply_markup=reply_markup
    )
    return TRAVEL_TYPE

# Handle travel type selection
async def travel_type(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    travel_groups = {
        '1': 'Family',
        '2': 'Friends',
        '3': 'Individual'
    }
    context.user_data['Travel_Type'] = travel_groups[query.data]

    # Asking for priority
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data='yes')],
        [InlineKeyboardButton("No", callback_data='no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        text="🎯 Is covering maximum places your priority?", 
        reply_markup=reply_markup
    )
    return PRIORITY

# Handle priority input and finalize the itinerary
async def priority(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data['Priority'] = query.data == 'yes'

    # Extract user data for FINAL function
    Type = context.user_data['Type']
    Duration = context.user_data['Duration']
    Budget = context.user_data['Budget']
    TYPE = context.user_data['Travel_Type']
    Ques = context.user_data['Priority']

    try:
        Output, Info = FINAL(Type, Duration, Budget, TYPE, Ques)

        response = f"*🗺 Travel Details:*\n"
        response += f"🏷 Vacation Type: {', '.join(Type)}\n"
        response += f"⏳ Duration: {Duration} days\n"
        response += f"💸 Budget: INR {Budget}\n"
        response += f"👥 Traveling with: {TYPE}\n"
        response += f"📍 Max Places Priority: {'Yes' if Ques else 'No'}\n\n"

        # Get hotel price and include in response
        hotel_name = Info[-1]
        price = get_hotel_price(hotel_name)

        response += f"🏨 *Accommodation*: {hotel_name}\n"
        response += f"💵 Price: INR {price}/day\n" if price else "Price: Not available.\n"
        response += "\n*Itinerary Suggestions:*\n"

        day_count = 1
        for item in Output:
            if "Day" in item:
                response += f"\n\n{item}"
            elif item.strip():  # Skip empty activities
                response += f"\n📅 Activity {day_count}: {item}"
                day_count += 1

        await query.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        await query.message.reply_text(f"❌ Error: {str(e)}")

    return ConversationHandler.END

# Function to cancel the conversation
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("🚫 Operation canceled. You can start again by typing /start.")
    return ConversationHandler.END

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],  # Fixed entry point
        states={
            VACATION_TYPE: [CallbackQueryHandler(vacation_type)],
            DURATION: [CallbackQueryHandler(duration)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, budget)],
            TRAVEL_TYPE: [CallbackQueryHandler(travel_type)],
            PRIORITY: [CallbackQueryHandler(priority)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Adding the greeting message handler for when the bot is opened without interaction
    application.add_handler(CommandHandler("greet", greet))

    application.add_handler(conv_handler)

    # Run Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    application.run_polling()

if __name__ == '__main__':
    main()
