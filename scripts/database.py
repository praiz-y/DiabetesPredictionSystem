import sqlite3
import pandas as pd
from datetime import datetime
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'diabetes_records.db')

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table for clinical predictions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clinical_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pregnancies INTEGER,
            glucose REAL,
            blood_pressure REAL,
            skin_thickness REAL,
            insulin REAL,
            bmi REAL,
            diabetes_pedigree REAL,
            age INTEGER,
            prediction INTEGER,
            risk_percentage REAL,
            status TEXT
        )
    ''')
    
    # Create table for lifestyle predictions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lifestyle_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            high_bp INTEGER,
            high_chol INTEGER,
            bmi REAL,
            smoker INTEGER,
            physical_activity INTEGER,
            fruits INTEGER,
            vegetables INTEGER,
            heavy_alcohol INTEGER,
            general_health INTEGER,
            mental_health INTEGER,
            prediction REAL,
            risk_class TEXT,
            status TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")


def save_clinical_prediction(pregnancies, glucose, blood_pressure, skin_thickness, 
                             insulin, bmi, diabetes_pedigree, age, prediction, 
                             risk_percentage, status):
    """Save a clinical prediction record to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO clinical_predictions 
        (pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, 
         diabetes_pedigree, age, prediction, risk_percentage, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, 
          diabetes_pedigree, age, prediction, risk_percentage, status))
    
    conn.commit()
    conn.close()


def save_lifestyle_prediction(high_bp, high_chol, bmi, smoker, physical_activity, 
                              fruits, vegetables, heavy_alcohol, general_health, 
                              mental_health, prediction, risk_class, status):
    """Save a lifestyle prediction record to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO lifestyle_predictions 
        (high_bp, high_chol, bmi, smoker, physical_activity, fruits, vegetables, 
         heavy_alcohol, general_health, mental_health, prediction, risk_class, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (high_bp, high_chol, bmi, smoker, physical_activity, fruits, vegetables, 
          heavy_alcohol, general_health, mental_health, prediction, risk_class, status))
    
    conn.commit()
    conn.close()


def get_last_clinical_records(limit=5):
    """Get the last N clinical prediction records."""
    conn = sqlite3.connect(DB_PATH)
    query = f'''
        SELECT * FROM clinical_predictions 
        ORDER BY timestamp DESC 
        LIMIT {limit}
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_last_lifestyle_records(limit=5):
    """Get the last N lifestyle prediction records."""
    conn = sqlite3.connect(DB_PATH)
    query = f'''
        SELECT * FROM lifestyle_predictions 
        ORDER BY timestamp DESC 
        LIMIT {limit}
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_all_clinical_records():
    """Get all clinical prediction records."""
    conn = sqlite3.connect(DB_PATH)
    query = 'SELECT * FROM clinical_predictions ORDER BY timestamp DESC'
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_all_lifestyle_records():
    """Get all lifestyle prediction records."""
    conn = sqlite3.connect(DB_PATH)
    query = 'SELECT * FROM lifestyle_predictions ORDER BY timestamp DESC'
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_statistics():
    """Get overall statistics from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clinical stats
    cursor.execute('SELECT COUNT(*) FROM clinical_predictions')
    total_clinical = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM clinical_predictions WHERE prediction = 1')
    diabetic_clinical = cursor.fetchone()[0]
    
    # Lifestyle stats
    cursor.execute('SELECT COUNT(*) FROM lifestyle_predictions')
    total_lifestyle = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM lifestyle_predictions WHERE prediction = 2.0')
    diabetic_lifestyle = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM lifestyle_predictions WHERE prediction = 1.0')
    prediabetic_lifestyle = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_clinical': total_clinical,
        'diabetic_clinical': diabetic_clinical,
        'total_lifestyle': total_lifestyle,
        'diabetic_lifestyle': diabetic_lifestyle,
        'prediabetic_lifestyle': prediabetic_lifestyle
    }


def delete_record(table_name, record_id):
    """Delete a specific record from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if table_name in ['clinical_predictions', 'lifestyle_predictions']:
        cursor.execute(f'DELETE FROM {table_name} WHERE id = ?', (record_id,))
        conn.commit()
    
    conn.close()


def clear_all_records():
    """Clear all records from both tables (use with caution!)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM clinical_predictions')
    cursor.execute('DELETE FROM lifestyle_predictions')
    
    conn.commit()
    conn.close()