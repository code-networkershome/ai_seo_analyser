# Frontend: AI SEO Analyzer Dashboard

Thus folder contains the user interface code built with **Streamlit**.

## Prerequisites
- The **Backend** must be running on `http://localhost:8000` for this UI to work.

## How to Run

1. Open a terminal in this `frontend/` folder.
2. Run the application:
   ```bash
   streamlit run app.py
   ```
3. The app will launch in your default browser at `http://localhost:8501`.

## Configuration
The app attempts to connect to the backend at `http://localhost:8000/analyze`. If you are running the backend on a different port, please update `app.py` line 67.
