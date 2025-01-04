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
    st.session_state.theme = 'dark'

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


def get_theme_css(theme):
    """Return CSS based on selected theme."""
    if theme == 'light':
        return """<style>
    /* Base Theme Colors */
    .stApp, .main {
        background-color: #f8fafc; /* Light background */
        color: #1e293b; /* Dark text */
    }

    /* Text Styling */
    .stApp div, .main div, .stMarkdown p {
        color: #475569; /* Subtle dark text for regular paragraphs */
        line-height: 1.7; /* Increased line-height for readability */
    }

    /* Headings Styling */
    h1, h2, h3, h4, h5, h6, .dataset-title {
        color: #1e293b; /* Dark color for headings */
        font-weight: 600; /* Bold headings */
    }

    /* Markdown Text */
    .stMarkdown a {
        color: #0284c7; /* Primary link color */
        text-decoration: none;
        transition: color 0.2s ease;
    }
    .stMarkdown a:hover {
        color: #0369a1; /* Darker color for link hover */
    }

    /* Sidebar and Button Styling */
    .stSidebar {
        background-color: #ffffff; /* Sidebar background */
        border-right: 1px solid #e2e8f0; /* Subtle border for separation */
        box-shadow: 2px 0 4px rgba(0, 0, 0, 0.05); /* Light shadow for depth */
    }
    .stButton > button {
        background-color: #ffffff;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        padding: 0.625rem 1.25rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .stButton > button:hover {
        background-color: #f1f5f9; /* Lighter background on hover */
        border-color: #cbd5e1;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    }

    /* Metric Containers and Dataset Cards */
    .metric-container, .dataset-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-container:hover, .dataset-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.1), 0 4px 6px -1px rgba(0, 0, 0, 0.06);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }

    /* Table Styling */
    .dataframe {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }
    .dataframe th {
        background-color: #f8fafc !important;
        color: #1e293b !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #e2e8f0 !important;
        padding: 12px 16px !important;
    }
    .dataframe td {
        background-color: #ffffff !important;
        color: #475569 !important;
        border-bottom: 1px solid #e2e8f0 !important;
        padding: 12px 16px !important;
    }

    /* Form Elements */
    .stRadio > label, .stCheckbox > label {
        color: #1e293b !important;
        font-weight: 500 !important;
    }
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
    }
    .stSlider > div > div > div > div,
    .stSlider > div > div > div > div > div {
        background-color: #0284c7 !important;
    }

    /* Typography */
    p, .stMarkdown p {
        color: #475569;
        line-height: 1.7;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b;
        font-weight: 600;
    }

</style>

        """
    elif theme == 'dark':
        # [Keep the existing dark theme CSS]
        return """
        <style>
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
        
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff;
        }
        
        p {
            color: #e6e6e6;
        }
        
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
        
        .stSidebar {
            background-color: #1a1a1a;
        }
        
        .stSidebar .stMarkdown {
            color: #ffffff;
        }
        </style>
        """
    else:  # system theme
        # [Keep the existing system theme CSS]
        return """
        <style>
        @media (prefers-color-scheme: dark) {
            /* Dark mode styles */
            .stApp { background-color: #000000; }
            .main { background-color: #000000; }
            /* [Include all dark theme styles] */
        }
        
        @media (prefers-color-scheme: light) {
            /* Light mode styles */
            .stApp { background-color: #ffffff; }
            .main { background-color: #ffffff; }
            /* [Include all light theme styles] */
        }
        </style>
        """

# Set page config
st.set_page_config(
    page_title="Micro Plastic Database Viewer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation and theme selector
with st.sidebar:
    st.title("Navigation")
    page = st.radio("", ["Home", "Data Explorer", "About"], key="navigation")
    st.session_state.current_page = page.lower()
    
    # Theme selector
    st.markdown("### Theme Settings")
    theme = st.selectbox(
        "Select Theme",
        options=['dark', 'light', 'system'],
        index=['dark', 'light', 'system'].index(st.session_state.theme),
        key="theme_selector"
    )
    st.session_state.theme = theme

# Apply theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)


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
