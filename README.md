# Student Placement Prediction System

## Overview

This project aims to build a machine learning system to predict whether a student is likely to get placed based on academic performance, technical skills, and other relevant factors. 

The objective is to analyze historical placement data and identify patterns that influence placement outcomes.

---

## Problem Statement

Campus placements are influenced by multiple factors such as:

- CGPA
- Internship experience
- Project work
- Workshop/Certificates
- Technical skills
- Communication ability
- Academic consistency

However, the relationship between these factors and final placement outcomes is often unclear to students.

The goal of this project is to design and implement a **data-driven system** that:

- Analyzes historical student data
- Identifies important features influencing placement
- Predicts the probability of a student getting placed
- Evaluates model performance using appropriate metrics

The system uses **supervised machine learning techniques** to model placement outcomes and provide insights into key factors that impact recruitment decisions.

This project focuses on **interpretability, structured experimentation, and reproducibility** rather than only maximizing model accuracy.

---

## Objectives

- Perform Exploratory Data Analysis (EDA)
- Engineer meaningful features
- Train and evaluate multiple models
- Compare performance using standard metrics
- Analyze limitations and potential biases

---

## Tech Stack

- Python
- Pandas & NumPy
- Matplotlib & Seaborn
- Scikit-learn
- Jupyter Notebook

---

## Results

| Model | Accuracy | ROC-AUC |
|------|------|------|
| Logistic Regression | 0.81 | 0.884 |
| Decision Tree | 0.72 | 0.71 |
| Random Forest | 0.79 | 0.867 |

---

## Key Insights

- Aptitude Test Score is the most important predictor of placement.
- Placement training and extracurricular activities significantly influence placement probability.