import discord
from discord.ext import commands
import pandas as pd
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
from poi_trialmerged import FINAL

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

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

# Function to send long messages
async def send_long_message(channel, content):
    """Send long messages in chunks of 2000 characters."""
    for i in range(0, len(content), 2000):
        await channel.send(content[i:i + 2000])

# Event that gets called when the bot is ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Check if the bot is mentioned in a message
@bot.event
async def on_message(message):
    # Ignore messages from bots
    if message.author.bot:
        return

    # Check if the bot is mentioned
    if bot.user.mentioned_in(message):
        await message.channel.send("Hello! How can I assist you with your trip? Use `!start` to begin your vacation itinerary creation!")

    # Process commands if any
    await bot.process_commands(message)

# Command to start the vacation itinerary creation process
@bot.command(name="start")
async def start(ctx):
    vacation_types = ['Adventure and Outdoors', 'Spiritual', 'City Life', 'Cultural', 'Relaxing']
    travel_groups = ['Family', 'Friends', 'Individual']

    # Ask for vacation type
    vacation_msg = "\nSelect Vacation Type (comma-separated):\n"
    for idx, vtype in enumerate(vacation_types):
        vacation_msg += f"{idx + 1}. {vtype}\n"
    await ctx.send(vacation_msg)
    
    def check_type_input(message):
        return message.author == ctx.author and message.content.isdigit()

    type_response = await bot.wait_for("message", check=check_type_input)
    Type_input = type_response.content
    Type = [vacation_types[int(i) - 1] for i in Type_input.split(',')]

    # Ask for duration
    await ctx.send("Duration (days) [1-7]:")
    duration_response = await bot.wait_for("message", check=check_type_input)
    Duration = int(duration_response.content)

    # Ask for budget
    await ctx.send("Budget (INR) [1000-150000]:")
    budget_response = await bot.wait_for("message", check=check_type_input)
    Budget = int(budget_response.content)

    # Ask for travel group
    travel_msg = "\nWho are you traveling with?\n"
    for idx, group in enumerate(travel_groups):
        travel_msg += f"{idx + 1}. {group}\n"
    await ctx.send(travel_msg)
    
    type_index_response = await bot.wait_for("message", check=check_type_input)
    TYPE_index = int(type_index_response.content) - 1
    TYPE = travel_groups[TYPE_index]

    # Ask if covering maximum places is a priority
    await ctx.send("Is covering maximum places a priority? (Yes/No):")
    ques_response = await bot.wait_for("message", check=lambda message: message.author == ctx.author)
    Ques = ques_response.content

    # Call the FINAL function and handle the result
    try:
        Output, Info = FINAL(Type, Duration, Budget, TYPE, Ques)

        response_msg = f"**Travel Details:**\n" \
                       f"Vacation Type: {', '.join(Type)}\n" \
                       f"Duration: {Duration} days\n" \
                       f"Budget: INR {Budget}\n" \
                       f"Traveling with: {TYPE}\n" \
                       f"Covering Maximum Places Priority: {Ques}\n"

        # Get hotel price and display
        hotel_name = Info[-1]  
        price = get_hotel_price(hotel_name)

        if price is not None:
            response_msg += f"**Suggested Accommodation:** {hotel_name}\n" \
                            f"Price: INR {price}/day\n" \
                            "*Prices may vary due to seasonal demands.\n"
        else:
            response_msg += f"**Suggested Accommodation:** {hotel_name}\nPrice: Not available\n"

        # Display itinerary
        response_msg += "\n**Suggested Itinerary:**\n"
        day_count = 1
        for item in Output:
            if "Day" in item:
                response_msg += f"\n{item}\n"
            elif item.strip():
                response_msg += f"Activity {day_count}: {item}\n"
                day_count += 1

        await send_long_message(ctx.channel, response_msg)

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

# The following function will run the Flask app but it shouldn't be called directly
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

# The Flask app will be served by Gunicorn when you deploy, so we don't need to start it here.

# Only run the bot if this script is executed directly
if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    bot.run(TOKEN)
