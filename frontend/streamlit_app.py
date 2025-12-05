import streamlit as st
from config import APP_TITLE, APP_ICON
from utils.auth import is_authenticated, logout_user

# Page Configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title(f"{APP_ICON} {APP_TITLE}")
    
    if is_authenticated():
        st.sidebar.success(f"Logged in as {st.session_state.get('user_email')}")
        if st.sidebar.button("Logout"):
            logout_user()
            
        st.markdown("""
        ### Welcome to your AI Dashboard!
        
        Use the sidebar to navigate through the application features:
        
        - **📂 Upload**: Upload your CSV datasets
        - **📊 Data Summary**: View statistics and visualizations
        - **🧠 AI Insights**: Get AI-powered analysis
        - **💬 Chat**: Ask questions about your data
        - **📋 Tasks**: Monitor background processing
        """)
        
    else:
        st.info("Please log in or sign up to continue.")
        st.markdown("""
        ### Features
        
        - **Secure Authentication**: User accounts and role management
        - **File Management**: Easy CSV uploads and processing
        - **Advanced Analytics**: Automatic data profiling and visualization
        - **AI Integration**: Powered by LLMs for deep insights
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Go to Login", use_container_width=True):
                st.switch_page("pages/01_Login.py")
        with col2:
            if st.button("Go to Signup", use_container_width=True):
                st.switch_page("pages/02_Signup.py")

if __name__ == "__main__":
    main()
