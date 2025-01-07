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
    # Data remains unchanged
}

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {"name": "", "age": "", "day_inputs": [""] * 5}

# Custom CSS for styling
st.markdown(
    """
    <style>
    /* CSS code remains unchanged */
    </style>
    """,
    unsafe_allow_html=True,
)

# Page 1: Enter Name and Age
if st.session_state.page == 1:
    st.markdown("<h1>HealthBuddy</h1>", unsafe_allow_html=True)
    st.subheader("Welcome! Let's get started.")
    name = st.text_input("Enter your name:")
    age = st.text_input("Enter your age:")
    if st.button("Next"):
        if not name.strip() or not age.strip():
            st.error("Please enter both your name and age before proceeding.")
        else:
            st.session_state.user_data["name"] = name
            st.session_state.user_data["age"] = age
            st.session_state.page = 2

# Page 2: Enter Food for Day 1, 2, and 3
elif st.session_state.page == 2:
    st.markdown("<h1>Food Intake - Part 1</h1>", unsafe_allow_html=True)
    st.subheader("Enter food names for Day 1, Day 2, and Day 3")
    day_inputs = []
    incomplete_inputs = False

    for i in range(3):
        day_input = st.text_area(f"Day {i+1} Foods (comma-separated):", key=f"day{i+1}")
        day_inputs.append(day_input)
        if not day_input.strip():  # Check if input is empty
            incomplete_inputs = True

    if st.button("Next"):
        if incomplete_inputs:
            st.error("Please fill out all food entries for Days 1, 2, and 3 before proceeding.")
        else:
            st.session_state.user_data["day_inputs"][:3] = day_inputs
            st.session_state.page = 3

    if st.button("Back"):
        st.session_state.page = 1

# Page 3: Enter Food for Day 4 and 5
elif st.session_state.page == 3:
    st.markdown("<h1>Food Intake - Part 2</h1>", unsafe_allow_html=True)
    st.subheader("Enter food names for Day 4 and Day 5")
    day_inputs = []
    incomplete_inputs = False

    for i in range(3, 5):
        day_input = st.text_area(f"Day {i+1} Foods (comma-separated):", key=f"day{i+1}")
        day_inputs.append(day_input)
        if not day_input.strip():  # Check if input is empty
            incomplete_inputs = True

    if st.button("Next"):
        if incomplete_inputs:
            st.error("Please fill out all food entries for Days 4 and 5 before proceeding.")
        else:
            st.session_state.user_data["day_inputs"][3:] = day_inputs
            st.session_state.page = 4

    if st.button("Back"):
        st.session_state.page = 2

# Page 4: Display Results
elif st.session_state.page == 4:
    st.markdown("<h1>Results</h1>", unsafe_allow_html=True)
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
            st.markdown(f"<div class='result-card'><h3>{vitamin} Deficiency</h3>"
                        f"<p><b>Diseases:</b> {', '.join(health_disease_data[vitamin]['Diseases'])}</p>"
                        f"<p><b>Foods to Eat:</b> {', '.join(health_disease_data[vitamin]['Foods to Eat'])}</p>"
                        f"<p><b>Precautions:</b> {', '.join(health_disease_data[vitamin]['Precautions'])}</p></div>",
                        unsafe_allow_html=True)
    else:
        st.markdown("<p class='result-card'>No deficiencies detected.</p>", unsafe_allow_html=True)
    
    if st.button("Restart"):
        st.session_state.page = 1
        st.session_state.user_data = {"name": "", "age": "", "day_inputs": [""] * 5}
