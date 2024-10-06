import streamlit as st  
import pickle  
from poi_trialmerged import FINAL  
import pandas as pd  

# Define custom styles for the gradient background and other elements
streamlit_style = """
    <style>
     @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,100..900;1,9..144,100..900&family=Kanit:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

        [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(109.6deg, rgb(0, 0, 0) 11.2%, rgb(6, 82, 90) 91.1%);
        background: linear-gradient(109.6deg, rgb(0, 0, 0) 11.2%, rgb(3, 56, 61) 91.1%);

        margin: 0px !important;
      }

      [data-testid="stAppViewContainer"] {
        max-width: 100% !important;;
        padding: 0px !important;
        margin: 0px !important;
      }
      [data-testid="stAppViewBlockContainer"] {
        max-width:70rem !important;;
      }

      [data-testid="stHeader"] {
        background: transparent !important;;
      } 
      [data-testid="stSidebar"] {
        background:white !important;;
        backdrop-filter: blur(200px);
      }

      .timeline {
        position: relative;
        margin: 0 auto;
        padding: 20px 0;
        width: 80%;
        max-width: 900px;
      }

      .timeline-item {
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 10px;
        font-family: 'Lato', sans-serif;
        font-size: 18px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        background-color: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(20px);
        color: black; 
      }

      .time {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #333;
      }

      .content {
        font-size: 16px;
        line-height: 1.6;
        color: #444;
      }

      .itinerary-header {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        color: white; 
      }

      .stButton > button {
        background-color: #28a745;
        color: white;
        font-size: 16px;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        cursor: pointer;
      }

      .stButton > button:hover {
        background-color: #218838;
      }

      h1,h3, h4, h5, h6 {
        color: white !important;
      }

      p {
        color: black;
        font-size:1.1rem;
        font-family:bold;
      }

      table {
        width: 100%;
        border-collapse: collapse;
        color: white;
      }

      th, td {
        padding: 10px;
        text-align: left;
        border: 1px solid white !important; /* Enforcing white border */
      }

      /* Custom styles for Suggested Itinerary section */
      .suggested-itinerary {
        margin-top: 30px; /* Adds margin-top to Suggested Itinerary */
      }

      .suggested-hotel {
        font-size: 22px;  /* Larger font size */
        color: yellow;    /* Yellow color for hotel/accommodation */
        font-weight: bold;
      }

      .price {
        color: yellow;  /* Red color for price text */
        font-size: 18px;  /* Font size for the price */
        font-weight: bold;
      }

      .note {
        font-size: 16px;
        color: red;
      }
    </style>
"""
st.markdown(streamlit_style, unsafe_allow_html=True)

st.title('Get Started. Select your preferences!')

# Load the saved itinerary data
with open("lol.pkl", "rb") as pickle_in:  
    load_lol = pickle.load(pickle_in)  

# Function to process and return the output
def output_main(Type, Duration, Budget, TYPE, Ques):  
    output, info = FINAL(Type, Duration, Budget, TYPE, Ques)
    return [output, info]

# Function to get hotel price from the CSV file
def get_hotel_price(hotel_name):
    try:
        hotel_data = pd.read_csv('data/Chennai_Hotels.csv')
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
        st.image("data/images.png",  width=370)  # Add the path to your logo
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
