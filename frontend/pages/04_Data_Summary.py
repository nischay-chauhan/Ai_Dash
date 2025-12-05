import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import API_URL
from utils.auth import get_auth_headers

st.set_page_config(page_title="Data Summary", page_icon="📊", layout="wide")

def data_summary_page():
    st.title("📊 Data Summary & Visualization")
    
    # Check authentication
    if "access_token" not in st.session_state:
        st.warning("Please log in to view data summaries.")
        st.stop()
        
    # Fetch list of uploads to allow selection
    headers = get_auth_headers()
    try:
        response = requests.get(f"{API_URL}/upload/", headers=headers)
        if response.status_code == 200:
            uploads = response.json()
            if not uploads:
                st.info("No files uploaded yet. Go to the Upload page to add data.")
                st.stop()
                
            upload_options = {u["filename"]: u["id"] for u in uploads}
            
            # Default to last uploaded if available
            default_index = 0
            if "last_upload_id" in st.session_state:
                for i, u in enumerate(uploads):
                    if u["id"] == st.session_state["last_upload_id"]:
                        default_index = i
                        break
            
            selected_filename = st.selectbox(
                "Select a dataset to analyze:",
                list(upload_options.keys()),
                index=default_index
            )
            
            upload_id = upload_options[selected_filename]
            
            if st.button("Analyze Dataset", type="primary"):
                with st.spinner("Fetching summary..."):
                    summary_response = requests.get(f"{API_URL}/data/summary/{upload_id}", headers=headers)
                    
                    if summary_response.status_code == 200:
                        summary = summary_response.json()
                        render_summary(summary)
                    else:
                        st.error(f"Failed to fetch summary: {summary_response.text}")
                        
    except Exception as e:
        st.error(f"Error fetching uploads: {str(e)}")

def render_summary(summary):
    st.divider()
    
    # 1. Dataset Overview
    st.header("1. Dataset Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", summary["shape"]["rows"])
    col2.metric("Columns", summary["shape"]["columns"])
    col3.metric("Missing Values", sum(summary["missing_values"].values()))
    
    # 2. Column Types
    st.subheader("Column Types")
    dtypes = summary["data_types"]
    dtype_counts = pd.Series(dtypes.values()).value_counts().reset_index()
    dtype_counts.columns = ["Type", "Count"]
    
    fig_types = px.pie(dtype_counts, values="Count", names="Type", title="Column Data Types")
    st.plotly_chart(fig_types, use_container_width=True)

    # 3. Missing Values
    st.header("2. Missing Values")
    missing = summary["missing_values"]
    missing_df = pd.DataFrame(list(missing.items()), columns=["Column", "Missing Count"])
    missing_df = missing_df[missing_df["Missing Count"] > 0]
    
    if not missing_df.empty:
        fig_missing = px.bar(missing_df, x="Column", y="Missing Count", title="Missing Values per Column")
        st.plotly_chart(fig_missing, use_container_width=True)
    else:
        st.success("No missing values found in the dataset!")

    # 4. Statistical Summary
    st.header("3. Statistical Summary")
    stats = pd.DataFrame(summary["stats"])
    st.dataframe(stats, use_container_width=True)

    # 5. Correlation Heatmap
    if "correlation" in summary:
        st.header("4. Correlation Heatmap")
        corr = pd.DataFrame(summary["correlation"])
        fig_corr = px.imshow(corr, text_auto=True, title="Correlation Matrix (Numeric Columns)")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Not enough numeric columns for correlation analysis.")

    # 6. Sample Data
    st.header("5. Sample Data")
    sample = pd.DataFrame(summary["sample_data"])
    st.dataframe(sample, use_container_width=True)

if __name__ == "__main__":
    data_summary_page()
