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
        "Diseases": ["Night blindness", "Dry skin", "Xerophthalmia", "Immune system deficiency", "Poor vision"],
        "Precautions": ["Maintain good hygiene", "Avoid smoking", "Use vitamin-enriched skin products", "Get regular eye exams", "Avoid excessive alcohol consumption"],
        "Foods to Eat": ["Carrots", "Sweet potatoes", "Spinach", "Apricots", "Liver", "Kale", "Red bell peppers", "Butternut squash"]
    },
    # (similar data for other vitamins omitted for brevity)
}

# Analyze deficiencies
def analyze_all_days(day_inputs):
    deficiencies_count = Counter()
    for day_num, day_input in enumerate(day_inputs, 1):
        food_names = [preprocess_text(food.strip()) for food in day_input.split(',') if food.strip()]
        if food_names:
            try:
                predictions = model.predict(food_names)
            except:
                predictions = [[0.0] * len(target_names)] * len(food_names)  # Dummy prediction
            for i, food in enumerate(food_names):
                food_predictions = dict(zip(target_names, predictions[i]))
                deficiencies = [
                    nutrient for nutrient, value in food_predictions.items()
                    if value < deficiency_thresholds.get(nutrient, float('inf'))
                ]
                deficiencies_count.update(deficiencies)
    return deficiencies_count.most_common(2)

# Streamlit app logic
if "page" not in st.session_state:
    st.session_state.page = 1
if "name" not in st.session_state:
    st.session_state.name = ""
if "age" not in st.session_state:
    st.session_state.age = 0
if "day_inputs" not in st.session_state:
    st.session_state.day_inputs = [""] * 5

if st.session_state.page == 1:
    st.title("Welcome to HealthBuddy")
    st.write("Please enter your details to continue:")
    st.session_state.name = st.text_input("Enter your name:")
    st.session_state.age = st.number_input("Enter your age:", min_value=0, max_value=120, step=1)
    if st.button("Next"):
        st.session_state.page = 2

elif st.session_state.page == 2:
    st.title("Food Data Entry")
    st.write("Enter food names for each day (comma-separated):")
    for i in range(5):
        st.session_state.day_inputs[i] = st.text_area(f"Day {i + 1}:", value=st.session_state.day_inputs[i], height=100)
    if st.button("Analyze"):
        st.session_state.page = 3
    if st.button("Back"):
        st.session_state.page = 1

elif st.session_state.page == 3:
    st.title("Analysis Results")
    st.write(f"Hello, {st.session_state.name} (Age: {st.session_state.age})!")
    st.write("Here are your vitamin deficiency analysis results:")
    deficiencies = analyze_all_days(st.session_state.day_inputs)
    if deficiencies:
        for vitamin, _ in deficiencies:
            st.write(f"### {vitamin} Deficiency")
            st.markdown(f"**Diseases:** {', '.join(health_disease_data[vitamin]['Diseases'])}")
            st.markdown(f"**Foods to Eat:** {', '.join(health_disease_data[vitamin]['Foods to Eat'])}")
            st.markdown(f"**Precautions:** {', '.join(health_disease_data[vitamin]['Precautions'])}")
            st.markdown("---")
    else:
        st.write("No deficiencies detected across the 5 days.")
    if st.button("Back"):
        st.session_state.page = 2
