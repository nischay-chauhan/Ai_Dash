import streamlit as st
import requests
import pandas as pd
from config import API_URL
from utils.auth import get_auth_headers

st.set_page_config(page_title="Upload Data", page_icon="📂")

def upload_page():
    st.title("📂 Upload CSV Data")
    
    if "access_token" not in st.session_state:
        st.warning("Please log in to upload files.")
        st.stop()
        
    st.subheader("Upload New File")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        if st.button("Upload File", type="primary"):
            with st.spinner("Uploading..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
                    headers = get_auth_headers()
                    
                    response = requests.post(
                        f"{API_URL}/upload/",
                        files=files,
                        headers=headers
                    )
                    
                    if response.status_code == 202:
                        data = response.json()
                        task_id = data.get("task_id")
                        upload_id = data.get("upload_id")
                        
                        st.success(f"File '{uploaded_file.name}' uploaded! Processing...")
                        
                        # Progress Bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # SSE Client to listen for progress
                        try:
                            # Connect to the SSE stream
                            # Note: We use stream=True to keep connection open
                            stream_url = f"{API_URL}/tasks/{task_id}/stream"
                            with requests.get(stream_url, stream=True) as stream_response:
                                for line in stream_response.iter_lines():
                                    if line:
                                        decoded_line = line.decode('utf-8')
                                        if decoded_line.startswith("data:"):
                                            import json
                                            event_data = json.loads(decoded_line[5:])
                                            
                                            status = event_data.get("status")
                                            percent = event_data.get("percent", 0)
                                            message = event_data.get("message", "")
                                            
                                            # Update UI
                                            progress_bar.progress(percent / 100)
                                            status_text.text(f"{status.title()}: {message}")
                                            
                                            if status == "completed":
                                                st.success("Processing Complete!")
                                                st.session_state["last_upload_id"] = upload_id
                                                if st.button("View Data Summary"):
                                                    st.switch_page("pages/04_Data_Summary.py")
                                                break
                                            elif status == "failed":
                                                st.error(f"Processing Failed: {event_data.get('error')}")
                                                break
                                                
                        except Exception as e:
                            st.error(f"Error tracking progress: {str(e)}")
                            
                    elif response.status_code == 400:
                        st.error(f"Upload failed: {response.json().get('detail')}")
                    else:
                        st.error(f"An error occurred: {response.text}")
                        
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")

    st.markdown("---")

    st.subheader("Your Uploaded Files")
    
    try:
        headers = get_auth_headers()
        response = requests.get(f"{API_URL}/upload/", headers=headers)
        
        if response.status_code == 200:
            uploads = response.json()
            
            if not uploads:
                st.info("No files uploaded yet.")
            else:
                # Create a DataFrame for better display
                data = []
                for upload in uploads:
                    data.append({
                        "Filename": upload["filename"],
                        "Size (KB)": round(upload["size"] / 1024, 2),
                        "Uploaded At": pd.to_datetime(upload["uploaded_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                        "Status": upload["status"]
                    })
                
                df = pd.DataFrame(data)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Status": st.column_config.TextColumn(
                            "Status",
                            help="Current processing status of the file",
                            validate="^uploaded|processing|completed|failed$"
                        )
                    }
                )
                
        else:
            st.error("Failed to fetch uploads.")
            
    except Exception as e:
        st.error(f"Error fetching uploads: {str(e)}")

if __name__ == "__main__":
    upload_page()
