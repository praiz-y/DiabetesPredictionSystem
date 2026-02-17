Diabetes Prediction System: A Dual-Stream AI Approach
    This repository contains a comprehensive Machine Learning system designed to predict diabetes risk using two distinct data streams: Clinical Laboratory Data and Lifestyle Behavioral Patterns.

📂 Project Structure

scripts/ (The Core Application)
        app.py: The main entry point. A Streamlit web application that provides the user interface for both clinical and lifestyle assessments.

        logic.py: The "Intelligence Layer." Contains the hybrid logic that combines Machine Learning predictions with medical rule-based overrides.

        database.py: Manages the SQLite database, handling user records, history tracking, and admin statistics.

        admin.py: A secure dashboard for healthcare administrators to visualize population trends and manage patient data.

        requirements.txt: List of all Python libraries needed to run the system.

notebooks/ (Research & Development)
        01_pima_eda.ipynb: Exploratory Data Analysis of the Pima Indians Clinical Dataset.

        02_pima_model_training.ipynb: The training pipeline for the clinical Random Forest model, including SMOTE for data balancing.

        03_cdc_eda.ipynb: Analysis of the CDC Lifestyle Dataset to identify key behavioral risk factors.

        04_cdc_model_training.ipynb: Training and validation of the lifestyle-based prediction model.

📊 How to Get the Data
To keep this repository lightweight, the datasets are not included. Please download them from Kaggle and place them in a folder named datasets/:

Clinical Data: Pima Indians Diabetes Database

Save as: diabetes.csv

Lifestyle Data: Diabetes Health Indicators Dataset

Save as: diabetes_binary_health_indicators_BRFSS2015.csv

🛠️ Installation & Setup
Clone the Repo:

Bash
git clone [(https://github.com/praiz-y/DiabetesPredictionSystem)]
cd [folder-name]
Install Dependencies:

Bash
pip install -r _scripts/requirements.txt
Run the App:

Bash
streamlit run _scripts/app.py
🔐 Admin Access
The system includes a secure Admin Panel (admin.py) for health officials.

Default Password: admin123

Features: Real-time risk distribution charts, BMI vs. Glucose correlation plots, and CSV data export.