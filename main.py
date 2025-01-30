import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
from scipy.signal import find_peaks
import plotly.graph_objects as go
from typing import Dict, Optional
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state with type hints
if 'current_page' not in st.session_state:
    st.session_state.current_page: str = 'home'
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns: Optional[list] = None
if 'show_column_selector' not in st.session_state:
    st.session_state.show_column_selector: bool = False
if 'current_dataset' not in st.session_state:
    st.session_state.current_dataset: Optional[str] = None
if 'processed_ftir_files' not in st.session_state:
    st.session_state.processed_ftir_files: Dict = {}
if 'polymer_list' not in st.session_state:
    st.session_state.polymer_list: Dict = {}
if 'selected_polymer' not in st.session_state:
    st.session_state.selected_polymer: Optional[str] = None

# Dataset information with type hints
datasets: Dict[str, Dict[str, str]] = {
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

external_databases: Dict[str, Dict[str, str]] = {
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

class DataLoader:
    """Handles data loading operations with error handling."""
    
    @staticmethod
    def load_data(file: str) -> pd.DataFrame:
        """
        Load a CSV file into a Pandas DataFrame with proper error handling.
        
        Args:
            file (str): Path to the CSV file
            
        Returns:
            pd.DataFrame: Loaded dataframe
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            pd.errors.EmptyDataError: If the file is empty
        """
        try:
            if not os.path.exists(file):
                raise FileNotFoundError(f"File not found: {file}")
                
            try:
                df = pd.read_csv(file, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(file, encoding="latin1")
                
            if df.empty:
                raise pd.errors.EmptyDataError(f"Empty CSV file: {file}")
                
            return df
            
        except Exception as e:
            logger.error(f"Error loading {file}: {str(e)}")
            raise

class FTIRProcessor:
    """Handles FTIR spectrum processing and analysis."""
    
    @staticmethod
    def process_ftir_file(file) -> pd.DataFrame:
        """
        Process FTIR file data.
        
        Args:
            file: File object containing FTIR data
            
        Returns:
            pd.DataFrame: Processed FTIR data
            
        Raises:
            ValueError: If file format is invalid
        """
        try:
            df = pd.read_csv(file)
            if len(df.columns) != 2:
                raise ValueError("CSV must have exactly 2 columns: wavenumber and transmittance")
            
            df.columns = ['cm-1', 'transmittance']
            df['absorbance'] = np.log10(100/df['transmittance'])
            return df
            
        except Exception as e:
            logger.error(f"Error processing FTIR file: {str(e)}")
            raise ValueError(f"Error processing file: {str(e)}")

    @staticmethod
    def find_peaks_in_spectrum(df: pd.DataFrame) -> pd.DataFrame:
        """
        Find significant peaks in FTIR spectrum.
        
        Args:
            df (pd.DataFrame): Processed FTIR data
            
        Returns:
            pd.DataFrame: Peak information
        """
        peaks, properties = find_peaks(-df['absorbance'],
                                     prominence=0.01,
                                     width=2,
                                     distance=20)
        
        sorted_indices = np.argsort(properties['prominences'])[::-1]
        significant_peaks = df['cm-1'].iloc[peaks].values[sorted_indices][:10]
        prominence_values = properties['prominences'][sorted_indices][:10]
        peak_heights = df['transmittance'].iloc[peaks].values[sorted_indices][:10]
        
        return pd.DataFrame({
            'Wavenumber': significant_peaks,
            'Prominence': prominence_values,
            'Transmittance': peak_heights
        })

def create_plotly_spectrum(df: pd.DataFrame, 
                          peaks: Optional[pd.DataFrame] = None, 
                          title: str = "FTIR Spectrum") -> go.Figure:
    """
    Create a Plotly figure for FTIR spectrum visualization.
    
    Args:
        df (pd.DataFrame): FTIR data
        peaks (Optional[pd.DataFrame]): Peak data
        title (str): Plot title
        
    Returns:
        go.Figure: Plotly figure object
    """
    fig = go.Figure()
    
    # Add main spectrum
    fig.add_trace(go.Scatter(
        x=df['cm-1'],
        y=df['transmittance'],
        name='Spectrum',
        line=dict(color='#2c7bb6', width=2)
    ))
    
    # Add peaks if available
    if peaks is not None:
        fig.add_trace(go.Scatter(
            x=peaks['Wavenumber'],
            y=peaks['Transmittance'],
            mode='markers',
            name='Peaks',
            marker=dict(size=8, color='red')
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Wavenumber (cm⁻¹)',
        yaxis_title='% Transmittance',
        template='plotly_white',
        showlegend=True,
        xaxis={'autorange': 'reversed'}
    )
    
    return fig

def main():
    """Main application entry point."""
    
    # Set page config
    st.set_page_config(
        page_title="Micro Plastic Database Viewer",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Load CSS
    try:
        with open('styles.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        logger.warning("styles.css not found")

    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("", ["Home", "Data Explorer", "Search by Polymer", "FTIR Viewer", "About"])
        st.session_state.current_page = page.lower()

    # Page routing
    if st.session_state.current_page == "home":
        render_home_page()
    elif st.session_state.current_page == "data explorer":
        render_data_explorer()
    elif st.session_state.current_page == "search by polymer":
        render_polymer_search()
    elif st.session_state.current_page == "ftir viewer":
        render_ftir_viewer()
    elif st.session_state.current_page == "about":
        render_about_page()

def render_home_page():
    """Render the home page."""
    st.title("Micro Plastic Database Explorer")
    st.markdown("### A Comprehensive Collection of Microplastic Research Data")
    
    # Calculate metrics
    try:
        total_records = sum(len(DataLoader.load_data(d["file"])) for d in datasets.values())
    except Exception as e:
        logger.error(f"Error calculating total records: {str(e)}")
        total_records = 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{total_records:,}</div>
                <div class="metric-label">Total Records</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{len(datasets)}</div>
                <div class="metric-label">Available Databases</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{datetime.now().strftime("%Y-%m-%d")}</div>
                <div class="metric-label">Last Updated</div>
            </div>
        """, unsafe_allow_html=True)

    # Display database information
    st.markdown("## Integrated Databases")
    for name, info in datasets.items():
        st.markdown(f"""
            <div class="dataset-card">
                <div class="dataset-title">{name}</div>
                <p>{info['description']}</p>
                <a href="{info['url']}" target="_blank">Access Source →</a>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## Other Databases")
    for name, info in external_databases.items():
        st.markdown(f"""
            <div class="dataset-card">
                <div class="dataset-title">{name}</div>
                <p>{info['description']}</p>
                <a href="{info['url']}" target="_blank">Access Database →</a>
            </div>
        """, unsafe_allow_html=True)

def render_data_explorer():
    """Render the data explorer page."""
    st.title("Data Explorer")
    
    dataset_choice = st.selectbox(
        "Select a database",
        options=list(datasets.keys())
    )
    
    # Reset selected columns if a new dataset is selected
    if st.session_state.current_dataset != dataset_choice:
        st.session_state.selected_columns = None
        st.session_state.current_dataset = dataset_choice
    
    try:
        df = DataLoader.load_data(datasets[dataset_choice]["file"])
        
        # Initialize selected columns if necessary
        if st.session_state.selected_columns is None:
            st.session_state.selected_columns = df.columns.tolist()
        
        # Display dataset info and download button
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
        
        # Column selector
        if st.button("Toggle Column Selector"):
            st.session_state.show_column_selector = not st.session_state.show_column_selector
            
        if st.session_state.show_column_selector:
            selected_cols = st.multiselect(
                "Select columns to display",
                options=df.columns.tolist(),
                default=st.session_state.selected_columns
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
        logger.error(f"Error in data explorer: {str(e)}")
        st.error(f"Error loading data: {str(e)}")

def render_polymer_search():
    """Render the polymer search page."""
    st.title("Polymer Search and Analysis")
    
    dataset_choice = st.selectbox(
        "Select a database",
        options=list(datasets.keys()),
        key="polymer_dataset_selector"
    )

    try:
        df = DataLoader.load_data(datasets[dataset_choice]["file"])
        
        # Determine polymer column
        polymer_column = 'Polymers' if 'Polymers' in df.columns else 'Polymer'
        
        if polymer_column in df.columns:
            # Extract unique polymers and their counts
            polymers_series = df[polymer_column].dropna().str.split(',').explode().str.strip()
            polymer_counts = polymers_series.value_counts()
            
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
                st.markdown(f"Total occurrences: **{polymer_counts[selected_polymer]}** "
                          f"(**{(polymer_counts[selected_polymer] / polymer_counts.sum() * 100):.2f}%**)")
                
                # Display filtered data
                st.subheader("Filtered Data")
                st.dataframe(filtered_data, height=400)
                
                # Download button for filtered data
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
        logger.error(f"Error in polymer search: {str(e)}")
        st.error(f"Error processing data: {str(e)}")

def render_ftir_viewer():
    """Render the FTIR viewer page."""
    st.title("FTIR Spectrum Viewer")
    st.markdown("""
    Upload FTIR spectrum data to visualize and analyze peaks. 
    Each CSV file should contain two columns: wavenumber and transmittance.
    """)
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload FTIR CSV files",
        type="csv",
        accept_multiple_files=True,
        help="Each CSV should have two columns: wavenumber and transmittance"
    )
    
    if uploaded_files:
        processor = FTIRProcessor()
        
        # Process uploaded files
        for file in uploaded_files:
            try:
                if file.name not in st.session_state.processed_ftir_files:
                    df = processor.process_ftir_file(file)
                    peaks = processor.find_peaks_in_spectrum(df)
                    st.session_state.processed_ftir_files[file.name] = {
                        'data': df,
                        'peaks': peaks
                    }
            except Exception as e:
                logger.error(f"Error processing FTIR file {file.name}: {str(e)}")
                st.error(f"Error processing {file.name}: {str(e)}")
        
        # Visualization
        if st.session_state.processed_ftir_files:
            view_mode = st.radio(
                "Select View Mode",
                ["Individual", "Combined"],
                disabled=len(st.session_state.processed_ftir_files) < 2
            )
            
            if view_mode == "Individual":
                selected_file = st.selectbox(
                    "Select file to visualize",
                    options=list(st.session_state.processed_ftir_files.keys())
                )
                
                if selected_file:
                    file_data = st.session_state.processed_ftir_files[selected_file]
                    spectrum_fig = create_plotly_spectrum(
                        file_data['data'], 
                        file_data['peaks'], 
                        f"FTIR Spectrum - {selected_file}"
                    )
                    st.plotly_chart(spectrum_fig, use_container_width=True)
                    
                    # Peak analysis
                    st.markdown("### Peak Analysis")
                    st.dataframe(file_data['peaks'])
            
            else:  # Combined view
                combined_fig = create_plotly_spectrum(
                    next(iter(st.session_state.processed_ftir_files.values()))['data'],
                    title="Combined FTIR Spectra"
                )
                
                # Add other spectra
                for name, file_data in list(st.session_state.processed_ftir_files.items())[1:]:
                    combined_fig.add_trace(
                        go.Scatter(
                            x=file_data['data']['cm-1'],
                            y=file_data['data']['transmittance'],
                            name=name
                        )
                    )
                
                st.plotly_chart(combined_fig, use_container_width=True)

def render_about_page():
    """Render the about page."""
    st.title("About")
    st.markdown("""
    ## About the Database Viewer
    
    This platform aggregates multiple microplastic databases into a single, accessible interface. 
    It provides tools for exploring and analyzing microplastic data from various sources.
    
    ### Data Sources
    - Environmental Laboratory of the U.S. Army Engineer Research and Development Center
    - NOAA National Centers for Environmental Information
    - Rochman Laboratory at the University of Toronto
    
    ### Features
    - Interactive data exploration
    - Polymer-specific analysis
    - FTIR spectrum visualization
    - Data export capabilities
    
    ### Technical Details
    Built with:
    - Streamlit
    - Pandas
    - Plotly
    - NumPy
    - SciPy
    
    For more information about the data sources or to report issues, please visit the respective database websites 
    listed on the home page.
    """)

if __name__ == "__main__":
    main()