import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# LAYOUT -------------------------------------
st.set_page_config(page_title="Home", initial_sidebar_state="auto", layout="wide")

st.markdown(
    "<h1>Pedestrian-Friendly City |<span style='font-size:1.2em;'> 2024</span></b><b style='color:red;'> <span style='font-size:1.2em;'>| Münster</span></b></h1>", 
    unsafe_allow_html=True
)

# SIDEBAR NAVIGATION -------------------------------------
# Create space and push the image to the bottom
st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

# Add logo at the bottom
st.sidebar.image("Images/ms_logo.png", use_container_width=True)
st.sidebar.markdown("<p style='text-align:center; font-size:14px;'>© 2024 Walkability Index | Developed by Şafak Çöze</p>", unsafe_allow_html=True)

st.divider()

# First part, walkability and pie chart --------------------------------------
# Load the CSV file
transport_data = pd.read_csv("Data/ms_transportation.csv")

# Create two columns
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("<h4>What is Walkability?</h4>", unsafe_allow_html=True)
    
    # Bullet points for walkability
    st.write("""
    **Walkability** refers to how pedestrian-friendly an area is, making it easy, accessible, and enjoyable to walk. And, walking is the most essential mode of transportation for people in urban areas. Whether they are visitors or residents, individuals using various transportation modes—motorized or non-motorized—must walk at some point during their journeys.
             
    - **Access to Amenities**: Proximity to parks, stores, public transport, and other essential services encourages walking.
    - **Landscape**: Aesthetic elements like greenery, open spaces, and natural features make walking more enjoyable.
    - **Pedestrian Comfort**: Comfortable walking environments are free from obstacles, have well-maintained paths, and provide places for rest.
    - **Pedestrian Infrastructure**: Includes sidewalks, pedestrian crossings, and pathways that support safe walking.
    - **Community Interaction**: Walkable areas foster social engagement and interaction among residents and visitors.
    - **Urban Planning**: Walkability is a key factor in designing cities that prioritize people and improve the quality of life.
    """)

    st.divider()

    st.markdown('<h3 style="color:black;">Interactive Map <span style="color:red; font-size:1.2em;"><b>| 2024</b></span>', unsafe_allow_html=True)

    st.page_link("pages/1_Walkability Index.py", label="Scenario-Based Walkability Scores | Explore How Walkable Münster is!")
    st.page_link("pages/2_Sub-Indexes.py", label="Walkability Scores and Sub-Indexes")

with col2:
    st.markdown("<h4>How Walkable is Münster by Districts?</h4>", unsafe_allow_html=True)
    
    # District Select Box
    districts = transport_data.columns[1:]  
    selected_district = st.selectbox("Select a district to explore its walkability based on the data from Stadt-Münster", districts)

    # Filter the data for the selected district
    district_data = transport_data[['Means of Transport', selected_district]]

    # Set the data for the selected district
    transport_data_filtered = district_data.set_index('Means of Transport').squeeze()

    # Get the colors from the 'Inferno' color scale
    inferno_colors = px.colors.sequential.Inferno

    # Pie Chart
    fig_pie = go.Figure([go.Pie(
        labels=transport_data_filtered.index,
        values=transport_data_filtered.values,
        hole=0.4,
        marker=dict(colors=inferno_colors[:len(transport_data_filtered)]), 
        hoverinfo='label'
    )])

    fig_pie.update_layout(
        title=f"Choice of Transport by {selected_district}",
        title_x=0,  # Set to 0 for left alignment
        title_xanchor='left',  # Align the title to the left
        height=550,  
        width=800,  
    )

    st.plotly_chart(fig_pie)
    
    # Brief intro about "On Foot"
    on_foot_percentage = transport_data_filtered.get("On Foot", 0)
    st.markdown(f"**On Foot**: In the {selected_district}, {on_foot_percentage}% of people prefer walking as their main mode of transport.")

    with st.expander("See explanation"):
        st.write('''
                To exclude specific transportation modes and view the updated percentage 
                by district and for Münster City, use the legend.
        ''')


st.divider()

# Second part, SCENARIO EXPLANATION --------------------------------------
st.markdown("<h4> Composite Walkability Index </h4>", unsafe_allow_html=True)
st.markdown('''The primary goal of this project is to develop a composite walkability index 
            that incorporates **thermal comfort**, allowing both citizens and decision-makers in 
            Münster to evaluate pedestrian environments during extreme heat and precipitation conditions.
            The composite walkability index incorporates several sub-indexes: **proximity**, **landscape and nature**, 
            **pedestrian comfort**, **pedestrian infrastructure**, and **outdoor thermal comfort**. The outdoor thermal 
            comfort sub-index is made up of **air temperature**, **relative humidity**, **wind speed**, **precipitation**, 
            and the **presence of trees**.''')

# Create two columns
col3, col4 = st.columns(2, gap="large")

with col3:
    st.divider()
    st.markdown("<h5>Scenario-I: <span style='color:red;'>Heat</span> ☀️</h5>", unsafe_allow_html=True)
    st.markdown(
        """
        *Scenario-I*: **Heat** refers to modeling and analyzing the impact of extreme heat conditions on walkability in urban environments. The goal is to provide decision-makers with insights into the heat-related challenges that pedestrians face and offer 
        solutions for improving the walkability and thermal comfort of the city under extreme heat conditions.
        """)
    st.divider()

with col4:
    st.divider()
    st.markdown("<h5>Scenario-II: <span style='color:blue;'>Precipitation</span> 🌧️</h5>", unsafe_allow_html=True)
    st.markdown(
        """
        *Scenario-II*: **Precipitation** focuses on modeling and analyzing the effects of heavy rainfall and wet conditions on walkability in urban areas. 
        Precipitation can affect pedestrian comfort and safety by making walking surfaces slippery, increasing the risk of accidents, and reducing overall 
        walkability.
        """)

# OPEN DATA ---------------------------------------
st.markdown("<h5> Open Data Portals </h5>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Create two columns
col5, col6 = st.columns(2, gap="large")

with col5:
    st.image("Images/osm_logo.svg", width=150, use_container_width=False)
    st.markdown("""
    **OSMnx** is a Python package that allows for the easy downloading, modeling, analyzing, and visualizing 
    of street networks and geospatial features from **OpenStreetMap**. In this project, OSMnx is used to model 
    walkability in Münster by downloading and analyzing pedestrian networks, amenities, and other relevant infrastructure.
    """)

with col6:
    st.image("Images/ms_logo.png", width=350, use_container_width=False)
    st.markdown("""
    **Stadt Münster** refers to the city of Münster open data portal. In this project, 
    Münster serves as the case study for analyzing and improving walkability. The project 
    includes open data from the Stadt-Münster, such as land-use diversity, public and commercial amenities,
    urban furniture, landmarks, and presence of trees
    """)

# Create two columns
col7, col8 = st.columns(2, gap="large")

with col7:
    st.image("Images/dwd_logo.png", width=350, use_container_width=False)
    st.markdown("""
    **DWD Weather Station** refers to the Deutscher Wetterdienst (DWD), Germany's national meteorological service. 
    The DWD weather stations provide valuable data on various climatic factors such as air temperature, humidity, 
    wind speed, and precipitation. In this project, data from DWD weather stations is used to assess outdoor 
    thermal comfort and its impact on walkability in Münster.
    """)

with col8:
    st.image("Images/opentopo_logo.png", width=250, use_container_width=False)
    st.markdown("""
    **OpenTopography** is an open-access platform providing high-resolution topographic data. In this project, 
    OpenTopography is utilized to access, integrate, and analyze topographic data for Münster, including slope analysis 
    derived from **Copernicus GLO-30 Digital Elevation Model**. This data helps assess the impact of terrain on 
    pedestrian comfort and walkability.
    """)
