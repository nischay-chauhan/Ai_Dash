import streamlit as st
from utils.auth import signup_user, is_authenticated
from config import APP_TITLE, APP_ICON

st.set_page_config(page_title=f"Signup - {APP_TITLE}", page_icon=APP_ICON)

def signup_page():
    st.title("Sign Up")
    
    if is_authenticated():
        st.success("You are already logged in!")
        if st.button("Go to Home"):
            st.switch_page("streamlit_app.py")
        return

    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["user", "admin"])
        submit_button = st.form_submit_button("Sign Up")
        
        if submit_button:
            if not email or not password:
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                success, message = signup_user(email, password, role)
                if success:
                    st.success(message)
                    st.switch_page("streamlit_app.py")
                else:
                    st.error(message)

    st.markdown("---")
    st.markdown("Already have an account? [Login](/Login)")

if __name__ == "__main__":
    signup_page()
