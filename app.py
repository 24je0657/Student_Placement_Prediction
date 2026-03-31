import streamlit as st 
import joblib

st.title("Student Placement Prediction System")
st.write("Enter Student details below:")


#input fields
cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, step=0.01)
internship_experience = st.number_input("Number Of Internships", min_value=0, max_value=10, step=1)
projects_completed = st.number_input("Number Of Projects Completed", min_value=0, max_value=10, step=1) 
workshops_attended = st.number_input("Number Of Workshops Attended", min_value=0, max_value=10, step=1)
aptitude_score = st.number_input("Aptitude Score", min_value=0, max_value=100, step=1)
softskills_rating = st.number_input("Soft Skills Rating", min_value=0, max_value=5, step=1)
extracurricular_activities = st.selectbox("Extracurricular Activities", ["Yes", "No"])
training = st.selectbox("Placement Training", ["Yes", "No"])
ssc=st.number_input("SSC Percentage", min_value=0.0, max_value=100.0, step=0.01)
hsc=st.number_input("HSC Percentage", min_value=0.0, max_value=100.0, step=0.01)



st.write("Click the button to predict placement status:")


model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")

if st.button("Predict"):
   
   input_data = [[cgpa,internship_experience,projects_completed,workshops_attended, 
                  aptitude_score, softskills_rating, 1 if extracurricular_activities == "Yes" else 0,
                  1 if training == "Yes" else 0, ssc, hsc]]
   input_data = scaler.transform(input_data)
   prediction = model.predict(input_data)
   probability = model.predict_proba(input_data)[0][1] 
   threshold = 0.4

   if probability >= threshold:
      st.success(f"Placed ✅ (Probability: {probability:.2f})")
      st.balloons()
      st.subheader(" 🎉 Congratulations!")
      st.write(
          "Your Hardwork and dedication have paid off! Your Profile is strong and you have a good chance of being placed. Keep up the great work and continue to build your skills and experience. Best of luck with your placement journey!"
      )

      
   else:
        st.error(f"Not Placed ❌ (Probability: {probability:.2f})")
        st.subheader(" 💪 Don't Give Up!")
        st.write(
            "This result is not the end -- it's just a sign of where to focus next."
            "Many Succesfull People faced setbacks before achieving their goals."
            "You have the ability to turn this around."
        )
