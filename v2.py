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
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with dark theme
st.markdown("""
    <style>
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
    }
    
    .stApp {
        background-color: #000000;
    }
    
    .main {
        background-color: #000000;
    }
    
    .metric-container {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 4px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #ffffff;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #b3b3b3;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .dataset-card {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 4px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .dataset-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #ffffff;
    }
    
    .stButton>button {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #404040;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: #404040;
        border-color: #4d4d4d;
    }
    
    .stSelectbox > div > div {
        font-family: inherit;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
    }
    
    .stMarkdown a {
        color: #00b4d8;
        text-decoration: none;
    }
    
    .stMarkdown a:hover {
        color: #48cae4;
        text-decoration: underline;
    }
    
    .stSidebar {
        background-color: #1a1a1a;
    }
    
    .stSidebar .stMarkdown {
        font-family: inherit;
        color: #ffffff;
    }
    
    p {
        color: #e6e6e6;
        line-height: 1.6;
    }

    /* Data table styling */
    .dataframe {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }

    .dataframe th {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
    }

    .dataframe td {
        background-color: #1a1a1a !important;
        color: #e6e6e6 !important;
    }

    /* Radio button and checkbox styling */
    .stRadio > label, .stCheckbox > label {
        color: #ffffff !important;
    }

    

    /* Text input styling */
    .stTextInput > div > div > input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border-color: #333333 !important;
    }

    /* Select box styling */
    .stSelectbox > div > div {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border-color: #333333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.title("Navigation")
    page = st.radio("", ["Home", "Data Explorer", "Search by Polymer", "About"], key="navigation")
    st.session_state.current_page = page.lower()


# Home Page
if st.session_state.current_page == "home":
    st.title("Micro Plastic Database Explorer")
    st.markdown("### A Comprehensive Collection of Microplastic Research Data")
    
    # Metrics
    total_records = sum(len(load_data(d["file"])) for d in datasets.values())
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">{:,}</div>
                <div class="metric-label">Total Records</div>
            </div>
        """.format(total_records), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">{}</div>
                <div class="metric-label">Available Databases</div>
            </div>
        """.format(len(datasets)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">{}</div>
                <div class="metric-label">Last Updated</div>
            </div>
        """.format(datetime.now().strftime("%Y-%m-%d")), unsafe_allow_html=True)

    # Available Databases
    st.markdown("## Integrated Databases")
    
    for name, info in datasets.items():
        st.markdown(f"""
            <div class="dataset-card">
                <div class="dataset-title">{name}</div>
                <p>{info['description']}</p>
                <a href="{info['url']}" target="_blank">Access Source →</a>
            </div>
        """, unsafe_allow_html=True)
    
    # External Databases Section
    st.markdown("## Other Databases")
    st.markdown("These databases are available through external platforms. Click the links to access their respective portals.")
    
    for name, info in external_databases.items():
        st.markdown(f"""
            <div class="dataset-card">
                <div class="dataset-title">{name}</div>
                <p>{info['description']}</p>
                <a href="{info['url']}" target="_blank">Access Database →</a>
            </div>
        """, unsafe_allow_html=True)

# Data Explorer Page
elif st.session_state.current_page == "data explorer":
    st.title("Data Explorer")
    
    dataset_choice = st.selectbox(
        "Select a database",
        options=list(datasets.keys()),
    )
    
    # Reset selected columns if a new dataset is selected
    if 'current_dataset' in st.session_state and st.session_state.current_dataset != dataset_choice:
        st.session_state.selected_columns = None  # Reset selected columns when switching datasets

    # Update the current dataset in session state
    st.session_state.current_dataset = dataset_choice
    
    try:
        df = load_data(datasets[dataset_choice]["file"])
        
        # Reset column selector if necessary
        if 'selected_columns' in st.session_state and st.session_state.selected_columns is None:
            st.session_state.selected_columns = df.columns.tolist()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {dataset_choice}")
            st.markdown(datasets[dataset_choice]["description"])
        with col2:
            with open(datasets[dataset_choice]["file"], "rb") as f:
                st.download_button(
                    label="Download CSV",
                    data=f,
                    file_name=datasets[dataset_choice]["file"],
                    mime="text/csv"
                )
        
        if st.button("Toggle Column Selector"):
            st.session_state.show_column_selector = not st.session_state.show_column_selector
            
        if st.session_state.show_column_selector:
            selected_cols = st.multiselect(
                "Select columns to display",
                options=df.columns.tolist(),
                default=st.session_state.selected_columns if st.session_state.selected_columns else df.columns.tolist()
            )
            st.session_state.selected_columns = selected_cols
        
        display_cols = st.session_state.selected_columns if st.session_state.selected_columns else df.columns.tolist()
        
        # Pagination
        rows_per_page = 50
        total_pages = len(df) // rows_per_page + (1 if len(df) % rows_per_page > 0 else 0)
        page = st.slider("Page", 1, total_pages, 1)
        
        start_idx = (page - 1) * rows_per_page
        end_idx = min(start_idx + rows_per_page, len(df))
        
        st.markdown(f"Showing rows {start_idx + 1} to {end_idx} of {len(df)}")
        st.dataframe(df.iloc[start_idx:end_idx][display_cols], height=500)
        
    except Exception as e:
        st.error(f"Error loading data: {e}")


elif st.session_state.current_page == "search by polymer":  # Changed to lowercase to match navigation
    st.title("Polymer Search and Analysis")
    
    # Initialize session state
    if 'polymer_list' not in st.session_state:
        st.session_state.polymer_list = {}
    if 'selected_polymer' not in st.session_state:
        st.session_state.selected_polymer = None
    if 'current_dataset' not in st.session_state:
        st.session_state.current_dataset = None

    # Dataset selection
    dataset_choice = st.selectbox(
        "Select a database",
        options=list(datasets.keys()),
        key="polymer_dataset_selector"
    )

    try:
        # Load the selected dataset
        df = load_data(datasets[dataset_choice]["file"])
        
        # Determine the polymer column based on the dataset
        polymer_column = 'Polymers' if 'Polymers' in df.columns else 'Polymer'
        
        if polymer_column in df.columns:
            # Extract unique polymers and their counts
            polymers_series = df[polymer_column].dropna().str.split(',').explode().str.strip()
            polymer_counts = polymers_series.value_counts()
            
            # Display polymer distribution
            # st.subheader("Polymer Distribution")
            # st.dataframe(polymer_counts, height=200)
            
            # Polymer selection
            selected_polymer = st.selectbox(
                "Select a Polymer for Detailed Analysis",
                options=[''] + list(polymer_counts.index),
                key="polymer_selector"
            )
            
            if selected_polymer:
                # Filter data for selected polymer
                filtered_data = df[df[polymer_column].str.contains(selected_polymer, na=False)]
                
                # Display statistics
                st.markdown(f"Total occurrences: **{polymer_counts[selected_polymer]}** (**{(polymer_counts[selected_polymer] / polymer_counts.sum() * 100):.2f}%**)")
                
                
                # Display filtered data
                st.subheader("Filtered Data")
                st.dataframe(filtered_data, height=400)
                
                # Add download button for filtered data
                csv = filtered_data.to_csv(index=False)
                st.download_button(
                    label="Download Filtered Data",
                    data=csv,
                    file_name=f"{selected_polymer}_data.csv",
                    mime="text/csv"
                )
        else:
            st.error(f"No polymer column found in the selected dataset. Expected column name: {polymer_column}")
            
    except Exception as e:
        st.error(f"Error processing data: {e}")

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
    

