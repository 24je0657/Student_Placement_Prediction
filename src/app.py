
# ===========================
# Student Placement Prediction Dashboard
# Requirements:
# pip install streamlit plotly shap matplotlib joblib pandas numpy
# ===========================
import os
import time
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import shap
import matplotlib.pyplot as plt

st.set_page_config(page_title="Student Placement Dashboard",
                   page_icon="🎓",
                   layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
.main {background:#f5f7fb;}
.block-container {padding-top:1rem;}
.card{
background:white;
padding:18px;
border-radius:12px;
box-shadow:0 2px 10px rgba(0,0,0,.1);
}
h1,h2,h3{color:#0b5394;}
</style>
""", unsafe_allow_html=True)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
model=joblib.load(os.path.join(BASE_DIR,"..","models","model.pkl"))
scaler=joblib.load(os.path.join(BASE_DIR,"..","models","scaler.pkl"))

feature_names=[
"CGPA","Internships","Projects","Workshops",
"Aptitude","Soft Skills","Extra Activities",
"Placement Training","SSC","HSC"
]

try:
    explainer=shap.Explainer(model)
except Exception:
    explainer=None

st.sidebar.title("🎓 Placement Dashboard")
st.sidebar.success("Machine Learning Model")
st.sidebar.write("""
**Algorithm:** Logistic Regression

**Scaler:** StandardScaler

Uses academic profile and skills to estimate placement probability.
""")

st.title("🎓 Student Placement Prediction Dashboard")
st.caption("Professional ML Dashboard with Explainable AI")

with st.expander("📋 Enter Student Details", expanded=True):
    c1,c2=st.columns(2)
    with c1:
        cgpa=st.number_input("CGPA",0.0,10.0,7.5,0.01)
        internships=st.number_input("Internships",0,10,1)
        projects=st.number_input("Projects",0,10,2)
        workshops=st.number_input("Workshops",0,10,1)
        aptitude=st.slider("Aptitude",0,100,75)
    with c2:
        soft=st.slider("Soft Skills",0.0,5.0,4.0,0.1)
        extra=st.radio("Extracurricular",["Yes","No"],horizontal=True)
        training=st.radio("Placement Training",["Yes","No"],horizontal=True)
        ssc=st.number_input("SSC %",0.0,100.0,85.0,0.1)
        hsc=st.number_input("HSC %",0.0,100.0,82.0,0.1)

if st.button(
    "🚀 Predict Placement",
    use_container_width=True,
    type="primary"
):
    vals=[[cgpa,internships,projects,workshops,aptitude,soft,
           1 if extra=="Yes" else 0,
           1 if training=="Yes" else 0,
           ssc,hsc]]

    raw=np.array(vals)
    scaled=scaler.transform(vals)

    bar=st.progress(0)
    for i in range(100):
        time.sleep(0.005)
        bar.progress(i+1)

    pred=model.predict(scaled)[0]
    prob=model.predict_proba(scaled)[0][1]

    t1,t2,t3=st.tabs(["Prediction","Explainability","Suggestions"])

    with t1:
        c1,c2=st.columns([1,1])

        with c1:
            st.metric("Placement Probability",f"{prob*100:.2f}%")

            gauge=go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob*100,
                title={"text":"Placement Chance"},
                gauge={
                    "axis":{"range":[0,100]},
                    "steps":[
                        {"range":[0,40],"color":"red"},
                        {"range":[40,70],"color":"orange"},
                        {"range":[70,100],"color":"lightgreen"}
                    ]
                }))
            st.plotly_chart(gauge,use_container_width=True)

        with c2:
            radar=go.Figure()
            radar.add_trace(go.Scatterpolar(
                r=[cgpa*10,aptitude,soft*20,projects*10,internships*10],
                theta=["CGPA","Aptitude","Soft Skills","Projects","Internships"],
                fill="toself"))
            radar.update_layout(showlegend=False)
            st.plotly_chart(radar,use_container_width=True)

        if prob>=0.4:
            st.success(f"Likely Placed ✅ ({prob:.2%})")
            st.balloons()
        else:
            st.error(f"Placement probability is low ❌ ({prob:.2%})")

    with t2:
        st.subheader("Feature Values")
        df=pd.DataFrame({"Feature":feature_names,
                         "Value":raw[0]})
        st.dataframe(df,use_container_width=True)

        st.subheader("Input Profile")
        fig=px.bar(df,x="Feature",y="Value")
        st.plotly_chart(fig,use_container_width=True)

        if explainer is not None:
            try:
                sv=explainer(scaled)
                st.subheader("SHAP Waterfall")
                fig1=plt.figure(figsize=(8,5))
                shap.plots.waterfall(sv[0],show=False)
                st.pyplot(fig1)
                plt.close(fig1)

                st.subheader("SHAP Feature Importance")
                fig2=plt.figure(figsize=(8,5))
                shap.plots.bar(sv,show=False)
                st.pyplot(fig2)
                plt.close(fig2)
            except Exception as e:
                st.info(f"SHAP visualization unavailable for this model: {e}")

    with t3:
        st.subheader("Personalized Recommendations")
        if cgpa<8:
            st.warning("Improve CGPA to strengthen your profile.")
        if aptitude<70:
            st.warning("Practice aptitude regularly.")
        if internships<2:
            st.warning("Complete more internships.")
        if projects<3:
            st.warning("Build more projects.")
        if training=="No":
            st.warning("Join placement training.")
        if soft<4:
            st.warning("Improve communication and soft skills.")
        if extra=="No":
            st.info("Participate in extracurricular activities.")

        report=f"""
Student Placement Report

Probability : {prob*100:.2f}%
Prediction : {'Placed' if prob>=0.4 else 'Not Placed'}

CGPA : {cgpa}
Internships : {internships}
Projects : {projects}
Workshops : {workshops}
Aptitude : {aptitude}
Soft Skills : {soft}
SSC : {ssc}
HSC : {hsc}
"""
        st.download_button("📄 Download Report",report,file_name="placement_report.txt")
