import pandas as pd
from flask import Flask, request, jsonify
from poi_trialmerged import FINAL

app = Flask(__name__)

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

@app.route('/plan_trip', methods=['POST'])
def plan_trip():
    # Get JSON data from the request
    data = request.json

    vacation_types = ['Adventure and Outdoors', 'Spiritual', 'City Life', 'Cultural', 'Relaxing']
    travel_groups = ['Family', 'Friends', 'Individual']

    # Extract user preferences
    try:
        Type_input = data['vacation_type']  # Expecting a list of vacation types
        Duration = int(data['duration'])
        Budget = int(data['budget'])
        TYPE = data['travel_group']  # Travel group as a string
        Ques = data['max_places_priority']  # Yes or No
        
        # Call the FINAL function and handle the result
        Output, Info = FINAL(Type_input, Duration, Budget, TYPE, Ques)

        # Prepare response
        response = {
            "vacation_type": Type_input,
            "duration": Duration,
            "budget": Budget,
            "traveling_with": TYPE,
            "max_places_priority": Ques,
        }

        # Get hotel price and include in response
        hotel_name = Info[-1]  # Assuming the last info item is the hotel name
        price = get_hotel_price(hotel_name)

        if price is not None:
            response["suggested_accommodation"] = {
                "hotel_name": hotel_name,
                "price": price
            }
        else:
            response["suggested_accommodation"] = {
                "hotel_name": hotel_name,
                "price": "Not available"
            }

        # Prepare itinerary
        itinerary = []
        day_count = 1
        for item in Output:
            if "Day" in item:
                itinerary.append({"day": item})
            elif item.strip():
                itinerary.append({"activity": f"Activity {day_count}: {item}"})
                day_count += 1
        response["itinerary"] = itinerary

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
