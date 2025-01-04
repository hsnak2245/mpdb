import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = None
if 'show_column_selector' not in st.session_state:
    st.session_state.show_column_selector = False
if 'current_dataset' not in st.session_state:
    st.session_state.current_dataset = None
if 'theme' not in st.session_state:
    st.session_state.theme = None

# Dataset information
datasets = {
    "MP_SED - A Microplastic Database for Sediments": {
        "file": "MP_SED_A_Microplastic_Database_for_SEDiments.csv",
        "description": (
            "A comprehensive database containing microplastic concentrations, sizes, shapes, and polymer data for sediments worldwide. "
            "Compiled from peer-reviewed literature, it serves as a valuable resource for understanding microplastic distribution in sediments."
        ),
        "url": "https://doer.el.erdc.dren.mil/microplasticdatabase.html"
    },
    "NOAA NCEI Marine Microplastics Database": {
        "file": "NOAA_NCEI_Marine_Microplastics_Database.csv",
        "description": (
            "A global dataset detailing the occurrence, distribution, and quantity of microplastics in marine environments. "
            "It includes data in CSV, JSON, and GeoJSON formats, accompanied by a GIS-based map for visualization."
        ),
        "url": "https://www.ncei.noaa.gov/products/microplastics"
    },
    "SLOPP": {
        "file": "slopp.csv",
        "description": (
            "The SLOPP (Spectral Library of Plastic Particles) is a collection of Raman spectra representing various microplastics found in environmental samples. "
            "It aids in the identification and analysis of microplastic particles using Raman spectroscopy."
        ),
        "url": "https://rochmanlab.wordpress.com/spectral-libraries-for-microplastics-research/"
    },
    "SLOPP-E": {
        "file": "sloppe.csv",
        "description": (
            "The SLOPPE (Spectral Library of Plastic Particles - Environmental) is an extension of SLOPP, including spectra from microplastics aged in environmental conditions. "
            "It enhances the accuracy of spectral matching for a broader range of microplastics."
        ),
        "url": "https://rochmanlab.wordpress.com/spectral-libraries-for-microplastics-research/"
    }
}

# External databases information
external_databases = {
    "FLOPP and FLOPP-E: ATR-FTIR Spectral Libraries": {
        "description": (
            "Comprehensive spectral libraries for microplastics analysis using ATR-FTIR. FLOPP contains 186 spectra and FLOPP-E contains 195 spectra "
            "from environmentally aged samples, providing valuable reference data for plastic particle identification."
        ),
        "url": "https://rochmanlab.wordpress.com/spectral-libraries-for-microplastics-research/"
    },
    "LITTERBASE": {
        "description": (
            "A GIS-based platform providing global data on marine litter distribution, including detailed information for Qatar. "
            "Offers comprehensive visualization of marine litter distribution and composition."
        ),
        "url": "https://litterbase.awi.de/litter"
    },
    "Adventure Scientists Freshwater Microplastics": {
        "description": (
            "A citizen science initiative collecting data on microplastic pollution in freshwater systems worldwide. "
            "Provides detailed information sheets and datasets from various sampling locations."
        ),
        "url": "https://www.adventurescientists.org/access-datasets.html"
    },
    "SCCWRP Microplastic Dataset": {
        "description": (
            "Southern California Coastal Water Research Project's comprehensive dataset on microplastic pollution, "
            "focusing on coastal waters and providing detailed analytical methods and results."
        ),
        "url": "https://microplastics.sccwrp.org/"
    },
    "One Earth One Ocean Microplastic Pollution Map": {
        "description": (
            "An interactive global mapping platform showing microplastic pollution distribution and concentration levels "
            "across different marine environments worldwide."
        ),
        "url": "https://grad.oeoo.world/"
    }
}

def load_data(file):
    """Load a CSV file into a Pandas DataFrame."""
    try:
        return pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(file, encoding="latin1")

# Set page config
st.set_page_config(
    page_title="Micro Plastic Database Viewer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define custom CSS
st.write("""
<style>
/* Base styles */
* {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
}

/* Dark theme styles */
.stApp.dark {
    background-color: #222;
    color: #fff;
}

.stApp.dark .main {
    background-color: #222;
}

/* Light theme styles (optional) */
.stApp.light {
    background-color: #fff;
    color: #000;
}

.stApp.light .main {
    background-color: #f0f0f0;
}

/* Other common styles (adjust as needed) */
.metric-container {
    background-color: rgba(255, 255, 255, 0.1); /* Adjust background color for dark/light theme */
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    padding: 1rem;
    margin: 0.5rem 0;
}

/* ... other styles ... */

</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.title("Navigation")
    page = st.radio("", ["Home", "Data Explorer", "About"], key="navigation")
    st.session_state.current_page = page.lower()

    st.title("Theme")
    theme_choice = st.radio("", ["Light", "Dark", "System"], key="theme_choice")
    if theme_choice == "Light":
        st.session_state.theme = "light"
    elif theme_choice == "Dark":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = None

# Apply theme class
if st.session_state.theme:
    st.write(f'<div class="stApp {st.session_state.theme}">', unsafe_allow_html=True)

# Home Page
if st.session_state.current_page == "home":
    st.title("Micro Plastic Database Explorer")
    st.markdown("### A Comprehensive Collection of Microplastic Research Data")

    # ... (rest of your Home Page content) ...

# Data Explorer Page
elif st.session_state.current_page == "data explorer":
    st.title("Data Explorer")

    # ... (rest of your Data Explorer content) ...

# About Page
elif st.session_state.current_page == "about":
    st.title("About")
    st.markdown("""
    ## About the Database Viewer
    
    This platform aggregates multiple microplastic databases into a single, accessible interface. 
    ### Data Sources
    - Environmental Laboratory of the U.S. Army Engineer Research and Development Center
    - NOAA National Centers for Environmental Information
    - Rochman Laboratory at the University of Toronto
    """)

# Close theme class if applied
if st.session_state.theme:
    st.write("</div>", unsafe_allow_html=True)