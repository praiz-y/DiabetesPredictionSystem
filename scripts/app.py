import streamlit as st
import pandas as pd
import pickle
import numpy as np
import database as db
from logic import get_clinical_advice, get_lifestyle_advice

# Initialize the DB once when app starts
db.init_db()

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Diabetes Prediction System", layout="wide")

# --- INITIALIZE SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- LOAD MODELS & SCALERS ---
@st.cache_resource
def load_assets():
    with open('../models/pima_model.pkl', 'rb') as f:
        p_model = pickle.load(f)
    with open('../models/pima_scaler.pkl', 'rb') as f:
        p_scaler = pickle.load(f)
    with open('../models/cdc_model.pkl', 'rb') as f:
        c_model = pickle.load(f)
    with open('../models/cdc_scaler.pkl', 'rb') as f:  # Add this line
        c_scaler = pickle.load(f)
    return p_model, p_scaler, c_model, c_scaler

p_model, p_scaler, c_model, c_scaler = load_assets()

# --- CUSTOM CSS FOR BETTER STYLING ---
st.markdown("""
<style>
    /* Home Page Cards */
    .mode-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 20px 0;
        cursor: pointer;
        transition: transform 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .mode-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.2);
    }
    .mode-card-clinical {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .mode-card-lifestyle {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .mode-card h2 {
        margin: 0;
        font-size: 32px;
        font-weight: bold;
    }
    .mode-card p {
        margin: 15px 0 0 0;
        font-size: 16px;
        opacity: 0.9;
    }
    
    /* Radio button styling */
    .stRadio > div {
        background-color: #020e38;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #031b6b;
        width: fit-content;
    }
    
    .stRadio > div:hover {
        background-color: #283354;
        border-color: #667eea;
    }
    
    /* Radio button labels */
    .stRadio label {
        font-weight: 500;
        color: #d6ffe4;
    }
    
    /* History card styling */
    .history-card {
        background: #422edb;
        padding: 15px;
        border-radius: 10px;
        border-left: 6px solid #667eea;
        margin: 10px 0;
    }
            
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HOME PAGE
# =============================================================================
if st.session_state.page == 'home':
    st.title("🏥 Diabetes Prediction & Risk Assessment System")
    st.markdown("""
    Welcome to the **Intelligent Diabetes Prediction System**. This tool uses Machine Learning 
    to assess your diabetes risk through two different approaches.
    """)
    st.markdown("""
    <div>
        <h2>📚 About This System</h2>
        <p>Our system is designed to help you understand your risk of Type 2 Diabetes using two different paths. Depending on what information you have ready today, you can choose the assessment that suits you best.</p>
        <p><b>💠Clinical Mode</b> If you have a recent medical report, this mode looks at your actual numbers—like Glucose and BMI—to see if your body is showing signs of insulin resistance.<br>
        <b>💠Lifestyle Mode</b> No lab results? No problem. This mode looks at how you live, eat, and move. It helps identify if your current habits might be putting you at risk in the future, even if you feel fine today.</p>
        <br>
        <h3>Choose Your Assessment Mode:</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the mode cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="mode-card mode-card-clinical">
            <h2>Clinical Mode</h2>
            <p>Best if you have lab results (Glucose, Insulin, BMI, etc.)</p>
            <p><strong>Based on:</strong> Pima Indians Dataset</p>
            <p><strong>Output:</strong> Diabetic / Non-Diabetic</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Start Clinical Assessment", use_container_width=True, type="primary"):
            st.session_state.page = 'clinical'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="mode-card mode-card-lifestyle">
            <h2> Lifestyle Mode</h2>
            <p>General assessment based on daily habits and health history</p>
            <p><strong>Based on:</strong> CDC BRFSS Dataset</p>
            <p><strong>Output:</strong> Healthy / Pre-diabetic / Diabetic</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🥗 Start Lifestyle Assessment", use_container_width=True, type="primary"):
            st.session_state.page = 'lifestyle'
            st.rerun()
    
    # Footer
    st.markdown("---")

# =============================================================================
# CLINICAL MODE PAGE
# =============================================================================
elif st.session_state.page == 'clinical':
    # Home Button
    if st.button("🏠 Back to Home", type="secondary"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.header("🏥 Clinical Assessment (Lab-based)")
    st.write("Please enter the values from your clinical report.")
    
    # Show previous records
    with st.expander("📜 View Your Recent Clinical Records (Last 5)"):
        recent_clinical = db.get_last_clinical_records(5)
        if not recent_clinical.empty:
            for idx, row in recent_clinical.iterrows():
                status_emoji = "🚨" if row['prediction'] == 1 else "✅"
                st.markdown(f"""
                <div class="history-card">
                    <strong>{status_emoji} {row['timestamp']}</strong><br>
                    Status: {row['status']}<br>
                    Glucose: {row['glucose']} mg/dL | BMI: {row['bmi']} | Age: {row['age']} years<br>
                    Risk: {row['risk_percentage']}%
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No previous records found. Complete an assessment to start tracking your history!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        preg = st.number_input("Pregnancies", 0, 20, 0, 
                               help="Number of times the patient has been pregnant.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        gluc = st.number_input("Glucose Level (mg/dL)", 0, 300, 100, 
                               help="Plasma glucose concentration (2 hours in an oral glucose tolerance test).")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        bp = st.number_input("Blood Pressure (mmHg)", 0, 150, 70, 
                             help="Diastolic blood pressure (the bottom number of a blood pressure reading).")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        skin = st.number_input("Skin Thickness (mm)", 0, 100, 20, 
                               help="Thickness of the skin at the triceps, measured in millimeters. Used as an indicator of body fat.")
    
    with col2:
        ins = st.number_input("Insulin Level (mu U/ml)", 0, 900, 80, 
                               help="2-Hour serum insulin levels. High levels may indicate insulin resistance.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        bmi = st.number_input("BMI (Body Mass Index)", 0.0, 70.0, 25.0, 
                               help="Weight in kg divided by (height in meters squared).")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        pedi = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, 0.5, 
                               help="This number represents how likely you are to develop diabetes based on your family's medical history.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        age = st.number_input("Age", 1, 120, 30, 
                               help="Current age of the user in years.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔬 Analyze Clinical Risk", use_container_width=True, type="primary"):
        # 1. Prepare data & Scale
        features = np.array([[preg, gluc, bp, skin, ins, bmi, pedi, age]])
        features_scaled = p_scaler.transform(features)
        
        # 2. Get the probability scores
        prob_scores = p_model.predict_proba(features_scaled)[0] 
        prediction = p_model.predict(features_scaled)[0]
        
        # 3. Convert to percentage
        risk_percent = round(prob_scores[1] * 100, 2)
        
        # 4. Get advice
        status, reasons, tips = get_clinical_advice(prediction, features[0], risk_percent)
        
        # 5. Save to database
        db.save_clinical_prediction(
            pregnancies=int(preg),
            glucose=float(gluc),
            blood_pressure=float(bp),
            skin_thickness=float(skin),
            insulin=float(ins),
            bmi=float(bmi),
            diabetes_pedigree=float(pedi),
            age=int(age),
            prediction=int(prediction),
            risk_percentage=float(risk_percent),
            status=status
        )
        
        st.divider()
        
        # 6. Display Result
        if "DIABETIC" in status:
            st.error(f"### {status}")
        elif "PRE-DIABETIC" in status:
            st.warning(f"### {status}")
        else:
            st.success(f"### {status}")
        
        st.info("✅ This assessment has been saved to your records.")
        
        st.subheader("🔍 Why this result?")
        for r in reasons:
            st.write(f"- {r}")
        
        st.subheader("💡 Recommended Health Tips")
        for t in tips:
            st.write(f"{t}")

# =============================================================================
# LIFESTYLE MODE PAGE
# =============================================================================
elif st.session_state.page == 'lifestyle':
    # Home Button
    if st.button("🏠 Back to Home", type="secondary"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.header("🥗 General Health & Lifestyle Assessment")
    st.write("Answer the following questions about your lifestyle and health habits.")
    
    # Show previous records
    with st.expander("📜 View Your Recent Lifestyle Records (Last 5)"):
        recent_lifestyle = db.get_last_lifestyle_records(5)
        if not recent_lifestyle.empty:
            for idx, row in recent_lifestyle.iterrows():
                if row['prediction'] == 2.0:
                    status_emoji = "🚨"
                elif row['prediction'] == 1.0:
                    status_emoji = "⚠️"
                else:
                    status_emoji = "✅"
                
                st.markdown(f"""
                <div class="history-card">
                    <strong>{status_emoji} {row['timestamp']}</strong><br>
                    Status: {row['status']}<br>
                    BMI: {row['bmi']} | Risk Class: {row['risk_class']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No previous records found. Complete an assessment to start tracking your history!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        hp = st.radio("Do you have High Blood Pressure?", 
                      ["No", "Yes"],
                      horizontal=True,
                      help="Have you ever been told by a doctor that you have high blood pressure?")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        hc = st.radio("Do you have High Cholesterol?", 
                      ["No", "Yes"],
                      horizontal=True,
                      help="Have you ever been told by a doctor that you have high cholesterol?")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        bmi_c = st.number_input("BMI", 10.0, 60.0, 22.0, 
                               help="Body Mass Index (Weight in kg / Height in m^2).")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        smoke = st.radio("Have you smoked >100 cigarettes in your lifetime?", 
                        ["No", "Yes"],
                        horizontal=True,
                        help="Have you smoked at least 100 cigarettes in your entire life?")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        act = st.radio("Physical activity in last 30 days?", 
                       ["No", "Yes"],
                       horizontal=True,
                       help="Any exercise or physical activity other than your regular job.")
    
    with col2:
        fruit = st.radio("Do you eat fruits daily?", 
                        ["No", "Yes"],
                        horizontal=True,
                        help="Do you consume fruit 1 or more times per day?")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        veg = st.radio("Do you eat vegetables daily?", 
                      ["No", "Yes"],
                      horizontal=True,
                      help="Do you consume vegetables 1 or more times per day?")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        alc = st.radio("Are you a heavy drinker?", 
                      ["No", "Yes"],
                      horizontal=True,
                      help="Men: >14 drinks/week. Women: >7 drinks/week.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        gen = st.slider("General Health (1=Excellent, 5=Poor)", 1, 5, 3, 
                        help="How would you rate your general health in the last month?")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        men = st.slider("Mental health 'not good' days", 0, 30, 0, 
                        help="Number of days in the last 30 days your mental health was not good.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔍 Assess Lifestyle Risk", use_container_width=True, type="primary"):
        # Convert inputs (radio buttons always have a value)
        hp_val = 1 if hp == "Yes" else 0
        hc_val = 1 if hc == "Yes" else 0
        smoke_val = 1 if smoke == "Yes" else 0
        act_val = 1 if act == "Yes" else 0
        fruit_val = 1 if fruit == "Yes" else 0
        veg_val = 1 if veg == "Yes" else 0
        alc_val = 1 if alc == "Yes" else 0
        
        inputs = np.array([[hp_val, hc_val, bmi_c, smoke_val, act_val, fruit_val, veg_val, alc_val, gen, men]])
        inputs_scaled = c_scaler.transform(inputs)      

        # Get probabilities using scaled data
        prediction = c_model.predict(inputs_scaled)[0]
        prob_scores = c_model.predict_proba(inputs_scaled)[0]
        
        # Convert to percentages
        risk_percents = [round(p * 100, 2) for p in prob_scores]
        
        # Get advice
        status, reasons, tips = get_lifestyle_advice(prediction, inputs[0], risk_percents)
        
        # Determine risk class for database
        if prediction == 2.0:
            risk_class = "Diabetic"
        elif prediction == 1.0:
            risk_class = "Pre-diabetic"
        else:
            risk_class = "Healthy"
        
        # Save to database
        db.save_lifestyle_prediction(
            high_bp=hp_val,
            high_chol=hc_val,
            bmi=float(bmi_c),
            smoker=smoke_val,
            physical_activity=act_val,
            fruits=fruit_val,
            vegetables=veg_val,
            heavy_alcohol=alc_val,
            general_health=gen,
            mental_health=men,
            prediction=float(prediction),
            risk_class=risk_class,
            status=status
        )
        
        st.divider() 
        
        # Display Result with Color Coding
        if "DIABETIC" in status:
            st.error(f"### {status}")
        elif "PRE-DIABETIC" in status:
            st.warning(f"### {status}")
        else:
            st.success(f"### {status}")

        st.info("✅ This assessment has been saved to your records.")

        # Display Explanations
        st.subheader("🔍 Why this result?")
        if reasons:
            for r in reasons:
                st.write(f"- {r}")
        else:
            st.write("- Your lifestyle habits indicate low vulnerability at this time.")

        # Display Tips
        st.subheader("💡 Recommended Lifestyle Changes")
        for t in tips:
            st.write(f"{t}")

# --- FOOTER (shown on all pages) ---
st.markdown("---")
st.caption("© 2026 Intelligent Diabetes Prediction System")
st.error("⚠️ **Medical Warning:** This is a decision support tool for educational purposes and not a replacement for professional medical advice. " \
"Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.")