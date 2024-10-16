# TripSage: AI-Based Travel Planning System

## Introduction

TripSage is an innovative AI-powered travel recommendation system designed to create personalized itineraries based on user preferences, budget, group size, and trip length. Using **Cosine Similarity and Points of Interest (POI) algorithms**, TripSage provides travelers with tailored travel plans that enhance their overall experience.

This particular version of TripSage is specifically designed with data from **_Chennai_** and generates itineraries focused on locations within the city. Future improvements will include expanding trip planning capabilities to cover other major cities across India, allowing for a broader range of destination options.

## Features

- *Custom Itinerary Generation*: Tailors itineraries based on user input.
- *POI Matching via Cosine Similarity*: Recommends activities and destinations based on user preferences.
- *Hotel Recommendations*: Suggests accommodations that fit within the user's budget and location.
- *Day-wise Plans*: Generates daily schedules and routes, visualized via Gantt charts.
- *Budget and Preference-Based Optimization*: Keeps the plan aligned with user financial constraints while ensuring relevant recommendations.


### Key Files:

1. **data/**: This directory contains several CSV files used for POI data, distance matrices, and hotel information. These datasets are central to generating itineraries and recommendations.
   
2. **main.py**: The main script that runs the **TripSage* application. Users interact with this script to input travel preferences and generate their personalized itinerary.

3. **POI_notebook.ipynb**: Jupyter Notebook for testing and processing Points of Interest (POI) data. Helpful for exploring and improving the recommendation system.

4. **Function_call_terminal.py**: Utility script used for invoking key functions from the terminal. This file can be used to run various internal processes from the command line.

## Installation

To set up the project on your local machine:

1. Clone the repository:

   bash
   git clone https://github.com/botkesaksham/TripSage-AI-Travel-Recommendation-System.git
   cd TripSage-AI-Travel-Recommendation-System
   

2. Install the necessary dependencies:

   bash
   pip install -r requirements.txt
   

3. Run the main application:

   bash
   python -m streamlit run main.py
   

## How it works

1. *Input Preferences*: Users can provide trip details, including travel type, budget, group size, and trip duration.
2. *Generate Recommendations*: The system will process the inputs and suggest relevant POIs, hotels, and activities.

## Requirements

- *Python 3.x*
- *Streamlit* (optional for the web interface)
- *Numpy, Pandas, Matplotlib, Plotly*
- *Telegram API* (if using the Telegram bot)

## Future Improvements

- *Real-time Data*: Incorporating live travel data (flights, weather, etc.) into itinerary suggestions.
- *Broader POI Database*: Expanding POI data for more global destinations.
- *Social Integration*: Allowing travelers to share itineraries or seek advice from other users.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.
