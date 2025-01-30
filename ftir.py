import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.signal import find_peaks
from groq import Groq
import json
import io
import base64
from datetime import datetime
from contextlib import contextmanager
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="FTIR Analyzer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .analysis-card {
        background-color: black;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .plotly-chart {
        background-color: black;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] {
        font-size: 20px;
    }
    </style>
""", unsafe_allow_html=True)

@contextmanager
def check_groq_auth(client):
    """Check if Groq authentication is working"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model="mixtral-8x7b-32768",
            max_tokens=1
        )
        yield True
    except Exception as e:
        yield False

class FTIRAnalyzer:
    def __init__(self):
        self.groq_client = Groq(api_key="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")
        with check_groq_auth(self.groq_client) as auth_status:
            self.auth_status = auth_status

    def get_auth_status(self):
        return self.auth_status

    @staticmethod
    def process_ftir_file(file):
        try:
            df = pd.read_csv(file)
            if len(df.columns) != 2:
                raise ValueError("CSV must have exactly 2 columns: wavenumber and transmittance")
            
            df.columns = ['cm-1', 'transmittance']
            df['absorbance'] = np.log10(100/df['transmittance'])
            return df
        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")

    @staticmethod
    def find_peaks_in_spectrum(df):
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

    def analyze_with_llm(self, peak_data, is_combined=False):
        if is_combined:
            prompt = self._create_combined_analysis_prompt(peak_data)
        else:
            prompt = self._create_single_analysis_prompt(peak_data)
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="mixtral-8x7b-32768",
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error in LLM analysis: {str(e)}")
            return None

    @staticmethod
    def _create_single_analysis_prompt(peak_data):
        return f"""
        You are a spectroscopy expert. Analyze this FTIR data and provide results in the following JSON format:
        {{
            "functional_groups": [
                {{"wavenumber": float, "group": string, "confidence": float}}
            ],
            "material_composition": [
                {{"material": string, "probability": float}}
            ],
            "quality_metrics": {{
                "signal_to_noise": float,
                "baseline_stability": string,
                "peak_resolution": string
            }},
            "key_findings": [string],
            "recommendations": [string]
        }}

        Peak Data (top 10 peaks):
        {peak_data.to_string()}
        """

    @staticmethod
    def _create_combined_analysis_prompt(peak_data):
        return f"""
        Compare these FTIR samples and provide results in the following JSON format:
        {{
            "sample_similarities": [string],
            "sample_differences": [string],
            "common_functional_groups": [
                {{"group": string, "frequency": float}}
            ],
            "sample_quality_comparison": {{
                "best_quality_sample": string,
                "quality_metrics": {{
                    "signal_to_noise": float,
                    "peak_resolution": string
                }}
            }},
            "recommendations": [string]
        }}

        Peak Data:
        {peak_data.to_string()}
        """

def create_plotly_spectrum(df, peaks=None, title="FTIR Spectrum"):
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

def parse_llm_analysis(analysis_text):
    try:
        # Try to parse the JSON response
        return json.loads(analysis_text)
    except:
        # If parsing fails, return a formatted message
        return {
            "error": "Could not parse LLM response",
            "raw_text": analysis_text
        }

def display_analysis_dashboard(analysis_data, spectrum_fig):
    st.markdown("### FTIR Analysis Dashboard")
    
    # Create tabs for different aspects of the analysis
    tab1, tab2, tab3 = st.tabs(["Spectrum Analysis", "Chemical Composition", "Recommendations"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(spectrum_fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Peak Analysis")
            if 'functional_groups' in analysis_data:
                for group in analysis_data['functional_groups']:
                    with st.container():
                        st.markdown(f"""
                        <div class="analysis-card">
                            <h5>{group['group']}</h5>
                            <p>Wavenumber: {group['wavenumber']} cm⁻¹</p>
                            <p>Confidence: {group['confidence']*100:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Material Composition")
            if 'material_composition' in analysis_data:
                fig = px.pie(
                    values=[m['probability'] for m in analysis_data['material_composition']],
                    names=[m['material'] for m in analysis_data['material_composition']],
                    title="Material Distribution"
                )
                st.plotly_chart(fig)
        
        with col2:
            st.markdown("#### Quality Metrics")
            if 'quality_metrics' in analysis_data:
                metrics_col1, metrics_col2 = st.columns(2)
                for i, (metric, value) in enumerate(analysis_data['quality_metrics'].items()):
                    with metrics_col1 if i % 2 == 0 else metrics_col2:
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=value
                        )
    
    with tab3:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Key Findings")
            if 'key_findings' in analysis_data:
                for finding in analysis_data['key_findings']:
                    st.markdown(f"""
                    <div class="analysis-card">
                        {finding}
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Recommendations")
            if 'recommendations' in analysis_data:
                for rec in analysis_data['recommendations']:
                    st.markdown(f"""
                    <div class="analysis-card">
                        {rec}
                    </div>
                    """, unsafe_allow_html=True)

def main():
    st.title("FTIR Spectrum Analyzer Dashboard")
    
    analyzer = FTIRAnalyzer()
    
    # Authentication status
    auth_status = analyzer.get_auth_status()
    status_col1, status_col2 = st.columns([1, 5])
    
    with status_col1:
        if auth_status:
            st.success("🟢")
        else:
            st.error("🔴")
    
    with status_col2:
        if auth_status:
            st.success("Groq API Connected")
        else:
            st.error("Groq API Connection Failed")
            st.warning("Analysis features will be disabled")
    
    # Initialize session state
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = {}
    if 'peak_data' not in st.session_state:
        st.session_state.peak_data = {}
    
    # Sidebar for file upload and controls
    with st.sidebar:
        st.header("Upload Data")
        uploaded_files = st.file_uploader(
            "Upload FTIR CSV files",
            type="csv",
            accept_multiple_files=True,
            help="Each CSV should have two columns: wavenumber and transmittance"
        )
        
        if uploaded_files:
            st.header("Analysis Controls")
            analysis_type = st.radio(
                "Select Analysis Type",
                ["Individual", "Combined"],
                disabled=len(uploaded_files) < 2
            )
    
    # Main content area
    if uploaded_files:
        # Process uploaded files
        for file in uploaded_files:
            try:
                if file.name not in st.session_state.processed_files:
                    df = analyzer.process_ftir_file(file)
                    peaks = analyzer.find_peaks_in_spectrum(df)
                    st.session_state.processed_files[file.name] = df
                    st.session_state.peak_data[file.name] = peaks
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
        
        # Analysis section
        if st.session_state.processed_files:
            if 'analysis_type' in locals() and analysis_type == "Individual":
                selected_file = st.selectbox(
                    "Select file to analyze",
                    options=list(st.session_state.processed_files.keys())
                )
                
                if selected_file:
                    df = st.session_state.processed_files[selected_file]
                    peaks = st.session_state.peak_data[selected_file]
                    
                    spectrum_fig = create_plotly_spectrum(df, peaks, f"FTIR Spectrum - {selected_file}")
                    
                    if st.button("Analyze Spectrum", disabled=not auth_status):
                        with st.spinner("Analyzing spectrum..."):
                            analysis = analyzer.analyze_with_llm(peaks)
                            if analysis:
                                analysis_data = parse_llm_analysis(analysis)
                                display_analysis_dashboard(analysis_data, spectrum_fig)
            
            elif len(st.session_state.processed_files) > 1:
                combined_fig = create_plotly_spectrum(
                    next(iter(st.session_state.processed_files.values())),
                    title="Combined FTIR Spectra"
                )
                
                # Add other spectra
                for name, df in list(st.session_state.processed_files.items())[1:]:
                    combined_fig.add_trace(
                        go.Scatter(x=df['cm-1'], y=df['transmittance'], name=name)
                    )
                
                if st.button("Analyze All Spectra", disabled=not auth_status):
                    with st.spinner("Performing combined analysis..."):
                        combined_peaks = pd.concat(
                            [peaks.assign(Sample=name) for name, peaks in st.session_state.peak_data.items()],
                            ignore_index=True
                        )
                        analysis = analyzer.analyze_with_llm(combined_peaks, is_combined=True)
                        if analysis:
                            analysis_data = parse_llm_analysis(analysis)
                            display_analysis_dashboard(analysis_data, combined_fig)

if __name__ == "__main__":
    main()