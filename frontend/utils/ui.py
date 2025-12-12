import streamlit as st

def load_custom_css():
    """Injects custom CSS into the Streamlit app."""
    st.markdown("""
        <style>
        /* Main Container */
        .main {
            background-color: #FFFFFF;
        }
        
        /* Card Style */
        .stCard {
            background-color: #FFFFFF;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #E5E7EB;
            margin-bottom: 1rem;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #111827;
            font-weight: 700;
        }
        
        /* Buttons */
        .stButton button {
            border-radius: 0.375rem;
            font-weight: 500;
            transition: all 0.2s;
        }
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        /* Custom Success/Info Messages */
        .stAlert {
            border-radius: 0.5rem;
        }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #F9FAFB;
            border-right: 1px solid #E5E7EB;
        }
        
        /* Insight Card */
        .insight-card {
            background-color: #F0F9FF;
            border-left: 4px solid #0EA5E9;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 0.25rem;
        }
        
        </style>
    """, unsafe_allow_html=True)

def card_container(key=None):
    """Creates a container that looks like a card."""
    container = st.container()
    return container

def styled_metric(label, value, delta=None):
    """Displays a styled metric."""
    st.metric(label=label, value=value, delta=delta)
