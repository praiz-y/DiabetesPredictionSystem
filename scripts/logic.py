def get_clinical_advice(prediction, input_data, probability):
    """
    input_data order: Pregnancies, Glucose, BloodPressure, SkinThickness, 
    Insulin, BMI, Pedigree, Age
    """
    glucose = input_data[1]
    bp = input_data[2]
    bmi = input_data[5]
    age = input_data[7]
    
    reasons = []
    tips = []

    # 1. Logic for Explanations (Why)
    if glucose > 140:
        reasons.append(f"High Glucose ({glucose} mg/dL): Your blood sugar is elevated, which is the primary indicator of diabetes.")
    elif glucose > 100:
        reasons.append(f"Elevated Glucose ({glucose} mg/dL): Your blood sugar is slightly above normal range.")
    
    if bmi > 30:
        reasons.append(f"High BMI ({bmi}): Excess weight can make your body's cells more resistant to insulin.")
    elif bmi > 25:
        reasons.append(f"Elevated BMI ({bmi}): Being overweight increases diabetes risk.")
    
    if bp > 80:
        reasons.append(f"High Blood Pressure ({bp} mmHg): Hypertension often coexists with diabetes and increases cardiovascular risk.")
    
    if age > 45:
        reasons.append("Age Factor: Risk naturally increases as you get older, requiring more frequent monitoring.")

    # 2. Logic for Recommendations (What to do)
    if prediction == 1:
        # HIGH RISK - DIABETIC
        status = f"DIABETIC (High Risk - {probability:.1f}% probability)"
        tips = [
            "Immediate Action: Consult an endocrinologist for a formal diagnostic test (HbA1c).",
            "Nutrition: Adopt a 'Diabetes Plate Method'—half non-starchy vegetables, one-quarter protein, one-quarter starch.",
            "Monitoring: Start a log of your daily blood sugar levels to identify patterns.",
            "Activity: Aim for at least 30 minutes of brisk walking daily to help lower blood sugar.",
            "Medication: Discuss treatment options with your healthcare provider."
        ]
        
        # Add specific reasons if none were found
        if not reasons:
            reasons.append("Your clinical markers indicate a high probability of diabetes based on the model analysis.")
    else:
        if glucose >= 126:
            status = "⚠️ DIABETIC (High Glucose Override)"
        elif glucose >= 100:
            status = "⚠️ PRE-DIABETIC (Elevated Glucose)"
        else:
            status = f"✅ NON-DIABETIC (Low Risk - {100 - probability:.1f}% confidence)"
        if not reasons:
            reasons.append("Your clinical markers are currently within the healthy reference range.")
        # SMART OVERRIDE: Warning for high glucose even if AI is optimistic
        if glucose >= 126:
            tips = [
                "⚠️ CRITICAL ALERT: Your Glucose is in the Diabetic range (126+ mg/dL).",
                "• Immediate Action: Consult a doctor for an HbA1c test immediately.",
                "• Verification: Ensure this was a fasting test (no food for 8+ hours).",
                "• Diet: Cut out all sugary drinks and refined sweets until you see a doctor."
            ]
        elif glucose >= 100:
            tips = [
                "⚠️ PRE-DIABETIC WARNING: Your glucose (100-125 mg/dL) is above normal.",
                "• Reversible: This stage can often be reversed with diet and exercise.",
                "• Monitoring: Get a follow-up test in 3 months.",
                "• Exercise: Aim for 150 minutes of activity per week."
            ]
        else:
            tips = [
                "• Keep It Up: Your blood sugar levels are currently in a healthy range.",
                "• Fiber: Focus on high-fiber foods to maintain steady insulin levels.",
                "• Checkups: Perform a fasting glucose test annually.",
                "• Weight: Maintain a healthy BMI (18.5-24.9)."
            ]
        
    return status, reasons, tips


def get_lifestyle_advice(prediction, input_data, probabilities):
    """
    input_data order: HighBP, HighChol, BMI, Smoker, PhysActivity, 
    Fruits, Veggies, HvyAlcohol, GenHlth, MentHlth
    """
    high_bp = input_data[0]
    high_chol = input_data[1]
    bmi = input_data[2]
    smoker = input_data[3]
    phys_act = input_data[4]
    fruits = input_data[5]
    veggies = input_data[6]
    alcohol = input_data[7]
    gen_health = input_data[8]
    
    reasons = []
    tips = []

    # 1. Logic for Explanations
    if high_bp == 1:
        reasons.append("❗ Hypertension: Your history of high blood pressure significantly raises your metabolic risk.")
    
    if high_chol == 1:
        reasons.append(" High Cholesterol: Elevated lipids can interfere with metabolic health.")
    
    if bmi > 30:
        reasons.append(f" BMI ({bmi}): Obesity is a leading driver of Type 2 Diabetes.")
    elif bmi > 25:
        reasons.append(f" BMI ({bmi}): Being overweight increases your risk of developing diabetes.")
    
    if smoker == 1:
        reasons.append(" Smoking: Nicotine can increase blood sugar levels and lead to insulin resistance.")
    
    if alcohol == 1:
        reasons.append(" Alcohol Consumption: Heavy drinking can cause chronic inflammation of the pancreas.")
    
    if phys_act == 0:
        reasons.append(" Physical Inactivity: Lack of exercise increases diabetes risk.")
    
    if fruits == 0 or veggies == 0:
        reasons.append(" Poor Diet: Limited fruit/vegetable intake affects metabolic health.")
    
    if gen_health >= 4:
        reasons.append(" General Health: Self-reported poor health correlates with higher diabetes risk.")

    # 2. Logic for Recommendations
    if prediction == 2.0:
        # DIABETIC
        status = f" DIABETIC (High Risk - {probabilities[2]:.1f}% Match)"
        tips = [
            " Medical Consultation: You should seek professional medical advice for a diagnostic screening.",
            " Lifestyle Change: If you smoke, consider a cessation program to improve insulin sensitivity.",
            " Diet: Minimize intake of 'white' carbohydrates (white bread, white rice, sugar).",
            " Hydration: Replace all sugary drinks and sodas with water.",
            " Treatment: Discuss medication options with your healthcare provider.",
            " Monitoring: Begin tracking your blood sugar levels regularly."
        ]
        
        if not reasons:
            reasons.append("Your lifestyle factors indicate a high probability of diabetes.")
            
    elif prediction == 1.0:
        # PRE-DIABETIC
        status = f" PRE-DIABETIC (Moderate Risk - {probabilities[1]:.1f}% Match)"
        tips = [
            " Warning: This stage is often reversible with immediate lifestyle changes!",
            " Movement: Increase physical activity. Strength training twice a week can improve glucose uptake.",
            " Diet: Double your intake of green leafy vegetables.",
            " Weight Loss: Losing even 5-7% of body weight can reduce pre-diabetes risk by 50%.",
            " Monitoring: Get your blood sugar tested every 3-6 months.",
            " Exercise: Aim for 150 minutes of moderate activity per week."
        ]
        
        if not reasons:
            reasons.append("Your lifestyle patterns suggest you're at moderate risk for developing diabetes.")
            
    else:
        # HEALTHY
        status = f"✅ HEALTHY (Low Risk - {probabilities[0]:.1f}% Match)"
        if not reasons:
            reasons.append("Your lifestyle choices suggest a low current risk for diabetes.")
        # NEW SMART LOGIC: Check for risk factors even if result is Healthy
        if bmi > 30 or smoker == 1 or high_bp == 1:
            tips = [
                "⚠️ Precaution: Although the model classifies you as healthy, your specific risk factors (BMI/Smoking/BP) are high.",
                "• Weight: Aiming to reduce your BMI toward 24.9 will keep you in this healthy category.",
                "• Smoking: Quitting now will significantly improve your long-term insulin sensitivity.",
                "• Prevention: Schedule a fasting glucose test annually to ensure you remain in the healthy range.",
                "• Activity: Increase daily movement to counteract high-risk factors."
            ]
        else:
            tips = [
                "• Keep It Up: Your lifestyle habits are currently providing strong protection.",
                "• Sleep: Ensure 7-9 hours of quality sleep to maintain healthy glucose metabolism.",
                "• Nutrition: Continue with a balanced diet rich in fiber and whole foods.",
                "• Exercise: Maintain regular physical activity to keep your metabolism strong.",
                "• Checkups: Annual health checkups are the best way to catch changes early."
            ]
        
    return status, reasons, tips