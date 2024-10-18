import os
from flask import Flask, request
import pandas as pd
from poi_trialmerged import FINAL
from twilio.twiml.messaging_response import MessagingResponse

# Initialize the Flask app
app = Flask(__name__)

# Load the Twilio WhatsApp number from environment variables
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER") # Twilio's sandbox number


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

# Function to handle incoming WhatsApp messages
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From')

    # Initialize user data if not present
    if from_number not in user_data:
        user_data[from_number] = {
            'stage': 0,
            'vacation_types': [],
            'duration': None,
            'budget': None,
            'travel_group': 'Family',  # Defaulting to Family
            'cover_places_priority': 'No'  # Defaulting to No
        }

    stage = user_data[from_number]['stage']

    # Initialize Twilio response
    response = MessagingResponse()

    if stage == 0:  # Starting stage
        response_message = "Welcome! Let's get started with your travel preferences.\n" \
                           "Choose a vacation type by entering numbers separated by commas:\n" \
                           "1. Adventure and Outdoors\n" \
                           "2. Spiritual\n" \
                           "3. City Life\n" \
                           "4. Cultural\n" \
                           "5. Relaxing"
        response.message(response_message)
        user_data[from_number]['stage'] = 1

    elif stage == 1:  # Handling vacation type selection
        try:
            selected_types = [int(i.strip()) for i in incoming_msg.split(',')]
            vacation_types = ['Adventure and Outdoors', 'Spiritual', 'City Life', 'Cultural', 'Relaxing']
            selected_vacation_types = [vacation_types[i - 1] for i in selected_types]
            user_data[from_number]['vacation_types'] = selected_vacation_types

            response_message = f"You selected: {', '.join(selected_vacation_types)}.\n" \
                               "Now, please enter the trip duration in days (e.g., 3):"
            response.message(response_message)
            user_data[from_number]['stage'] = 2  # Move to the next stage

        except Exception as e:
            print(f"Error in vacation type selection: {e}")
            response.message("Invalid selection. Please try again.")

    elif stage == 2:  # Handling duration input
        try:
            duration = int(incoming_msg)
            user_data[from_number]['duration'] = duration
            
            response_message = "Enter your budget in INR (e.g., 50000):"
            response.message(response_message)
            user_data[from_number]['stage'] = 3  # Move to the next stage

        except ValueError:
            response.message("Please enter a valid number for duration.")

    elif stage == 3:  # Handling budget input
        try:
            budget = int(incoming_msg)
            user_data[from_number]['budget'] = budget
            
            response_message = "Who are you traveling with? (Family/Friends/Individual):"
            response.message(response_message)
            user_data[from_number]['stage'] = 4  # Move to the next stage

        except ValueError:
            response.message("Please enter a valid number for budget.")

    elif stage == 4:  # Handling travel group input
        travel_group = incoming_msg.strip()
        if travel_group in ['Family', 'Friends', 'Individual']:
            user_data[from_number]['travel_group'] = travel_group
            
            response_message = "Is covering maximum places a priority? (Yes/No):"
            response.message(response_message)
            user_data[from_number]['stage'] = 5  # Move to the next stage
        else:
            response.message("Please enter a valid travel group (Family/Friends/Individual).")

    elif stage == 5:  # Handling priority input
        cover_places_priority = incoming_msg.strip().capitalize()
        if cover_places_priority in ['Yes', 'No']:
            user_data[from_number]['cover_places_priority'] = cover_places_priority
            
            # Gather all user inputs
            vacation_types = user_data[from_number]['vacation_types']
            duration = user_data[from_number]['duration']
            budget = user_data[from_number]['budget']
            travel_group = user_data[from_number]['travel_group']
            priority = user_data[from_number]['cover_places_priority']

            # Call the FINAL function
            try:
                Output, Info = FINAL(vacation_types, duration, budget, travel_group, priority)

                # Debugging prints
                print(f"Output: {Output}")
                print(f"Info: {Info}")

                # Send Itinerary back to the user
                itinerary = "\n".join(Output)
                response.message(f"Your suggested itinerary:\n{itinerary}")

                # Include hotel information
                hotel_name = Info[-1]  # Assuming the last info item is the hotel name
                price = get_hotel_price(hotel_name)
                if price:
                    response.message(f"Suggested Hotel: {hotel_name}, Price: INR {price}/day")
                else:
                    response.message(f"Suggested Hotel: {hotel_name}, Price: Not available")

                # Reset user data after processing
                del user_data[from_number]

            except Exception as e:
                print(f"Error processing FINAL function: {e}")  # Debugging the exception
                response.message("Error processing your request. Please try again.")

        else:
            response.message("Please answer with 'Yes' or 'No'.")

    else:
        response.message("Invalid input. Type 'Start' to begin.")
    
    return str(response), 200

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
