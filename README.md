# Student Placement Prediction System

> An end-to-end Machine Learning application that predicts student placement outcomes using academic performance, internships, projects, certifications, aptitude scores and soft skills.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-purple)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red)
![License](https://img.shields.io/badge/License-MIT-green)

## Project Overview

Campus placement decisions depend on multiple academic, technical and extracurricular factors. Understanding how these factors influence placement can help students identify areas for improvement and enable institutions to provide targeted guidance.

This project develops an end-to-end machine learning pipeline that predicts placement outcomes using historical student data. The workflow includes data preprocessing, exploratory data analysis, feature engineering, model training, evaluation and deployment through an interactive Streamlit application.

## Live Demo

🚀 **Try the deployed application here:**

**🔗 Live Demo:** https://studentplacementprediction-system.streamlit.app/

The web application allows users to:

- Predict a student's placement status in real time.
- View the probability of placement.
- Enter academic, aptitude, internship, project, certification, and extracurricular details through an intuitive interface.
- Receive instant predictions powered by the trained machine learning model.


## Features

- Exploratory Data Analysis (EDA)
- Data preprocessing pipeline
- Feature scaling using StandardScaler
- Categorical encoding
- Stratified train-test split
- Multiple ML algorithms
- Hyperparameter tuning with GridSearchCV
- 5-fold Cross Validation
- ROC-AUC evaluation
- Feature Importance Analysis
- Interactive Streamlit Web Application


## Machine Learning Pipeline

Data Collection

↓

Data Cleaning

↓

Exploratory Data Analysis

↓

Feature Engineering

↓

Data Preprocessing

↓

Model Training

↓

Hyperparameter Optimization

↓

Model Evaluation

↓

Prediction


```text
Student_Placement_Prediction
│
├── data
│   ├── raw
│   └── processed
│
├── notebooks
│
├── images
│
├── models
│
├── app.py
│
├── requirements.txt
│
└── README.md
```

## Model Performance

Three machine learning models were trained and evaluated to identify the most suitable model for predicting student placement.

| Model | Accuracy | ROC-AUC |
|:------|---------:|---------:|
| **Logistic Regression** | **81.0%** | **0.884** |
| Decision Tree | 72.0% | 0.710 |
| Random Forest | 79.0% | 0.867 |

> **Final Model:** Logistic Regression was selected for deployment as it achieved the highest ROC-AUC while providing the best balance between accuracy and generalization.

---

## Cross-Validation

To evaluate the model's stability and generalization capability, **5-Fold Cross Validation** was performed.

| Fold | Accuracy |
|------|---------:|
| Fold 1 | 79.35% |
| Fold 2 | 79.60% |
| Fold 3 | 81.20% |
| Fold 4 | 79.45% |
| Fold 5 | 80.40% |

**Average Cross-Validation Accuracy:** **80.0%**

This demonstrates that the model performs consistently across different subsets of the dataset and is not dependent on a single train-test split.

---

## Hyperparameter Tuning

Hyperparameter tuning was performed using **GridSearchCV** to optimize the Logistic Regression model.

| Hyperparameter | Best Value |
|---------------|-----------:|
| Regularization Parameter (`C`) | **1** |

The tuned model produced performance similar to the default Logistic Regression model, confirming that the default configuration was already optimal for this dataset.

---

## Threshold Tuning

The default classification threshold for Logistic Regression is **0.5**. Since the objective was to identify as many eligible students as possible, the decision threshold was also evaluated at **0.4**.

| Threshold | Accuracy | Recall (Placed) | False Negatives |
|-----------|---------:|----------------:|----------------:|
| **0.5** | **81%** | **78%** | **188** |
| **0.4** | **79%** | **83%** | **143** |

### Key Observation

Lowering the classification threshold from **0.5** to **0.4**:

- Increased **Recall** for the *Placed* class from **78%** to **83%**
- Reduced **False Negatives** from **188** to **143**
- Slightly reduced overall accuracy from **81%** to **79%**

This trade-off was considered acceptable because correctly identifying students who are likely to be placed was prioritized over maximizing overall accuracy.

---

## Confusion Matrix (Threshold = 0.5)

| | Predicted: Not Placed | Predicted: Placed |
|---|---:|---:|
| **Actual: Not Placed** | **966** | **195** |
| **Actual: Placed** | **188** | **651** |

### Classification Report

| Class | Precision | Recall | F1-Score |
|------|----------:|--------:|----------:|
| Not Placed | 0.84 | 0.83 | 0.83 |
| Placed | 0.77 | 0.78 | 0.77 |

**Overall Accuracy:** **81%**

---

## Confusion Matrix (Threshold = 0.4)

| | Predicted: Not Placed | Predicted: Placed |
|---|---:|---:|
| **Actual: Not Placed** | **893** | **268** |
| **Actual: Placed** | **143** | **696** |

### Classification Report

| Class | Precision | Recall | F1-Score |
|------|----------:|--------:|----------:|
| Not Placed | 0.86 | 0.77 | 0.81 |
| Placed | 0.72 | 0.83 | 0.77 |

**Overall Accuracy:** **79%**

---

## Correlation Analysis

Feature correlation analysis was performed to understand the relationship between input features and the target variable.

### Key Insights

- 📌 **Aptitude Test Score** showed the strongest positive correlation with Placement Status (**0.52**).
- 📌 **HSC Marks (0.51)** and **Projects (0.48)** were also strong indicators of placement.
- 📌 **CGPA (0.42)** and **Soft Skills Rating (0.43)** demonstrated moderate positive influence.
- 📌 No pair of features exhibited extremely high correlation, indicating **low multicollinearity** and making the dataset suitable for Logistic Regression.

---

## Project Highlights

- Developed an **end-to-end Student Placement Prediction System** using **Python, Scikit-learn, and Streamlit**.
- Trained and compared **Logistic Regression, Decision Tree, and Random Forest** models.
- Achieved **81% Accuracy** and **0.884 ROC-AUC** using Logistic Regression.
- Performed **5-Fold Cross Validation** to validate model robustness.
- Applied **GridSearchCV** for hyperparameter optimization.
- Improved **Recall** for the *Placed* class from **78%** to **83%** through decision threshold tuning.
- Reduced **False Negatives** by **24%** (188 → 143), improving identification of students likely to be placed.
- Built and deployed an interactive **Streamlit dashboard** featuring:
  - Probability-based prediction
  - Interactive visualizations
  - SHAP-based explainability
  - Personalized placement recommendations
  - Downloadable prediction reports

## Dashboard & Prediction

<p align="center">
<img src="Streamlit_Images/dashboard.png" width="48%">
<img src="Streamlit_Images/prediction.png" width="48%">
</p>

## Analytics & Recommendations

<p align="center">
<img src="Streamlit_Images/analytics.png" width="48%">
<img src="Streamlit_Images/recommendations.png" width="48%">
</p>

## Future Improvements

- Deep Learning models
- Automated feature engineering
- Real-time database integration
- Resume-based placement prediction


## Author

Mohammad Salman

B.Tech CSE
IIT (ISM) Dhanbad

LinkedIn :https://www.linkedin.com/in/salman-mohammad-192ba035b?

Email :salmanmohammad14113@gmail.com
