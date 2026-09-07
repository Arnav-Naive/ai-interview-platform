# Project Setup and Run Instructions

This project is a Django-based web application with Gemini AI integration for resume analysis.

## Prerequisites

*   Python 3.10 or higher
*   Virtual environment tool (`venv`)

## Getting Started

Follow these steps to set up and run the project locally.

### 1. Set Up Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies

Install the required Python packages using pip:

```bash
pip install django google-generativeai requests pydantic
```
*(Note: Refer to `pip freeze` for the exact versions if needed.)*

### 3. Configure Gemini AI API Key (Optional)

The project uses Google's Gemini AI. If you have an API key, set it in `chaiaurDjango/chaiaurDjango/settings.py`:

```python
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```

**Mock Mode:** If you do not have an API key, the system will automatically run in "Mock Mode," providing a simulated resume analysis so you can still test the application.

### 4. Database Migrations

Apply the database migrations to set up the SQLite database:

```bash
cd chaiaurDjango
python manage.py migrate
```

### 5. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

### 6. Access the Application

Once the server is running, open your web browser and navigate to:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Project Structure

*   `chaiaurDjango/` - Main Django project directory.
    *   `manage.py` - Django's command-line utility.
    *   `users/` - Application handling user registration and login.
    *   `templates/` - HTML templates for the website and user views.
    *   `media/` - Directory for uploaded files (e.g., resumes).
*   `.venv/` - Virtual environment directory.
