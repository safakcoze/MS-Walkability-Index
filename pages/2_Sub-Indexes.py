import streamlit as st
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import folium.plugins

# LAYOUT -------------------------------------
st.set_page_config(page_title="Sub-Indexes", page_icon="🚶", initial_sidebar_state="auto", layout="wide")
st.markdown(
    "<h1>Walkability Index <b style='color:red;'> <span style='font-size:1.2em;'>| Sub-Indexes</span></b></h1>", 
    unsafe_allow_html=True
)

# SIDEBAR AND MS LOGO -------------------------------------
# Create space and push the image to the bottom
st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)  # Adds spacing

# Add logo at the bottom
st.sidebar.markdown("<p style='text-align:center; font-size:14px;'>© 2024 Walkability Index | Developed by Şafak Çöze</p>", unsafe_allow_html=True)

# RELATED DATASETS -------------------------------------
# Load GeoJSON files using GeoPandas
districts_gdf = gpd.read_file('Data/ms_districts_prj.geojson')
streets_gdf = gpd.read_file('Data/ms_streets_prj.geojson')

# Remove datetime columns if they exist
districts_gdf = districts_gdf.select_dtypes(exclude=['datetime'])

# Get the district names
district_names = districts_gdf['NAME_STADT'].unique()

# Create two columns for district and sub-index selection
col1, col2, col3 = st.columns(3)

with col1:
    # Place District selection
    selected_district = st.selectbox("Select a District", district_names)

with col2:
    # Define sub-indices list
    sub_indices = ['Proximity Score', 'Landscape and Nature Score', 'Pedestrian Infrastructure Score', 
                   'Pedestrian Comfort Score', 'Outdoor Thermal Comfort - August', 'Outdoor Thermal Comfort - October']

    # Select sub-index for visualization
    selected_sub_index = st.selectbox("Select a Sub-Index", sub_indices)

with col3:
    color_theme = st.selectbox("Select a Color Theme", ["Viridis", "YlGnBu", "Magma", "Neptunes", "Hot-Cold"])

# Add description paragraph based on the selected sub-index
with st.expander("Brief Introduction"):
    if selected_sub_index == "Proximity Score":
        st.markdown("""
        **Proximity Sub-Index** includes land-use diversity, public amenities, commercial amenities, and public transport stations
        indicators to calculate the sub-index score.
        """)
    if selected_sub_index == "Landscape and Nature Score":
        st.markdown("""
        **Landscape and Nature Sub-Index** includes parks, open spaces, blue infrastructure such as lake and canals, landmarks, and 
        urban furniture indicators to calculate the sub-index score.
        """)
    if selected_sub_index == "Pedestrian Infrastructure Score":
        st.markdown("""
        **Pedestrian Infrastructure Sub-Index** includes street lightings data from Stadt-Münster and OpenStreetMaps, 
        street connectivity data as nodes data from OSMnx library to calculate the sub-index score.
        """)
    if selected_sub_index == "Pedestrian Comfort Score":
        st.markdown("""
        **Pedestrian Infrastructure Sub-Index** includes slope, obstacles, and presence of barriers indicators
        to calculate the sub-index score.
        """)
    elif selected_sub_index == "Outdoor Thermal Comfort - August":
        st.markdown("""
        **Outdoor Thermal Comfort Sub-Index** evaluates factors such as air temperature, relative humidity, wind speed, precipitation, 
        and presence of trees which influence the outdoor thermal comfort in urban areas. August is referenced by the date of August 13, 
        2024, and corresponds to Scenario-I as under heat.
        """)
    elif selected_sub_index == "Outdoor Thermal Comfort - October":
        st.markdown("""
        **Outdoor Thermal Comfort Sub-Index** evaluates factors such as air temperature, relative humidity, wind speed, precipitation, 
        and presence of trees which influence the outdoor thermal comfort in urban areas. October is based on the date of October 9, 2024, and corresponds to Scenario-II
        as under precipitation.
        """)

# Filter the selected district
district_geometry = districts_gdf[districts_gdf['NAME_STADT'] == selected_district].geometry.iloc[0]

# Ensure CRS consistency
if streets_gdf.crs != districts_gdf.crs:
    streets_gdf = streets_gdf.to_crs(districts_gdf.crs)

# Filter streets within the district
streets_in_district = streets_gdf[streets_gdf.intersects(district_geometry)]

# Define color mapping based on the selected theme
color_mappings = {
    "Viridis": {
        "Excellent": "#440154",
        "Good": "#3b528b",
        "Moderate": "#21908d",
        "Poor": "#5ec962",
        "Very Poor": "#fde725"
    },
    "YlGnBu": {
        "Excellent": "#081d58",
        "Good": "#225ea8",
        "Moderate": "#41b6c4",
        "Poor": "#7fcdbb",
        "Very Poor": "#ffffd9"
    },
    "Magma": {
        "Excellent": "#000004",
        "Good": "#3b0f70",
        "Moderate": "#8c2981",
        "Poor": "#de4968",
        "Very Poor": "#fcfdbf"
    },
    "Neptunes": {
        "Excellent": "#07592e",
        "Good": "#1e8b7a",
        "Moderate": "#23b190",
        "Poor": "#9fc5e8",
        "Very Poor": "#ffffd9"
    },
    "Hot-Cold": {
        "Excellent": "#436b88",
        "Good": "#b0dac2",
        "Moderate": "#e6cc84",
        "Poor": "#ee923c",
        "Very Poor": "#d13728"
    }
}

# Function to classify street based on the score
def classify_street(score):
    if score >= 60:
        return "Excellent"
    elif score >= 50:
        return "Good"
    elif score >= 25:
        return "Moderate"
    elif score >= 15:
        return "Poor"
    else:
        return "Very Poor"

# Create Folium map with a gray basemap (CartoDB Positron)
m = folium.Map(location=[district_geometry.centroid.y, district_geometry.centroid.x], zoom_start=14, tiles='CartoDB positron')

# Add districts to the map
folium.GeoJson(
    districts_gdf,
    name="Districts",
    style_function=lambda x: {'color': 'gray', 'weight': 0.5, 'fillOpacity': 0.1}
).add_to(m)

# Add streets to the map based on the selected sub-index
for _, row in streets_in_district.iterrows():
    # Get the selected sub-index score
    sub_index_score = row[selected_sub_index]

    # Prepare the popup text with all sub-index scores
    popup_text = f"<b>Street ID:</b> {row['Unique_ID']}<br>"
    for sub_index in sub_indices:
        score = row[sub_index]
        if sub_index == selected_sub_index:
            popup_text += f"<b style='color:red;'>{sub_index}:</b> {score}<br>"  # Highlight selected sub-index in red
        else:
            popup_text += f"<b>{sub_index}:</b> {score}<br>"

    # Classify street based on the selected sub-index score
    category = classify_street(sub_index_score)

    # Get the color for the current sub-index score based on the selected color theme
    if category == "Excellent":
        color = color_mappings[color_theme]["Excellent"]
    elif category == "Good":
        color = color_mappings[color_theme]["Good"]
    elif category == "Moderate":
        color = color_mappings[color_theme]["Moderate"]
    elif category == "Poor":
        color = color_mappings[color_theme]["Poor"]
    else:
        color = color_mappings[color_theme]["Very Poor"]

    # Add streets to the map with hover effect (adjust thickness on hover)
    folium.GeoJson(
        row.geometry,
        style_function=lambda x, color=color: {
            'color': color,
            'weight': 2,
            'opacity': 0.9
        },
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=f"{selected_sub_index}: {sub_index_score} | {category}",
        highlight_function=lambda x: {
            'color': 'red',
            'weight': 10,
            'opacity': 0.5
        }
    ).add_to(m)

# Add Fullscreen control
folium.plugins.Fullscreen(position="topleft").add_to(m)

# Display the map
folium_static(m, width=1300, height=600)

with st.expander("See explanation"):
    st.write('''
            The map above shows the selected sub-index scores for each street segment in the selected district. 
            Click on any street segment to see detailed information about all sub-index scores, with the selected sub-index score highlighted in red.
    ''')
