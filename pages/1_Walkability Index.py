import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import Fullscreen
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
from folium import IFrame

# LAYOUT -------------------------------------
st.set_page_config(page_title="Walkability Index", page_icon="🚶", initial_sidebar_state="auto", layout="wide")
st.markdown(
    "<h1>Walkability Index <b style='color:red;'> <span style='font-size:1.2em;'>| Münster</span></b></h1>", 
    unsafe_allow_html=True
)

# SIDEBAR AND MS LOGO -------------------------------------
# Create space and push the image to the bottom
st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)  # Adds spacing

# Add logo at the bottom
st.sidebar.image("Images/ms_logo.png", use_container_width=True)
st.sidebar.markdown("<p style='text-align:center; font-size:14px;'>© 2024 Walkability Index | Developed by Şafak Çöze</p>", unsafe_allow_html=True)

# RELATED DATASETS -------------------------------------
# Load GeoJSON files using GeoPandas
districts_gdf = gpd.read_file('Data/ms_districts_prj.geojson')
streets_gdf = gpd.read_file('Data/ms_streets_prj.geojson')

# Remove datetime columns if they exist
districts_gdf = districts_gdf.select_dtypes(exclude=['datetime'])

# Get the district names
district_names = districts_gdf['NAME_STADT'].unique()

# Place District, Scenario, and Color Theme selection next to each other
col1, col2, col3 = st.columns(3)

with col1:
    selected_district = st.selectbox("Select a District", district_names)

with col2:
    selected_scenario = st.selectbox("Select a Scenario", ["Scenario-I", "Scenario-II"])

with col3:
    color_theme = st.selectbox("Select a Color Theme", ["Viridis", "YlGnBu", "Magma", "Neptunes", "Hot-Cold"])

# Filter the selected district
district_geometry = districts_gdf[districts_gdf['NAME_STADT'] == selected_district].geometry.iloc[0]

# Ensure CRS consistency
if streets_gdf.crs != districts_gdf.crs:
    streets_gdf = streets_gdf.to_crs(districts_gdf.crs)

# Filter streets within the district
streets_in_district = streets_gdf[streets_gdf.intersects(district_geometry)]

# Define a function for street classification
def classify_street(score):
    if score >= 42:
        return "Excellent"
    elif score >= 29:
        return "Good"
    elif score >= 21:
        return "Moderate"
    elif score >= 14:
        return "Poor"
    else:
        return "Very Poor"

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

# Create Folium map with a gray basemap (CartoDB Positron)
m = folium.Map(location=[district_geometry.centroid.y, district_geometry.centroid.x], zoom_start=14, tiles='CartoDB positron')

# Add districts to the map
folium.GeoJson(
    districts_gdf,
    name="Districts",
    style_function=lambda x: {'color': 'gray', 'weight': 0.5, 'fillOpacity': 0.1}
).add_to(m)

# Function to style streets based on classification
def style_function(feature):
    score_field = 'Walkability Score - August'  # Default score field

    # Check the selected scenario and use the appropriate score
    if selected_scenario == "Scenario-II":
        score_field = 'Walkability Score - October'
    
    score = feature['properties'].get(score_field, 0)  # Default to 0 if not found
    category = classify_street(score)

    return {
        'color': color_mappings[color_theme].get(category, "gray"),
        'weight': 2,
        'opacity': 0.9
    }

# Add streets to the map 
for _, row in streets_in_district.iterrows():
    score_field = 'Walkability Score - August' if selected_scenario == "Scenario-I" else 'Walkability Score - October'
    score = row[score_field]
    category = classify_street(score)

    popup_text = f"""
    <b>Street ID:</b> {row['Unique_ID']}<br>
    <b>Scenario:</b> {selected_scenario}<br>
    <b>Walkability Score:</b> {score}<br>
    <b>Category:</b> <span style="color:{color_mappings[color_theme][category]};"><b>{category}</b></span>
    """

    # Add streets to the map with hover effect 
    geo_json = folium.GeoJson(
        row.geometry,
        style_function=lambda x, cat=category: {
            'color': color_mappings[color_theme].get(cat, "gray"),
            'weight': 2,
            'opacity': 0.9
        },
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=f"Score: {score} | {category}",
        highlight_function=lambda x: {
            'color': 'red',
            'weight': 10,
            'opacity': 0.5
        }
    )

    geo_json.add_to(m)

# Add Fullscreen control
Fullscreen(position="topleft").add_to(m)

# Display the map
folium_static(m, width=1300, height=600)

with st.expander("See explanation"):
    st.write('''
            The map above changes according to the selected "district" and "scenario",
            and the score and walkability assessment can be reached via the tooltip
            by hovering over. For more detailed information, click on the relevant 
            street segment and get information via the pop-up.
    ''')

st.divider()

# STREET SEGMENTS AND RADAR CHART ------------------------------

st.markdown(
    "<h2> <b style='color:red;'> <span style='font-size:1.2em;'>| Street Segments</span></b></h2>", 
    unsafe_allow_html=True
)

# Ensure 'Unique_ID' is treated as a string
streets_gdf['Unique_ID'] = streets_gdf['Unique_ID'].astype(str)

# Search box for Street ID
selected_street_id = st.text_input("Enter Street ID (Unique_ID):", "")

# If a Street ID is entered, proceed with visualization
if selected_street_id:
    # Filter the selected street segment
    street_data = streets_gdf[streets_gdf['Unique_ID'] == selected_street_id]

    if not street_data.empty:
        # Extract sub-index scores
        sub_index_scores = {
            "Proximity": street_data.iloc[0].get("Proximity Score", 0),
            "Landscape": street_data.iloc[0].get("Landscape and Nature Score", 0),
            "Infrastructure": street_data.iloc[0].get("Pedestrian Infrastructure Score", 0),
            "Comfort": street_data.iloc[0].get("Pedestrian Comfort Score", 0),
            "Thermal Comfort-I": street_data.iloc[0].get("Outdoor Thermal Comfort - August", 0),
            "Thermal Comfort-II": street_data.iloc[0].get("Outdoor Thermal Comfort - October", 0)
        }

        # Extract district name
        district_name = street_data.iloc[0]["District"]

        # Extract total Walkability Index scores for both scenarios
        scenario_1_score = street_data.iloc[0].get("Walkability Score - August", "N/A")
        scenario_2_score = street_data.iloc[0].get("Walkability Score - October", "N/A")

        # Create a two-column layout 
        col1, col2 = st.columns([2, 1]) 

        with col1:
            # Display radar chart
            st.subheader(f"Radar Chart")
            categories = list(sub_index_scores.keys())
            values = list(sub_index_scores.values())

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]], 
                theta=categories + [categories[0]],
                fill='toself',
                name="Walkability Scores"
            ))
            fig.update_layout(
                width=800,  
                height=600,  
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                title=f"Radar Chart of Walkability Scores for the Selected Street ID"
            )
            st.plotly_chart(fig, use_container_width=False)  

        with col2:
            # Display Scenario Scores
            st.markdown("### Scenario-Based Walkability Scores") 

            st.markdown(f"""
                <div style="padding: 15px; border-radius: 10px;">
                    <p><b style="color:#E63946;">Scenario-I (August):</b> {scenario_1_score}</p>
                    <p><b style="color:#1D3557;">Scenario-II (October):</b> {scenario_2_score}</p>
                </div>
            """, unsafe_allow_html=True)

          # Sub-Indexes Title
            st.markdown("### Walkability Sub-Indexes Scores")

            # Display all sub-index scores
            st.markdown(f"🏢 **Proximity:** {sub_index_scores['Proximity']}", unsafe_allow_html=True)
            st.markdown(f"🌳 **Landscape & Nature:** {sub_index_scores['Landscape']}", unsafe_allow_html=True)
            st.markdown(f"🚏 **Pedestrian Infrastructure:** {sub_index_scores['Infrastructure']}", unsafe_allow_html=True)
            st.markdown(f"🚶‍♂️ **Comfort:** {sub_index_scores['Comfort']}", unsafe_allow_html=True)
            st.markdown(f"☀️ **Thermal Comfort (August):** {sub_index_scores['Thermal Comfort-I']}", unsafe_allow_html=True)
            st.markdown(f"🌧 **Thermal Comfort (October):** {sub_index_scores['Thermal Comfort-II']}", unsafe_allow_html=True)            

        # Find the strongest and weakest sub-index
        strongest_sub_index = max(sub_index_scores, key=sub_index_scores.get)
        weakest_sub_index = min(sub_index_scores, key=sub_index_scores.get)

        # Summary below both columns (Full Width)
        summary_text = f"""
        The strongest sub-index for this street segment is <b style='color:green;'>{strongest_sub_index}</b> 
        with a score of <b>{sub_index_scores[strongest_sub_index]}</b>, indicating its strength in this area. 
        However, the weakest sub-index is <b style='color:red;'>{weakest_sub_index}</b> 
        with a score of <b>{sub_index_scores[weakest_sub_index]}</b>, suggesting potential areas for improvement.
        """
        st.markdown(summary_text, unsafe_allow_html=True)

    else:
        st.warning("Street ID not found! Please enter a valid ID.")

with st.expander("See explanation"):
    st.write('''
            The relevant radar chart above provides detailed information
            about the walkability scores ​and especially the sub-indexes
            of the street whose Street ID is entered. The "r" value on the
            radar chart gives the walkability score of the relevant sub-index.
    ''')