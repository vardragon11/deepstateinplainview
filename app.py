from flask import Flask, render_template
import requests
import folium
import plotly 
import pandas as pd
#import geopandas as gpd

# Initialize Flask app
app = Flask(__name__)

# Here's a tuple containing U.S. state names and their abbreviations:
states = (
    ("Alabama", "AL"), ("Alaska", "AK"), ("Arizona", "AZ"), ("Arkansas", "AR"),
    ("California", "CA"), ("Colorado", "CO"), ("Connecticut", "CT"), ("Delaware", "DE"),
    ("Florida", "FL"), ("Georgia", "GA"), ("Hawaii", "HI"), ("Idaho", "ID"),
    ("Illinois", "IL"), ("Indiana", "IN"), ("Iowa", "IA"), ("Kansas", "KS"),
    ("Kentucky", "KY"), ("Louisiana", "LA"), ("Maine", "ME"), ("Maryland", "MD"),
    ("Massachusetts", "MA"), ("Michigan", "MI"), ("Minnesota", "MN"), ("Mississippi", "MS"),
    ("Missouri", "MO"), ("Montana", "MT"), ("Nebraska", "NE"), ("Nevada", "NV"),
    ("New Hampshire", "NH"), ("New Jersey", "NJ"), ("New Mexico", "NM"), ("New York", "NY"),
    ("North Carolina", "NC"), ("North Dakota", "ND"), ("Ohio", "OH"), ("Oklahoma", "OK"),
    ("Oregon", "OR"), ("Pennsylvania", "PA"), ("Rhode Island", "RI"), ("South Carolina", "SC"),
    ("South Dakota", "SD"), ("Tennessee", "TN"), ("Texas", "TX"), ("Utah", "UT"),
    ("Vermont", "VT"), ("Virginia", "VA"), ("Washington", "WA"), ("West Virginia", "WV"),
    ("Wisconsin", "WI"), ("Wyoming", "WY")
)

# Fetch data from API (FRED or BLS)
def fetch_economic_data():
    # Example: Using FRED API for unemployment data (Replace with your FRED API key)
    api_key = "ADD YOUR API KEY"
    for s,a in states:
        try:
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id={a}UR&api_key={api_key}&file_type=json"
            response = requests.get(url)
            
            # Check for successful API response
            if response.status_code == 200:
                data = response.json()['observations']
                df = pd.DataFrame(data)
                df = df[['date', 'value']]
                df['value'] = df['value'].astype(float)
                df['state'] = s
                df['date'] = pd.to_datetime(df['date'])
                threshold_dt = pd.Timestamp('2024-12-01')
                df_filter = df[df['date'] == threshold_dt]
                if a in 'AL':
                    master_df = df_filter
                else:
                    master_df = pd.concat([master_df,df_filter], ignore_index =True)
                    
            else:
                print("API Request Failed")
        except Exception as ee:
            print("API request failed: ",ee)
    return master_df

def get_eco_data():
     # Get the economic data
    data = fetch_economic_data()

    #what is the date we are looking at 
    dateof = data['date'][0]
    # we only need the the state and unemployement rate values
    df = data[['state','value']]
    leg_name = "Unemployment for the name (%) as of {dateof}"

    if data:
     create_map(df,leg_name)
    else:
        print("No data was provided..check up stream")

def get_edu_data():
    # Get the economic data
    data = pd.read_csv("ELC-Totals-by-State.csv")

    # we only need the the state and unemployement rate values
    df = data[['state','Total-L']]
    leg_name = "Worse Case 100% loss of Department of Education funding"

    if df:
        create_map(df,leg_name)
    else:
        print("No data was provided..check up stream")

# Generate a color-coded map based on economic data
def create_map(df, leg_name):
    # Get the economic data
    #data = fetch_economic_data()

    if df is None:
        return "Failed to retrieve data"

    # Load state coordinates (GeoJSON format)
    geo_json = 'https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json'

    # Create a Folium map centered on the U.S.
    m = folium.Map(location=[37.8, -96], zoom_start=4)
#     #what is the date we are looking at 
#     dateof = data['date'][0]
#     # we only need the the state and unemployement rate values
#     df = data[['state','value']]

    # Color scale for the map
    folium.Choropleth(
        geo_data=geo_json,
        name='choropleth',
        data=df,
        columns=['state','value'],
        key_on='feature.properties.name',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=leg_name
    ).add_to(m)
    # Save map as HTML
    m.save('templates/unemp_map.html')
    
    return 'Map created successfully'


def create_doed_map(data):
    # Get the economic data
    data = fetch_economic_data()

# Define route to display map
@app.route('/')
def home():
     create_map()
     return render_template('map.html')

# Run the app
if __name__ == '__main__':
     app.run(debug=True)