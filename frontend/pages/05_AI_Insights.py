import streamlit as st
import requests
import json
from config import API_URL
from utils.auth import get_auth_headers
from utils.ui import load_custom_css

st.set_page_config(page_title="AI Insights", page_icon="🤖", layout="wide")

def ai_insights_page():
    load_custom_css()
    
    st.title("🤖 AI Insights")
    st.markdown("Generate **AI-powered insights** from your uploaded datasets.")

    if "access_token" not in st.session_state:
        st.warning("Please log in to use AI Insights.")
        st.stop()
        
    headers = get_auth_headers()
    
    try:
        response = requests.get(f"{API_URL}/upload/", headers=headers)
        if response.status_code == 200:
            uploads = response.json()
            if not uploads:
                st.info("No files uploaded yet. Go to the Upload page to add data.")
                st.stop()
                
            upload_options = {u["filename"]: u["id"] for u in uploads}
            
            default_index = 0
            if "last_upload_id" in st.session_state:
                for i, u in enumerate(uploads):
                    if u["id"] == st.session_state["last_upload_id"]:
                        default_index = i
                        break
            
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    selected_filename = st.selectbox(
                        "Select a dataset to analyze:",
                        list(upload_options.keys()),
                        index=default_index
                    )
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True) # Spacer
                    upload_id = upload_options[selected_filename]
                    generate_btn = st.button("✨ Generate Insights", type="primary", use_container_width=True)
            
            if generate_btn:
                with st.spinner("Analyzing dataset... this may take a moment."):
                    try:
                        ai_response = requests.post(f"{API_URL}/ai/insights/{upload_id}", headers=headers)
                        
                        if ai_response.status_code == 200:
                            data = ai_response.json()
                            insights = data.get("insights", [])
                            
                            st.session_state["current_insights"] = insights
                            st.success("Insights generated successfully!")
                        else:
                            st.error(f"Failed to generate insights: {ai_response.text}")
                            
                    except Exception as e:
                        st.error(f"Error connecting to AI service: {str(e)}")

            if "current_insights" in st.session_state:
                st.divider()
                st.subheader("Key Findings")
                
                insights = st.session_state["current_insights"]
                
                if isinstance(insights, list):
                    for i, insight in enumerate(insights):
                        st.markdown(f"""
                        <div class="insight-card">
                            <strong>Insight {i+1}</strong><br>
                            {insight}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("Insights format unexpected. Raw output:")
                    st.code(str(insights))
                
                st.divider()
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    insights_text = "\n\n".join([f"- {ins}" for ins in insights]) if isinstance(insights, list) else str(insights)
                    st.download_button(
                        label="📥 Download Insights",
                        data=insights_text,
                        file_name=f"insights_{selected_filename}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

    except Exception as e:
        st.error(f"Error fetching uploads: {str(e)}")

if __name__ == "__main__":
    ai_insights_page()
