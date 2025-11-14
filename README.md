# AI Dashboard (Ai_Dash)

A powerful AI-powered dashboard application built with FastAPI, Celery, and modern web technologies. This application provides a robust backend for handling file uploads, data processing, and AI-powered analytics.

## Features

- **User Authentication**: Secure user registration and login system
- **File Upload**: Upload and manage various file types
- **AI Processing**: Integrates AI models for data analysis
- **Task Management**: Asynchronous task processing with Celery
- **RESTful API**: Clean, well-documented API endpoints
- **Database**: SQLAlchemy ORM with SQLite (can be configured for other databases)

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Redis (for Celery task queue)
- Virtual environment (recommended)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Ai_Dash
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt  # Create this file with your dependencies
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following variables:
   ```
   DATABASE_URL=sqlite:///./app.db
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Initialize the database**
   ```bash
   alembic upgrade head
   ```

6. **Start Redis server**
   ```bash
   redis-server
   ```

7. **Start Celery worker**
   ```bash
   celery -A backend.celery_app worker --loglevel=info
   ```

8. **Run the application**
   ```bash
   uvicorn backend.main:app --reload
   ```

9. **Access the API documentation**
   Open your browser and navigate to:
   ```
   http://localhost:8000/docs
   ```

## API Endpoints

- `/auth/*`: User authentication endpoints
- `/upload/*`: File upload and management
- `/data/*`: Data retrieval and processing
- `/ai/*`: AI model endpoints
- `/tasks/*`: Task status and management

## AI Features

- Document summarization
- Data analysis
- File content extraction
- Asynchronous processing

## Testing

To run the test suite:
```bash
pytest tests/
```

## Project Structure

```
Ai_Dash/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── celery_app.py        # Celery configuration
│   ├── models/              # Database models
│   ├── routers/             # API route handlers
│   └── tasks/               # Background tasks
├── migrations/              # Database migrations
├── uploads/                 # Uploaded files storage
└── requirements.txt         # Project dependencies
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For any questions or feedback, please open an issue on GitHub.
