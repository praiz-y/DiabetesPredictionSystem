import streamlit as st
import pandas as pd
import database as db
from datetime import datetime
import hashlib
import plotly.express as px
import plotly.graph_objects as go

# Initialize the DB
db.init_db()

# --- ADMIN PASSWORD CONFIGURATION ---
ADMIN_PASSWORD_HASH = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password():
    """Returns True if the user entered the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hash_password(st.session_state["password"]) == ADMIN_PASSWORD_HASH:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Enter Admin Password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.info("🔒 This area is restricted to administrators only.")
        st.caption("Default password: admin123")
        return False
    
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Enter Admin Password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    
    else:
        return True


# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Admin Panel - Diabetes Prediction System",
    page_icon="🔐",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .big-metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .big-metric-value {
        font-size: 48px;
        font-weight: bold;
        margin: 10px 0;
    }
    .big-metric-label {
        font-size: 16px;
        opacity: 0.95;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Check password
if not check_password():
    st.stop()

# --- ADMIN PANEL CONTENT ---
st.title("🔐 Admin Panel - Diabetes Prediction System")
st.markdown("---")

# Logout button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🚪 Logout", type="secondary"):
        st.session_state["password_correct"] = False
        st.rerun()

# Get statistics
stats = db.get_statistics()

# Get all data for visualizations
df_clinical_all = db.get_all_clinical_records()
df_lifestyle_all = db.get_all_lifestyle_records()

# Calculate derived metrics with error handling
total_screenings = stats.get('total_clinical', 0) + stats.get('total_lifestyle', 0)

# Calculate non_diabetic_clinical safely
if 'non_diabetic_clinical' in stats:
    non_diabetic_clinical = stats['non_diabetic_clinical']
else:
    non_diabetic_clinical = stats.get('total_clinical', 0) - stats.get('diabetic_clinical', 0)

# Calculate healthy_lifestyle safely
if 'healthy_lifestyle' in stats:
    healthy_lifestyle = stats['healthy_lifestyle']
else:
    healthy_lifestyle = stats.get('total_lifestyle', 0) - stats.get('diabetic_lifestyle', 0) - stats.get('prediabetic_lifestyle', 0)

# High risk count (diabetic from both + pre-diabetic from lifestyle)
high_risk_count = stats.get('diabetic_clinical', 0) + stats.get('diabetic_lifestyle', 0) + stats.get('prediabetic_lifestyle', 0)

# Healthy count (non-diabetic clinical + healthy lifestyle)
healthy_count = non_diabetic_clinical + healthy_lifestyle

# --- LARGE METRIC CARDS AT TOP ---
st.header("📊 Key Performance Metrics")

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

with metric_col1:
    st.markdown(f"""
    <div class="big-metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <div class="big-metric-label">Total Screenings</div>
        <div class="big-metric-value">{total_screenings}</div>
    </div>
    """, unsafe_allow_html=True)

with metric_col2:
    st.markdown(f"""
    <div class="big-metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <div class="big-metric-label">Clinical Assessments</div>
        <div class="big-metric-value">{stats['total_clinical']}</div>
    </div>
    """, unsafe_allow_html=True)

with metric_col3:
    st.markdown(f"""
    <div class="big-metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
        <div class="big-metric-label">Lifestyle Assessments</div>
        <div class="big-metric-value">{stats['total_lifestyle']}</div>
    </div>
    """, unsafe_allow_html=True)

with metric_col4:
    st.markdown(f"""
    <div class="big-metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
        <div class="big-metric-label">High-Risk/Diabetic</div>
        <div class="big-metric-value">{high_risk_count}</div>
    </div>
    """, unsafe_allow_html=True)

with metric_col5:
    st.markdown(f"""
    <div class="big-metric-card" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);">
        <div class="big-metric-label">Healthy Count</div>
        <div class="big-metric-value">{healthy_count}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- VISUALIZATION SECTION ---
st.header("📈 Data Visualizations & Analytics")

# Row 1: Risk Distribution and Assessment Distribution
viz_row1_col1, viz_row1_col2 = st.columns(2)

with viz_row1_col1:
    st.subheader("🎯 Overall Risk Distribution")
    if total_screenings > 0:
        # Combine all assessments into risk categories
        overall_risk_data = pd.DataFrame({
            'Risk Level': ['Healthy', 'Pre-Diabetic', 'Diabetic'],
            'Count': [
                healthy_count,
                stats.get('prediabetic_lifestyle', 0),
                stats.get('diabetic_clinical', 0) + stats.get('diabetic_lifestyle', 0)
            ]
        })
        
        fig_risk_dist = px.pie(
            overall_risk_data,
            values='Count',
            names='Risk Level',
            hole=0.5,
            color='Risk Level',
            color_discrete_map={
                'Healthy': '#4facfe',
                'Pre-Diabetic': '#fee140',
                'Diabetic': '#f5576c'
            }
        )
        fig_risk_dist.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=14
        )
        fig_risk_dist.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_risk_dist, use_container_width=True)
    else:
        st.info("No data available yet")

with viz_row1_col2:
    st.subheader("📊 Assessment Type Distribution")
    if total_screenings > 0:
        assessment_data = pd.DataFrame({
            'Assessment Type': ['Clinical', 'Lifestyle'],
            'Count': [stats.get('total_clinical', 0), stats.get('total_lifestyle', 0)]
        })
        
        fig_assessment_dist = px.pie(
            assessment_data,
            values='Count',
            names='Assessment Type',
            hole=0.5,
            color='Assessment Type',
            color_discrete_map={
                'Clinical': '#667eea',
                'Lifestyle': '#f093fb'
            }
        )
        fig_assessment_dist.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=14
        )
        fig_assessment_dist.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_assessment_dist, use_container_width=True)
    else:
        st.info("No data available yet")

# Row 2: Clinical vs Lifestyle Risk Breakdown
st.subheader("🔍 Detailed Risk Breakdown by Assessment Type")
breakdown_col1, breakdown_col2 = st.columns(2)

with breakdown_col1:
    st.markdown("**Clinical Assessment Breakdown**")
    if stats.get('total_clinical', 0) > 0:
        clinical_breakdown = pd.DataFrame({
            'Status': ['Non-Diabetic', 'Diabetic'],
            'Count': [non_diabetic_clinical, stats.get('diabetic_clinical', 0)]
        })
        
        fig_clinical_breakdown = px.pie(
            clinical_breakdown,
            values='Count',
            names='Status',
            hole=0.4,
            color='Status',
            color_discrete_map={
                'Non-Diabetic': '#4facfe',
                'Diabetic': '#f5576c'
            }
        )
        fig_clinical_breakdown.update_traces(textposition='inside', textinfo='percent+label')
        fig_clinical_breakdown.update_layout(height=350, showlegend=True)
        st.plotly_chart(fig_clinical_breakdown, use_container_width=True)
    else:
        st.info("No clinical data yet")

with breakdown_col2:
    st.markdown("**Lifestyle Assessment Breakdown**")
    if stats.get('total_lifestyle', 0) > 0:
        lifestyle_breakdown = pd.DataFrame({
            'Status': ['Healthy', 'Pre-Diabetic', 'Diabetic'],
            'Count': [healthy_lifestyle, stats.get('prediabetic_lifestyle', 0), stats.get('diabetic_lifestyle', 0)]
        })
        
        fig_lifestyle_breakdown = px.pie(
            lifestyle_breakdown,
            values='Count',
            names='Status',
            hole=0.4,
            color='Status',
            color_discrete_map={
                'Healthy': '#4facfe',
                'Pre-Diabetic': '#fee140',
                'Diabetic': '#f5576c'
            }
        )
        fig_lifestyle_breakdown.update_traces(textposition='inside', textinfo='percent+label')
        fig_lifestyle_breakdown.update_layout(height=350, showlegend=True)
        st.plotly_chart(fig_lifestyle_breakdown, use_container_width=True)
    else:
        st.info("No lifestyle data yet")

st.markdown("---")

# Row 3: Glucose vs BMI Scatter Plot
st.subheader("🔬 Glucose vs. BMI Correlation Analysis")
if not df_clinical_all.empty:
    # Create risk level column
    df_clinical_all['Risk Level'] = df_clinical_all['prediction'].apply(
        lambda x: 'Diabetic' if x == 1 else 'Non-Diabetic'
    )
    
    fig_scatter = px.scatter(
        df_clinical_all,
        x='bmi',
        y='glucose',
        color='Risk Level',
        size='age',
        hover_data=['age', 'blood_pressure', 'risk_percentage'],
        color_discrete_map={
            'Non-Diabetic': '#4facfe',
            'Diabetic': '#f5576c'
        },
        title='Patient Clustering: BMI vs Glucose (Size = Age)',
        labels={'bmi': 'Body Mass Index (BMI)', 'glucose': 'Glucose Level (mg/dL)'}
    )
    
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.info("💡 **Insight**: Red dots (Diabetic) clustering in the top-right corner shows high BMI + high glucose correlation with diabetes risk.")
else:
    st.info("No clinical data available for correlation analysis")

st.markdown("---")

# Row 4: Lifestyle Risk Factors
st.subheader("🏃 Lifestyle Risk Factor Frequency")
if not df_lifestyle_all.empty:
    # Calculate frequencies
    lifestyle_factors = {
        'High Blood Pressure': df_lifestyle_all['high_bp'].sum(),
        'High Cholesterol': df_lifestyle_all['high_chol'].sum(),
        'Smoker': df_lifestyle_all['smoker'].sum(),
        'Heavy Alcohol': df_lifestyle_all['heavy_alcohol'].sum(),
        'Low Physical Activity': (df_lifestyle_all['physical_activity'] == 0).sum(),
        'No Daily Fruits': (df_lifestyle_all['fruits'] == 0).sum(),
        'No Daily Vegetables': (df_lifestyle_all['vegetables'] == 0).sum()
    }
    
    lifestyle_df = pd.DataFrame({
        'Risk Factor': list(lifestyle_factors.keys()),
        'Count': list(lifestyle_factors.values())
    }).sort_values('Count', ascending=True)
    
    fig_lifestyle_factors = px.bar(
        lifestyle_df,
        x='Count',
        y='Risk Factor',
        orientation='h',
        color='Count',
        color_continuous_scale='Reds',
        title='Frequency of Lifestyle Risk Factors Among Users'
    )
    
    fig_lifestyle_factors.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_lifestyle_factors, use_container_width=True)
    
    st.info("💡 **Insight**: This shows which lifestyle factors are most common in your user population.")
else:
    st.info("No lifestyle data available for risk factor analysis")

st.markdown("---")

# Row 5: Assessment Timeline
st.subheader("📅 Assessment Timeline & Usage Growth")

timeline_col1, timeline_col2 = st.columns(2)

with timeline_col1:
    st.markdown("**Clinical Assessments Over Time**")
    if stats.get('clinical_trend'):
        trend_df = pd.DataFrame(stats['clinical_trend'], columns=['Date', 'Count'])
        
        fig_clinical_timeline = px.area(
            trend_df,
            x='Date',
            y='Count',
            title='Clinical Assessments (Last 7 Days)',
            labels={'Count': 'Number of Assessments'}
        )
        fig_clinical_timeline.update_traces(
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.3)',
            line_color='#667eea'
        )
        fig_clinical_timeline.update_layout(height=300)
        st.plotly_chart(fig_clinical_timeline, use_container_width=True)
    else:
        st.info("No trend data for the last 7 days")

with timeline_col2:
    st.markdown("**Lifestyle Assessments Over Time**")
    if stats.get('lifestyle_trend'):
        trend_df = pd.DataFrame(stats['lifestyle_trend'], columns=['Date', 'Count'])
        
        fig_lifestyle_timeline = px.area(
            trend_df,
            x='Date',
            y='Count',
            title='Lifestyle Assessments (Last 7 Days)',
            labels={'Count': 'Number of Assessments'}
        )
        fig_lifestyle_timeline.update_traces(
            fill='tozeroy',
            fillcolor='rgba(240, 147, 251, 0.3)',
            line_color='#f093fb'
        )
        fig_lifestyle_timeline.update_layout(height=300)
        st.plotly_chart(fig_lifestyle_timeline, use_container_width=True)
    else:
        st.info("No trend data for the last 7 days")

st.markdown("---")

# Row 6: Age Distribution
st.subheader("👥 Age Distribution of Users")
if not df_clinical_all.empty:
    fig_age_dist = px.histogram(
        df_clinical_all,
        x='age',
        nbins=20,
        color='Risk Level',
        color_discrete_map={
            'Non-Diabetic': '#4facfe',
            'Diabetic': '#f5576c'
        },
        title='Age Distribution of Clinical Assessment Users',
        labels={'age': 'Age (years)', 'count': 'Number of Users'}
    )
    
    fig_age_dist.update_layout(height=400, bargap=0.1)
    st.plotly_chart(fig_age_dist, use_container_width=True)
    
    # Age insights
    age_col1, age_col2, age_col3 = st.columns(3)
    with age_col1:
        st.metric("Average Age", f"{df_clinical_all['age'].mean():.1f} years")
    with age_col2:
        st.metric("Youngest User", f"{df_clinical_all['age'].min()} years")
    with age_col3:
        st.metric("Oldest User", f"{df_clinical_all['age'].max()} years")
    
    st.info("💡 **Insight**: Track if at-risk populations are getting younger, which aligns with medical trends of Type 2 Diabetes in younger adults.")
else:
    st.info("No age data available yet")

st.markdown("---")

# --- MASTER DATA LOG ---
st.header("📋 Master Data Log - Searchable Records")

tab1, tab2 = st.tabs(["📊 Clinical Records", "🏃 Lifestyle Records"])

with tab1:
    st.subheader("Clinical Assessment Records")
    
    if not df_clinical_all.empty:
        # Search functionality
        search_col1, search_col2, search_col3 = st.columns(3)
        
        with search_col1:
            search_id = st.text_input("Search by ID", key="search_clinical_id")
        with search_col2:
            min_glucose = st.number_input("Min Glucose", 0, 300, 0, key="min_gluc")
        with search_col3:
            min_bmi = st.number_input("Min BMI", 0, 100, 0, key="min_bmi")
        
        # Filter data
        filtered_df = df_clinical_all.copy()
        
        if search_id:
            filtered_df = filtered_df[filtered_df['id'].astype(str).str.contains(search_id)]
        if min_glucose > 0:
            filtered_df = filtered_df[filtered_df['glucose'] >= min_glucose]
        if min_bmi > 0:
            filtered_df = filtered_df[filtered_df['bmi'] >= min_bmi]
        
        # Display
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Download
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"clinical_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        st.caption(f"Showing {len(filtered_df)} of {len(df_clinical_all)} records")
    else:
        st.info("No clinical records in database")

with tab2:
    st.subheader("Lifestyle Assessment Records")
    
    if not df_lifestyle_all.empty:
        # Search functionality
        search_col1, search_col2, search_col3 = st.columns(3)
        
        with search_col1:
            search_id_life = st.text_input("Search by ID", key="search_lifestyle_id")
        with search_col2:
            filter_risk = st.selectbox("Filter by Risk", ["All", "Healthy", "Pre-Diabetic", "Diabetic"], key="filter_risk")
        with search_col3:
            min_bmi_life = st.number_input("Min BMI", 0, 100, 0, key="min_bmi_life")
        
        # Filter data
        filtered_df_life = df_lifestyle_all.copy()
        
        if search_id_life:
            filtered_df_life = filtered_df_life[filtered_df_life['id'].astype(str).str.contains(search_id_life)]
        
        if filter_risk != "All":
            filtered_df_life = filtered_df_life[filtered_df_life['risk_class'] == filter_risk]
        
        if min_bmi_life > 0:
            filtered_df_life = filtered_df_life[filtered_df_life['bmi'] >= min_bmi_life]
        
        # Display
        st.dataframe(
            filtered_df_life,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Download
        csv = filtered_df_life.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"lifestyle_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        st.caption(f"Showing {len(filtered_df_life)} of {len(df_lifestyle_all)} records")
    else:
        st.info("No lifestyle records in database")

st.markdown("---")

# --- SETTINGS ---
with st.expander("⚙️ Database Management & Settings"):
    st.warning("⚠️ **Warning:** These actions are irreversible!")
    
    st.markdown("### 🗑️ Clear All Records")
    confirm = st.checkbox("I understand this action cannot be undone")
    
    if confirm:
        if st.button("🗑️ Clear All Records", type="primary"):
            db.clear_all_records()
            st.success("✅ All records have been deleted!")
            st.balloons()
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔐 Change Admin Password")
    st.write("Use the password hash generator below:")
    
    new_pass = st.text_input("Enter new password", type="password", key="new_password")
    if new_pass:
        new_hash = hash_password(new_pass)
        st.code(new_hash, language="text")
        st.info("Copy this hash and replace `ADMIN_PASSWORD_HASH` in admin.py")

st.markdown("---")
st.caption("© 2026 Diabetes Prediction System - Admin Panel")