import discord
from discord.ext import commands
import pandas as pd
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from threading import Thread
from poi_trialmerged import FINAL

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Set up intents and bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

def get_hotel_price(hotel_name):
    """Retrieve the price of a hotel by its name."""
    try:
        hotel_data = pd.read_csv('data/chennai_Hotels.csv')
        hotel_row = hotel_data[hotel_data['Hotel'] == hotel_name]
        if not hotel_row.empty:
            return hotel_row['Price'].values[0]
        return None
    except Exception as e:
        print(f"Error loading hotel data: {e}")
        return None

async def send_long_message(channel, content):
    """Send long messages in chunks of 2000 characters."""
    for i in range(0, len(content), 2000):
        await channel.send(content[i:i + 2000])

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    """Event triggered when a message is sent in a channel."""
    if message.author.bot:
        return

    if bot.user.mentioned_in(message):
        await message.channel.send("Hello! How can I assist you with your trip? Use `!start` to begin your vacation itinerary creation!")

    await bot.process_commands(message)

@bot.command(name="start")
async def start(ctx):
    """Start the vacation itinerary creation process."""
    vacation_types = ['Adventure and Outdoors', 'Spiritual', 'City Life', 'Cultural', 'Relaxing']
    travel_groups = ['Family', 'Friends', 'Individual']

    # Ask for vacation type
    vacation_msg = "\nSelect Vacation Type (comma-separated):\n" + "\n".join(f"{idx + 1}. {vtype}" for idx, vtype in enumerate(vacation_types))
    await ctx.send(vacation_msg)

    type_response = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content.isdigit())
    Type_input = type_response.content
    Type = [vacation_types[int(i) - 1] for i in Type_input.split(',')]

    # Ask for duration
    await ctx.send("Duration (days) [1-7]:")
    duration_response = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content.isdigit())
    Duration = int(duration_response.content)

    # Ask for budget
    await ctx.send("Budget (INR) [1000-150000]:")
    budget_response = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content.isdigit())
    Budget = int(budget_response.content)

    # Ask for travel group
    travel_msg = "\nWho are you traveling with?\n" + "\n".join(f"{idx + 1}. {group}" for idx, group in enumerate(travel_groups))
    await ctx.send(travel_msg)

    type_index_response = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content.isdigit())
    TYPE_index = int(type_index_response.content) - 1
    TYPE = travel_groups[TYPE_index]

    # Ask if covering maximum places is a priority
    await ctx.send("Is covering maximum places a priority? (Yes/No):")
    ques_response = await bot.wait_for("message", check=lambda m: m.author == ctx.author)
    Ques = ques_response.content.strip().lower()

    # Call the FINAL function and handle the result
    try:
        Output, Info = FINAL(Type, Duration, Budget, TYPE, Ques)

        response_msg = (
            f"**Travel Details:**\n"
            f"Vacation Type: {', '.join(Type)}\n"
            f"Duration: {Duration} days\n"
            f"Budget: INR {Budget}\n"
            f"Traveling with: {TYPE}\n"
            f"Covering Maximum Places Priority: {Ques.capitalize()}\n"
        )

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

@app.route('/interactions', methods=['POST'])
def interactions():
    """Handle interactions from Discord."""
    data = request.json

    # Verify the interaction
    if data['type'] == 1:  # This is a Ping
        return jsonify({'type': 1})  # Respond with Pong

    # Further processing can go here
    # Handle command interactions, etc.
    # Example: Call a function based on the interaction data

    return jsonify({'type': 4, 'data': {'content': 'This is a response message'}})  # Reply to the interaction

@app.route('/')
def home():
    return "Bot is running!", 200

def run_flask():
    """Run the Flask app."""
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

# Only run the bot if this script is executed directly
if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    bot.run(TOKEN)
