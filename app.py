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

# App layout
st.title("HealthBuddy by Praveen")
st.subheader("Analyze your vitamin intake")

# Input for 5 days of food
foods_input = st.text_area("Enter food items for the past 5 days (comma-separated):")

if st.button("Analyze"):
    if foods_input.strip():
        food_names = [preprocess_text(food.strip()) for food in foods_input.split(',') if food.strip()]
        deficiencies_count = Counter()

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
                st.markdown(f"**{vitamin} Deficiency**")
                st.write(f"Diseases: {', '.join(health_disease_data[vitamin]['Diseases'])}")
                st.write(f"Foods to Eat: {', '.join(health_disease_data[vitamin]['Foods to Eat'])}")
                st.write(f"Precautions: {', '.join(health_disease_data[vitamin]['Precautions'])}")
        else:
            st.success("No deficiencies detected. Keep up the good diet!")
    else:
        st.warning("Please enter some food items to analyze.")
