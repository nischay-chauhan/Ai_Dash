import streamlit as st
import requests
from config import API_BASE_URL, TOKEN_KEY, USER_INFO_KEY

def login_user(email, password):
    """
    Authenticates user with the backend and stores the token.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state[TOKEN_KEY] = data["access_token"]
            # We might want to fetch user info here or decode the token
            # For now, let's just store a flag
            st.session_state["authenticated"] = True
            st.session_state["user_email"] = email
            return True, "Login successful"
        else:
            return False, response.json().get("detail", "Login failed")
            
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def signup_user(email, password, role="user"):
    """
    Registers a new user.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json={"email": email, "password": password, "role": role}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state[TOKEN_KEY] = data["access_token"]
            st.session_state["authenticated"] = True
            st.session_state["user_email"] = email
            return True, "Signup successful"
        else:
            return False, response.json().get("detail", "Signup failed")
            
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def logout_user():
    """
    Clears session state to log out the user.
    """
    if TOKEN_KEY in st.session_state:
        del st.session_state[TOKEN_KEY]
    if "authenticated" in st.session_state:
        del st.session_state["authenticated"]
    if "user_email" in st.session_state:
        del st.session_state["user_email"]
    
    # Rerun to update UI
    st.rerun()

def get_auth_headers():
    """
    Returns headers with Bearer token for API requests.
    """
    if TOKEN_KEY in st.session_state:
        return {"Authorization": f"Bearer {st.session_state[TOKEN_KEY]}"}
    return {}

def is_authenticated():
    """
    Checks if the user is currently authenticated.
    """
    return st.session_state.get("authenticated", False)

def require_auth():
    """
    Redirects to login if not authenticated.
    """
    if not is_authenticated():
        st.warning("Please log in to access this page.")
        st.stop()
