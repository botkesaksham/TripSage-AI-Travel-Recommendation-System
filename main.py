import streamlit as st  
import pathlib
import pickle  
from poi_trialmerged import FINAL  
import pandas as pd  

# Function to load CSS from the 'assets' folder
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the external CSS
css_path = pathlib.Path("styles.css")
load_css(css_path)

st.title('Get Started. Select your preferences!')

# Load the saved itinerary data
# with open("lol.pkl", "rb") as pickle_in:  
#     load_lol = pickle.load(pickle_in)  

# Function to process and return the output
def output_main(Type, Duration, Budget, TYPE, Ques):  
    output, info = FINAL(Type, Duration, Budget, TYPE, Ques)
    return [output, info]

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
        st.error(f"Error loading hotel data: {e}")
        return None

def main():  
    vacation_types = ['Adventure and Outdoors', 'Spiritual', 'City Life', 'Cultural', 'Relaxing']  
    travel_groups = ['Family', 'Friends', 'Individual']  

    # Sidebar input section
    with st.sidebar:
        # Add your logo or image here in the sidebar
        st.image("data/images.png",  width=300)  # Add the path to your logo
        st.header("Provide Your Preferences") 

        Type = st.multiselect("Vacation type according to priority:", vacation_types)  
        Duration = st.number_input("Duration (days)", min_value=1, max_value=7, step=1)  
        Budget = st.number_input("Budget (INR)", min_value=1000, max_value=150000, step=500)  
        TYPE = st.selectbox("Who are you traveling with?", travel_groups)  
        Ques = st.radio("Is covering maximum places a priority?", ['Yes', "No"])  

        cutoff = Budget / Duration
        recommend_button = st.button("What do you recommend?")

    # Output section when the user clicks on the button
    if recommend_button:
        try:
            RESULT = output_main(Type, Duration, Budget, TYPE, Ques)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            if cutoff < 260:
                st.subheader("Irrational. Try increasing your Budget or scaling down the Duration.")  
            else:
                st.subheader("Irrational. Please check your Inputs.")
            return

        Output, Info = RESULT

        # Display user inputs and the suggested itinerary as a table
        st.markdown('<h2 style="color:white;">Travel Details </h2>', unsafe_allow_html=True)
        
        # Table for inputs
        st.markdown(f'''
        <table>
            <tr>
                <th>Vacation Type</th>
                <td>{", ".join(Type)}</td>
            </tr>
            <tr>
                <th>Duration</th>
                <td>{Duration} days</td>
            </tr>
            <tr>
                <th>Budget</th>
                <td>INR {Budget}</td>
            </tr>
            <tr>
                <th>Traveling with</th>
                <td>{TYPE}</td>
            </tr>
            <tr>
                <th>Covering Maximum Places Priority</th>
                <td>{Ques}</td>
            </tr>
        </table>
        ''', unsafe_allow_html=True)

        # Suggested Itinerary with custom margin and styles
        st.markdown('<div class="suggested-itinerary">', unsafe_allow_html=True)

        # Get hotel price and display
        hotel_name = Info[-1]
        price = get_hotel_price(hotel_name)

        if price is not None:
            st.markdown(f'<p class="suggested-hotel">Suggested Accommodation: {hotel_name}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="price">Price: INR {price}/day</p>', unsafe_allow_html=True)
            st.markdown('<p class="note">*Prices may vary due to seasonal demands.</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="suggested-hotel">Suggested Accommodation: {hotel_name}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="price">Price: Not available</p>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        st.subheader('Suggested Itinerary')

        # Timeline layout
        st.markdown('<div class="timeline">', unsafe_allow_html=True)
        day_count = 1

        for item in Output:
            if "Day" in item:
                st.markdown(f'<h3>{item}</h3>', unsafe_allow_html=True)
            elif item.strip():
                st.markdown(f'''
                <div class="timeline-item">
                    <div class="time">Activity {day_count}</div>
                    <div class="content">
                        <p>{item}</p>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                day_count += 1

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == '__main__':  
    main()
