import streamlit as st
from utils.auth import login_user, is_authenticated
from config import APP_TITLE, APP_ICON

st.set_page_config(page_title=f"Login - {APP_TITLE}", page_icon=APP_ICON)

def login_page():
    st.title("Login")
    
    if is_authenticated():
        st.success("You are already logged in!")
        if st.button("Go to Home"):
            st.switch_page("streamlit_app.py")
        return

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                success, message = login_user(email, password)
                if success:
                    st.success(message)
                    st.switch_page("streamlit_app.py")
                else:
                    st.error(message)

    st.markdown("---")
    st.markdown("Don't have an account? [Sign up](/Signup)")

if __name__ == "__main__":
    login_page()
