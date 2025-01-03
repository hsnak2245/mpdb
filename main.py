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
st.markdown("Toggle across datasets to view data. You can navigate through 25 rows per page.")

# Sidebar for dataset selection
dataset_choice = st.sidebar.selectbox(
    "Select a dataset",
    options=list(datasets.keys()),
)

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

    # Check if the data has been loaded properly
    if df.empty:
        st.error("The dataset is empty.")
    else:
        # Pagination
        page_size = 25
        num_pages = len(df) // page_size + (1 if len(df) % page_size > 0 else 0)

        # Display the page navigation
        page_number = st.sidebar.slider(
            "Page", 1, num_pages, 1
        )

        # Calculate the start and end row index for the current page
        start_idx = (page_number - 1) * page_size
        end_idx = min(page_number * page_size, len(df))

        # Display the data for the selected page with headers
        st.subheader(f"Showing Rows {start_idx + 1} to {end_idx} of {len(df)}")
        st.dataframe(df.iloc[start_idx:end_idx])  # This is where the table is displayed

        # Display the current page number and total pages
        st.markdown(f"**Page {page_number} of {num_pages}**")

except Exception as e:
    st.error(f"Error loading data: {e}")
