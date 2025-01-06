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
    # Add other vitamins as per the original data...
}

# Streamlit app
st.set_page_config(page_title="HealthBuddy", layout="centered")

# Mobile-friendly CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
        font-family: Arial, sans-serif;
    }
    .stTextInput, .stTextArea {
        font-size: 14px;
    }
    .stButton button {
        font-size: 16px;
        width: 100%;
        padding: 12px;
        background-color: #007bff;
        color: white;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("HealthBuddy")
st.subheader("Vitamin Deficiency Tracker")
st.write("Track your daily nutrient intake and get recommendations.")

# Collapsible food input
with st.expander("Enter your food intake for each day"):
    day_inputs = []
    for i in range(1, 6):
        day_inputs.append(st.text_input(f"Day {i} Foods (comma-separated):", key=f"day_{i}_input"))

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
    most_common_deficiencies = deficiencies_count.most_common(2)
    if most_common_deficiencies:
        for vitamin, _ in most_common_deficiencies:
            st.write(f"### {vitamin} Deficiency")
            st.markdown(f"**Diseases:** {', '.join(health_disease_data[vitamin]['Diseases'])}")
            st.markdown(f"**Foods to Eat:** {', '.join(health_disease_data[vitamin]['Foods to Eat'])}")
            st.markdown(f"**Precautions:** {', '.join(health_disease_data[vitamin]['Precautions'])}")
            st.markdown("---")
    else:
        st.write("No deficiencies detected.")

# Analyze button
if st.button("Analyze All Days"):
    analyze_all_days(day_inputs)
