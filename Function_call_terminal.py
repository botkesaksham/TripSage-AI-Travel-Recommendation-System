import pandas as pd
from poi_trialmerged import FINAL

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

def main():
    vacation_types = ['Adventure and Outdoors', 'Spiritual', 'City Life', 'Cultural', 'Relaxing']
    travel_groups = ['Family', 'Friends', 'Individual']

    print("Get Started. Select your preferences!")

    # Gather user preferences
    print("\nSelect Vacation Type (comma-separated):")
    for idx, vtype in enumerate(vacation_types):
        print(f"{idx + 1}. {vtype}")
    
    Type_input = input("Enter the numbers corresponding to your choices: ")
    Type = [vacation_types[int(i) - 1] for i in Type_input.split(',')]
    
    Duration = int(input("Duration (days) [1-7]: "))
    Budget = int(input("Budget (INR) [1000-150000]: "))
    
    print("\nWho are you traveling with?")
    for idx, group in enumerate(travel_groups):
        print(f"{idx + 1}. {group}")
    
    TYPE_index = int(input("Enter the number corresponding to your choice: ")) - 1
    TYPE = travel_groups[TYPE_index]
    
    Ques = input("Is covering maximum places a priority? (Yes/No): ")

    # Call the FINAL function and handle the result
    try:
        Output, Info = FINAL(Type, Duration, Budget, TYPE, Ques)

        # Display user inputs and the suggested itinerary
        print("\nTravel Details:")
        print(f"Vacation Type: {', '.join(Type)}")
        print(f"Duration: {Duration} days")
        print(f"Budget: INR {Budget}")
        print(f"Traveling with: {TYPE}")
        print(f"Covering Maximum Places Priority: {Ques}")

        # Get hotel price and display
        hotel_name = Info[-1]  # Assuming the last info item is the hotel name
        price = get_hotel_price(hotel_name)

        if price is not None:
            print(f"Suggested Accommodation: {hotel_name}")
            print(f"Price: INR {price}/day")
            print("*Prices may vary due to seasonal demands.")
        else:
            print(f"Suggested Accommodation: {hotel_name}")
            print("Price: Not available")

        print("\nSuggested Itinerary:")
        day_count = 1
        for item in Output:
            if "Day" in item:
                print(f"\n{item}")
            elif item.strip():
                print(f"Activity {day_count}: {item}")
                day_count += 1

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main() 