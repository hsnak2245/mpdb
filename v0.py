import streamlit as st
import pandas as pd

# Define dataset information with links and descriptions
datasets = {
    "MP_SED - A Microplastic Database for Sediments": {
        "file": "MP_SED_A_Microplastic_Database_for_SEDiments.csv",
        "description": (
            "A comprehensive database containing microplastic concentrations, sizes, shapes, and polymer data for sediments worldwide. "
            "Compiled from peer-reviewed literature, it serves as a valuable resource for understanding microplastic distribution in sediments. "
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
            "It aids in the identification and analysis of microplastic particles using Raman spectroscopy. "
        ),
        "url": "https://rochmanlab.wordpress.com/spectral-libraries-for-microplastics-research/"
    },
    "SLOPP-E": {
        "file": "sloppe.csv",
        "description": (
            "The SLOPPE (Spectral Library of Plastic Particles - Environmental) is an extension of SLOPP, including spectra from microplastics aged in environmental conditions. "
            "It enhances the accuracy of spectral matching for a broader range of microplastics. "
        ),
        "url": "https://rochmanlab.wordpress.com/spectral-libraries-for-microplastics-research/"
    }
}

def load_data(file):
    """Load a CSV file into a Pandas DataFrame."""
    try:
        return pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(file, encoding="latin1")

# Initialize session state variables
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = None
if 'show_column_selector' not in st.session_state:
    st.session_state.show_column_selector = False
if 'current_dataset' not in st.session_state:
    st.session_state.current_dataset = None

# Set Streamlit configuration
st.set_page_config(
    page_title="Micro Plastic Databases",
    page_icon="📊",
    layout="wide",
)

# Apply custom styles
st.markdown(
    """
    <style>
    body {
        font-family: 'Space Mono', monospace;
        background-color: #ffffff;
        color: #000000;
    }
    .css-1aumxhk {
        font-family: 'Space Mono', monospace;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App header
st.title("Micro Plastic Database Viewer")
st.markdown("Toggle across datasets to view data. You can navigate through 50 rows per page.")

# Sidebar for dataset selection
dataset_choice = st.sidebar.selectbox(
    "Select a dataset",
    options=list(datasets.keys()),
)

# Reset column selection when dataset changes
if st.session_state.current_dataset != dataset_choice:
    st.session_state.current_dataset = dataset_choice
    st.session_state.selected_columns = None
    st.session_state.show_column_selector = False

# Load selected dataset
st.header(f"{dataset_choice}")
st.markdown(datasets[dataset_choice]["description"])
st.markdown(f"Access the dataset here: [{dataset_choice}]({datasets[dataset_choice]['url']})")

# Display download button for the complete CSV
with open(datasets[dataset_choice]["file"], "rb") as f:
    st.download_button(
        label="Download the complete CSV",
        data=f,
        file_name=datasets[dataset_choice]["file"],
        mime="text/csv"
    )

try:
    df = load_data(datasets[dataset_choice]["file"])

    if df.empty:
        st.error("The dataset is empty.")
    else:
        # Column selection interface
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("Toggle Column Selector"):
                st.session_state.show_column_selector = not st.session_state.show_column_selector

        if st.session_state.show_column_selector:
            selected_cols = st.multiselect(
                "Select columns to display",
                options=df.columns.tolist(),
                default=st.session_state.selected_columns if st.session_state.selected_columns else df.columns.tolist()
            )
            if st.button("Apply Selection"):
                st.session_state.selected_columns = selected_cols
        
        # Use selected columns or all columns if none selected
        display_columns = st.session_state.selected_columns if st.session_state.selected_columns else df.columns.tolist()

        # Pagination
        page_size = 50
        num_pages = len(df) // page_size + (1 if len(df) % page_size > 0 else 0)
        page_number = st.sidebar.slider("Page", 1, num_pages, 1)

        # Calculate page indices
        start_idx = (page_number - 1) * page_size
        end_idx = min(page_number * page_size, len(df))

        # Display the data
        st.subheader(f"Showing Rows {start_idx + 1} to {end_idx} of {len(df)}")
        st.dataframe(df.iloc[start_idx:end_idx][display_columns], height=600)
        st.markdown(f"**Page {page_number} of {num_pages}**")

except Exception as e:
    st.error(f"Error loading data: {e}")