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
        "Precautions": [
            "Maintain good hygiene",
            "Avoid smoking",
            "Use vitamin-enriched skin products"
        ],
        "Foods to Eat": [
            "Carrots",
            "Sweet potatoes",
            "Spinach",
            "Apricots",
            "Liver"
        ]
    },
    "Vitamin_B12": {
        "Diseases": ["Anemia", "Fatigue", "Nerve damage"],
        "Precautions": [
            "Regular check-ups",
            "Avoid alcohol",
            "Consider supplements if vegetarian"
        ],
        "Foods to Eat": [
            "Meat",
            "Fish",
            "Eggs",
            "Dairy products",
            "Fortified cereals"
        ]
    },
    "Vitamin_C": {
        "Diseases": ["Scurvy", "Bleeding gums", "Weakened immunity"],
        "Precautions": [
            "Avoid smoking",
            "Minimize stress",
            "Eat fresh fruits and vegetables"
        ],
        "Foods to Eat": [
            "Oranges",
            "Strawberries",
            "Bell peppers",
            "Broccoli",
            "Kiwi"
        ]
    },
    "Vitamin_D": {
        "Diseases": ["Rickets", "Bone pain", "Muscle weakness"],
        "Precautions": [
            "Get sunlight exposure",
            "Maintain calcium levels",
            "Take supplements if needed"
        ],
        "Foods to Eat": [
            "Fatty fish",
            "Fortified milk",
            "Eggs",
            "Mushrooms"
        ]
    },
    "Vitamin_E": {
        "Diseases": ["Nerve damage", "Muscle weakness", "Vision issues"],
        "Precautions": [
            "Avoid excessive fat restriction",
            "Include antioxidants in diet"
        ],
        "Foods to Eat": [
            "Nuts",
            "Seeds",
            "Spinach",
            "Sunflower oil",
            "Avocados"
        ]
    },
    "Vitamin_K": {
        "Diseases": ["Bleeding disorders", "Weak bones"],
        "Precautions": [
            "Avoid prolonged use of antibiotics",
            "Ensure a balanced diet"
        ],
        "Foods to Eat": [
            "Leafy greens",
            "Broccoli",
            "Brussels sprouts",
            "Parsley",
            "Fish oil"
        ]
    },
}

# Initialize session state for page navigation and data storage
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        "name": "",
        "age": "",
        "gender": "",
        "day_inputs": ["", "", "", "", ""]
    }

# Page 1: Enter Name, Age, and Gender
if st.session_state.page == 1:
    st.title("HealthBuddy")
    st.subheader("Welcome! Let's start with your details.")
    name = st.text_input("Enter your name:")
    age = st.text_input("Enter your age:")
    gender = st.selectbox("Select your gender:", ["", "Male", "Female", "Other"])

    if st.button("Next"):
        st.session_state.user_data["name"] = name
        st.session_state.user_data["age"] = age
        st.session_state.user_data["gender"] = gender
        st.session_state.page = 2

# Page 2: Enter Food for Days 1, 2, and 3
elif st.session_state.page == 2:
    st.title("Food Intake - Part 1")
    st.subheader("Enter food names for Day 1, Day 2, and Day 3")
    day_inputs = []
    for i in range(3):
        day_input = st.text_area(f"Day {i+1} Foods (comma-separated):")
        day_inputs.append(day_input)
    
    if st.button("Next"):
        st.session_state.user_data["day_inputs"][:3] = day_inputs
        st.session_state.page = 3

    if st.button("Back"):
        st.session_state.page = 1

# Page 3: Enter Food for Days 4 and 5
elif st.session_state.page == 3:
    st.title("Food Intake - Part 2")
    st.subheader("Enter food names for Day 4 and Day 5")
    day_inputs = []
    for i in range(3, 5):
        day_input = st.text_area(f"Day {i+1} Foods (comma-separated):")
        day_inputs.append(day_input)
    
    if st.button("Next"):
        st.session_state.user_data["day_inputs"][3:] = day_inputs
        st.session_state.page = 4

    if st.button("Back"):
        st.session_state.page = 2

# Page 4: Display Results
elif st.session_state.page == 4:
    st.title("Results")
    st.subheader("Analyzing your vitamin deficiencies...")

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

    most_common_deficiencies = deficiencies_count.most_common(2)
    if most_common_deficiencies:
        for vitamin, _ in most_common_deficiencies:
            st.markdown(f"**{vitamin} Deficiency**")
            st.write(f"Diseases: {', '.join(health_disease_data[vitamin]['Diseases'])}")
            st.write(f"Foods to Eat: {', '.join(health_disease_data[vitamin]['Foods to Eat'])}")
            st.write(f"Precautions: {', '.join(health_disease_data[vitamin]['Precautions'])}")
    else:
        st.write("No deficiencies detected.")

    if st.button("Restart"):
        st.session_state.page = 1
        st.session_state.user_data = {
            "name": "",
            "age": "",
            "gender": "",
            "day_inputs": ["", "", "", "", ""]
        }
