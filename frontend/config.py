import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# UI Configuration
APP_TITLE = "AI Dashboard"
APP_ICON = "📊"

# Auth Configuration
TOKEN_KEY = "access_token"
USER_INFO_KEY = "user_info"
