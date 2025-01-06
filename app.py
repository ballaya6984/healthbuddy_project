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

# Initialize session state for page navigation and data storage
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {"name": "", "age": "", "day_inputs": [""] * 5}

# Page 1: Enter Name and Age
if st.session_state.page == 1:
    st.title("HealthBuddy")
    st.subheader("Welcome! Let's get started.")
    st.text_input("Enter your name:", key="name", on_change=lambda: st.session_state.user_data.update({"name": st.session_state.name}))
    st.text_input("Enter your age:", key="age", on_change=lambda: st.session_state.user_data.update({"age": st.session_state.age}))
    if st.button("Next"):
        st.session_state.page = 2

# Page 2: Enter Food for Day 1, 2, and 3
elif st.session_state.page == 2:
    st.title("Food Intake - Part 1")
    st.subheader("Enter food names for Day 1, Day 2, and Day 3")
    for i in range(3):
        st.text_input(f"Day {i+1} Foods (comma-separated):", key=f"day_{i+1}_input",
                      on_change=lambda i=i: st.session_state.user_data["day_inputs"].__setitem__(i, st.session_state[f"day_{i+1}_input"]))
    if st.button("Next"):
        st.session_state.page = 3
    if st.button("Back"):
        st.session_state.page = 1

# Page 3: Enter Food for Day 4 and 5
elif st.session_state.page == 3:
    st.title("Food Intake - Part 2")
    st.subheader("Enter food names for Day 4 and Day 5")
    for i in range(3, 5):
        st.text_input(f"Day {i+1} Foods (comma-separated):", key=f"day_{i+1}_input",
                      on_change=lambda i=i: st.session_state.user_data["day_inputs"].__setitem__(i, st.session_state[f"day_{i+1}_input"]))
    if st.button("Next"):
        st.session_state.page = 4
    if st.button("Back"):
        st.session_state.page = 2

# Page 4: Display Results
elif st.session_state.page == 4:
    st.title("Results")
    st.subheader("Analyzing your vitamin deficiencies...")
    
    # Analyze deficiencies
    deficiencies_count = Counter()
    for day_num, day_input in enumerate(st.session_state.user_data["day_inputs"], 1):
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

    # Display deficiencies
    most_common_deficiencies = deficiencies_count.most_common(2)
    if most_common_deficiencies:
        for vitamin, _ in most_common_deficiencies:
            st.markdown(f"### {vitamin} Deficiency")
            st.markdown(f"**Diseases:** {', '.join(health_disease_data[vitamin]['Diseases'])}")
            st.markdown(f"**Foods to Eat:** {', '.join(health_disease_data[vitamin]['Foods to Eat'])}")
            st.markdown(f"**Precautions:** {', '.join(health_disease_data[vitamin]['Precautions'])}")
            st.markdown("---")
    else:
        st.write("No deficiencies detected.")
    
    if st.button("Restart"):
        st.session_state.page = 1
        st.session_state.user_data = {"name": "", "age": "", "day_inputs": [""] * 5}
