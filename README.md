# TripSage: AI-Based Travel Planning System

## Introduction

**TripSage** is an innovative travel planning system that uses artificial intelligence to create highly personalized travel itineraries. Traditional travel planning tools often struggle with providing customized, budget-friendly, and preference-based recommendations. **TripSage** solves this by leveraging **Points of Interest (POI)** and **cosine similarity algorithms**, offering travel plans based on user-specific preferences, group characteristics, budget, and trip length. Whether you are a solo traveler, a family, or a group of friends, **TripSage** delivers itineraries that cater to your unique travel needs.

## Features

- **Personalized Recommendations**: Tailors itineraries based on user preferences (e.g., adventure, cultural, relaxing).
- **Cosine Similarity**: Matches users with relevant POIs based on their input.
- **Hotel Suggestions**: Optimizes hotel selection based on proximity to POIs and budget.
- **Dynamic Itinerary Generation**: Creates day-wise travel plans that adapt based on user priorities.
- **User-Friendly Interface**: Intuitive and easy-to-use interface for seamless interaction.
- **Budget Management**: Ensures that hotels and activities stay within the user’s budget.

## Methodology

The system is composed of the following core modules:

1. **Input Processing and Setup**: Users input their preferences (e.g., duration, group type, budget), which are processed into a numeric matrix for further computation.
   
2. **Cosine Similarity and POI Selection**: Using cosine similarity, the system calculates the best-matching POIs based on user preferences, sorting and ranking them for itinerary inclusion.
   
3. **Distance Clustering and Hotel Allocation**: Hotels are selected based on proximity to selected POIs and within the user's financial constraints.
   
4. **Itinerary Scheduling and Routing**: The system generates an optimized route for the traveler, considering time constraints and travel duration.
   
5. **Visualization**: The itinerary is displayed as a **Gantt chart**, showing a clear overview of activities and POIs for each day.

## Architecture

![System Architecture](path_to_architecture_diagram)  
*(Replace with actual path to your architecture diagram)*

## Installation

To set up the project on your local machine:

1. Clone the repository:

   ```bash
   git clone https://github.com/your_username/TripSage.git
   cd TripSage
   ```

2. Install the necessary dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   streamlit run app.py
   ```

## Usage

1. **Input Preferences**: The user provides details such as travel type, budget, trip duration, and group characteristics.
2. **Generate Itinerary**: The system processes the inputs and provides a personalized travel plan.
3. **Review Itinerary**: Users can review, modify, and finalize their itinerary using the visual Gantt chart.

## Requirements

- **Python 3.x**
- **Streamlit**
- **Numpy, Pandas, Plotly, Matplotlib**
- **Pickle for data serialization**

## Performance

TripSage outperforms traditional travel planning systems in terms of accuracy and personalization. The AI-driven approach ensures that itineraries align closely with user preferences and are updated dynamically.

## Future Improvements

- **Real-time Updates**: Integration with live data sources such as weather, flight schedules, and events.
- **Enhanced POI Data**: Expanding POI databases for better global coverage.
- **Niche Travel Experiences**: Offering itineraries for eco-tourism, luxury travel, and adventure sports.

## Contributing

If you'd like to contribute to **TripSage**, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Let me know if you’d like to add or modify any sections!
