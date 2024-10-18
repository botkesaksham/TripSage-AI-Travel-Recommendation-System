import os
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import pandas as pd
from poi_trialmerged import FINAL

# Initialize the Flask app
app = Flask(__name__)

# Load Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# In-memory user data storage for simplicity
user_data = {}

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

# Function to send an SMS with the itinerary
def send_sms(to_number, message):
    try:
        # Debugging statement to print the numbers
        print(f"Sending SMS from {TWILIO_PHONE_NUMBER} to {to_number}")

        # Ensure that 'to_number' is different from 'TWILIO_PHONE_NUMBER'
        if to_number == TWILIO_PHONE_NUMBER:
            print("Error: 'To' number is the same as 'From' number. Cannot send SMS.")
            return
        
        sms = client.messages.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            body=message
        )
        print(f"SMS sent: {sms.sid}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

# Function to make a call with a simple test message
def make_call(to_number):
    try:
        call = client.calls.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            url="https://7bba-2401-4900-1f2a-25a6-f901-67e0-b5e4-355c.ngrok-free.app/voice"  # Replace with your ngrok URL
        )
        return call.sid
    except Exception as e:
        return str(e)

# Route to handle call initiation
@app.route('/start_call/<phone_number>', methods=['GET'])
def start_call(phone_number):
    call_sid = make_call(phone_number)
    return f"Call initiated. SID: {call_sid}"

# Route to handle voice response during the call
@app.route('/voice', methods=['POST'])
def voice_reply():
    from_number = request.values.get('From')

    # Initialize user data if not present
    if from_number not in user_data:
        user_data[from_number] = {
            'stage': 0,
            'vacation_types': [],
            'duration': None,
            'budget': None,
            'travel_group': 'Family',
            'cover_places_priority': 'No'
        }

    stage = user_data[from_number]['stage']
    response = VoiceResponse()

    if stage == 0:  # Starting stage
        response.say("Welcome to the TripSage Travel Planning Bot for Chennai City!", voice='alice')
        response.say("Press 1 for Adventure and Outdoors, 2 for Spiritual, 3 for City Life, 4 for Cultural, and 5 for Relaxing.", voice='alice')
        response.gather(input='dtmf', action='/voice/vacation_type', timeout=5)

    return str(response)

# Route to handle vacation type selection
@app.route('/voice/vacation_type', methods=['POST'])
def vacation_type():
    from_number = request.values.get('From')
    incoming_msg = request.values.get('Digits').strip()

    response = VoiceResponse()
    vacation_types = {
        "1": "Adventure and Outdoors",
        "2": "Spiritual",
        "3": "City Life",
        "4": "Cultural",
        "5": "Relaxing"
    }

    selected_type = vacation_types.get(incoming_msg)
    if selected_type:
        user_data[from_number]['vacation_types'].append(selected_type)
        response.say(f"You selected {selected_type}. Please enter the trip duration in days, followed by the pound sign.", voice='alice')
        response.gather(input='dtmf', action='/voice/duration', timeout=5)
        user_data[from_number]['stage'] = 2
    else:
        response.say("Sorry, I didn't understand that. Please select a valid option.", voice='alice')
        response.redirect('/voice')

    return str(response)

# Route to handle trip duration input
@app.route('/voice/duration', methods=['POST'])
def trip_duration():
    from_number = request.values.get('From')
    duration = request.values.get('Digits').strip()

    response = VoiceResponse()
    try:
        user_data[from_number]['duration'] = int(duration)
        response.say(f"Your trip will last {duration} days. Please provide your budget in INR followed by the pound sign.", voice='alice')
        response.gather(input='dtmf', action='/voice/budget', timeout=5)
        user_data[from_number]['stage'] = 3
    except ValueError:
        response.say("Please enter a valid number of days.", voice='alice')
        response.redirect('/voice/duration')

    return str(response)

# Route to handle budget input
@app.route('/voice/budget', methods=['POST'])
def trip_budget():
    from_number = request.values.get('From')
    budget = request.values.get('Digits').strip()

    response = VoiceResponse()
    try:
        user_data[from_number]['budget'] = int(budget)
        response.say(f"Your budget is set to {budget} INR. Who are you traveling with? Press 1 for Family, 2 for Friends, or 3 for Individual.", voice='alice')
        response.gather(input='dtmf', action='/voice/group', timeout=5)
        user_data[from_number]['stage'] = 4
    except ValueError:
        response.say("Please enter a valid budget in INR.", voice='alice')
        response.redirect('/voice/budget')

    return str(response)

# Route to handle travel group input
@app.route('/voice/group', methods=['POST'])
def travel_group():
    from_number = request.values.get('From')
    group = request.values.get('Digits').strip()

    response = VoiceResponse()
    if group == '1':
        user_data[from_number]['travel_group'] = 'Family'
    elif group == '2':
        user_data[from_number]['travel_group'] = 'Friends'
    elif group == '3':
        user_data[from_number]['travel_group'] = 'Individual'
    else:
        response.say("Please respond with 1 for Family, 2 for Friends, or 3 for Individual.", voice='alice')
        response.redirect('/voice/group')
        return str(response)

    response.say(f"You are traveling with {user_data[from_number]['travel_group']}. Is covering maximum places a priority? Press 1 for Yes or 2 for No.", voice='alice')
    response.gather(input='dtmf', action='/voice/priority', timeout=5)
    user_data[from_number]['stage'] = 5

    return str(response)

# Route to handle priority input
@app.route('/voice/priority', methods=['POST'])
def cover_places_priority():
    from_number = request.values.get('From')
    priority = request.values.get('Digits').strip()

    response = VoiceResponse()
    if priority == '1':
        user_data[from_number]['cover_places_priority'] = 'Yes'
    elif priority == '2':
        user_data[from_number]['cover_places_priority'] = 'No'
    else:
        response.say("Please respond with 1 for Yes or 2 for No.", voice='alice')
        response.redirect('/voice/priority')
        return str(response)

    # Gather all user inputs
    vacation_types = user_data[from_number]['vacation_types']
    duration = user_data[from_number]['duration']
    budget = user_data[from_number]['budget']
    travel_group = user_data[from_number]['travel_group']
    priority = user_data[from_number]['cover_places_priority']

    # Debugging: Print user inputs
    print(f"User Input - Vacation Types: {vacation_types}, Duration: {duration}, Budget: {budget}, Travel Group: {travel_group}, Priority: {priority}")

    # Call the FINAL function
    try:
        Output, Info = FINAL(vacation_types, duration, budget, travel_group, priority)

        # Debugging: Print output and info
        print(f"FINAL Function Output: {Output}")
        print(f"FINAL Function Info: {Info}")

        # Send Itinerary back to the user
        itinerary = "\n".join(Output)
        response.say(f"Your suggested itinerary is as follows: {itinerary}")

        # Include hotel information
        hotel_name = Info[-1]  # Assuming the last info item is the hotel name
        price = get_hotel_price(hotel_name)
        if price:
            response.say(f"Suggested Hotel: {hotel_name}, Price: INR {price}")

        # Send SMS with the itinerary (if applicable)
        send_sms("+919840830415", f"Your suggested itinerary is as follows:\n{itinerary}")
        
    except Exception as e:
        response.say("An error occurred while generating your itinerary. Please try again later.", voice='alice')
        print(f"Error during itinerary generation: {e}")

    return str(response)

if __name__ == '__main__':
    app.run(debug=True)
