import streamlit as st
import pandas as pd
import nltk
from nltk.corpus import stopwords
import joblib
from collections import Counter

# Download stopwords
nltk.download('stopwords')

# Preprocessing function
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    cleaned_text = ''.join([char.lower() if char.isalpha() or char.isspace() else ' ' for char in text])
    tokens = cleaned_text.split()
    tokens = [word for word in tokens if word not in stop_words]
    abbreviation_mapping = {"CKD": "Cooked", "STMD": "Steamed", "RAW": "Raw"}
    expanded_text = ' '.join([abbreviation_mapping.get(word.upper(), word) for word in tokens])
    return expanded_text

# Load the model
model = joblib.load('healthbuddyapp3.pkl')

# Define nutrients and thresholds
target_names = ['Vitamin_A', 'Vitamin_B12', 'Vitamin_C', 'Vitamin_D', 'Vitamin_E', 'Vitamin_K']
deficiency_thresholds = {
    'Vitamin_A': 15.0,
    'Vitamin_B12': 0.5,
    'Vitamin_C': 10.0,
    'Vitamin_D': 0.5,
    'Vitamin_E': 5.0,
    'Vitamin_K': 2.0,
}

# Define health and disease data
health_disease_data = {
    "Vitamin_A": {
        "Diseases": ["Night blindness", "Dry skin", "Xerophthalmia"],
        "Precautions": ["Maintain good hygiene", "Avoid smoking"],
        "Foods to Eat": ["Carrots", "Sweet potatoes", "Spinach"]
    },
    # Add other vitamins as needed
}

# Streamlit app configuration
st.set_page_config(page_title="HealthBuddy", layout="centered")

# Mobile-friendly CSS for card-based UI
st.markdown("""
    <style>
    body {
        background-color: #f8f9fa;
        font-family: Arial, sans-serif;
    }
    .stApp {
        padding: 0;
        margin: 0;
    }
    .header {
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .header h1 {
        color: #007bff;
        font-size: 36px;
    }
    .header h3 {
        color: #333;
        font-size: 18px;
        margin-top: -10px;
    }
    .card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin: 10px 0;
    }
    .card h4 {
        color: #007bff;
        margin-bottom: 10px;
    }
    .stButton button {
        font-size: 16px;
        width: 100%;
        padding: 12px;
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        border: none;
    }
    .stTextInput input {
        font-size: 14px;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown("<div class='header'><h1>HealthBuddy</h1><h3>Vitamin Deficiency Tracker</h3></div>", unsafe_allow_html=True)

# Input cards for each day
st.markdown("<div class='card'><h4>Enter Food Intake</h4>", unsafe_allow_html=True)
day_inputs = []
for i in range(1, 6):
    day_inputs.append(st.text_input(f"Day {i} Foods (comma-separated):", key=f"day_{i}_input"))
st.markdown("</div>", unsafe_allow_html=True)

# Analysis function
def analyze_all_days(day_inputs):
    deficiencies_count = Counter()
    for day_num, day_input in enumerate(day_inputs, 1):
        food_names = [preprocess_text(food.strip()) for food in day_input.split(',') if food.strip()]
        if food_names:
            try:
                predictions = model.predict(food_names)
            except:
                predictions = [[0.0] * len(target_names)] * len(food_names)
            for i, food in enumerate(food_names):
                food_predictions = dict(zip(target_names, predictions[i]))
                deficiencies = [
                    nutrient for nutrient, value in food_predictions.items()
                    if value < deficiency_thresholds.get(nutrient, float('inf'))
                ]
                deficiencies_count.update(deficiencies)
    
    # Display results
    st.markdown("<div class='card'><h4>Results</h4>", unsafe_allow_html=True)
    most_common_deficiencies = deficiencies_count.most_common(2)
    if most_common_deficiencies:
        for vitamin, _ in most_common_deficiencies:
            st.markdown(f"<strong>{vitamin} Deficiency</strong>", unsafe_allow_html=True)
            st.markdown(f"<strong>Diseases:</strong> {', '.join(health_disease_data[vitamin]['Diseases'])}", unsafe_allow_html=True)
            st.markdown(f"<strong>Foods to Eat:</strong> {', '.join(health_disease_data[vitamin]['Foods to Eat'])}", unsafe_allow_html=True)
            st.markdown(f"<strong>Precautions:</strong> {', '.join(health_disease_data[vitamin]['Precautions'])}", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
    else:
        st.markdown("No deficiencies detected.")
    st.markdown("</div>", unsafe_allow_html=True)

# Analyze button
if st.button("Analyze All Days"):
    analyze_all_days(day_inputs)
