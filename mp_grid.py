import streamlit as st
import pandas as pd

# Initialize session state
if 'polymer_list' not in st.session_state:
    st.session_state.polymer_list = {}
if 'selected_polymer' not in st.session_state:
    st.session_state.selected_polymer = None
if 'current_dataset' not in st.session_state:
    st.session_state.current_dataset = None

# Example datasets
datasets = {
    "MP_SED - A Microplastic Database for Sediments": {
        "file": "MP_SED_A_Microplastic_Database_for_SEDiments.csv",  # Replace with actual file path
        "columns_of_interest": ['Polymers'],
    },
    "SLOPP": {
        "file": "SLOPP.csv",  # Replace with actual file path
        "columns_of_interest": ['Polymer'],
    }
}

# Function to load data
def load_data(file):
    try:
        return pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(file, encoding="latin1")

# Extract polymers from dataset
def extract_polymers(dataset_name):
    dataset_info = datasets[dataset_name]
    data = load_data(dataset_info['file'])
    polymers_column = dataset_info['columns_of_interest'][0]

    polymers_series = data[polymers_column].dropna().str.split(',').explode().str.strip()
    polymer_counts = polymers_series.value_counts()

    st.session_state.polymer_list[dataset_name] = polymer_counts

# Main application page
def polymer_search_page():
    st.set_page_config(page_title="Polymer Search", layout="wide")
    st.title("Polymer Search and Analysis")

    # Dataset selection
    col1, col2 = st.columns([3, 1])
    with col1:
        dataset_switch = st.selectbox(
            label="Select Dataset",
            options=datasets.keys(),
            index=list(datasets.keys()).index(st.session_state.current_dataset)
            if st.session_state.current_dataset else 0
        )

    if dataset_switch != st.session_state.current_dataset:
        st.session_state.current_dataset = dataset_switch
        st.session_state.selected_polymer = None
        extract_polymers(dataset_switch)

    # Display current dataset's polymer list
    polymer_data = st.session_state.polymer_list.get(st.session_state.current_dataset, pd.Series())
    st.subheader(f"Polymer Data: {st.session_state.current_dataset}")
    if not polymer_data.empty:
        st.dataframe(polymer_data, height=00)

        # Polymer selection
        selected_polymer = st.selectbox(
            label="Select a Polymer for Detailed Analysis",
            options=[None] + list(polymer_data.index),
            index=0
        )

        # Check if the polymer exists
        if selected_polymer:
            if selected_polymer in polymer_data.index:
                st.session_state.selected_polymer = selected_polymer
                dataset_info = datasets[st.session_state.current_dataset]
                data = load_data(dataset_info['file'])
                polymers_column = dataset_info['columns_of_interest'][0]
                filtered_data = data[data[polymers_column].str.contains(selected_polymer, na=False)]

                # Display polymer details and stats
                st.markdown(f"Occurrences: **{polymer_data[selected_polymer]}** ( **{(polymer_data[selected_polymer] / polymer_data.sum() * 100):.2f}%**)")
                st.subheader("Filtered Data")
                st.dataframe(filtered_data, height=300)
            else:
                st.error(f"The polymer '{selected_polymer}' does not exist in the selected dataset.")
        else:
            st.info("Select a polymer to view details.")
    else:
        st.warning(f"No data available for the selected dataset: {st.session_state.current_dataset}")

# Run the application
if __name__ == '__main__':
    st.session_state.current_dataset = list(datasets.keys())[0]
    extract_polymers(st.session_state.current_dataset)
    polymer_search_page()
