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
        "Diseases": [
            "Night blindness", "Dry skin", "Xerophthalmia", "Immune system deficiency", "Poor vision"
        ],
        "Precautions": [
            "Maintain good hygiene",
            "Avoid smoking",
            "Use vitamin-enriched skin products",
            "Get regular eye exams",
            "Avoid excessive alcohol consumption"
        ],
        "Foods to Eat": [
            "Carrots", "Sweet potatoes", "Spinach", "Apricots", "Liver", "Kale", "Red bell peppers", "Butternut squash"
        ]
    },
    "Vitamin_B12": {
        "Diseases": [
            "Anemia", "Fatigue", "Nerve damage", "Pernicious anemia", "Memory problems", "Pale skin"
        ],
        "Precautions": [
            "Regular check-ups",
            "Avoid alcohol",
            "Consider supplements if vegetarian",
            "Monitor levels of folate and iron",
            "Get tested if pregnant or elderly"
        ],
        "Foods to Eat": [
            "Meat", "Fish", "Eggs", "Dairy products", "Fortified cereals", "Fortified nutritional yeast", "Clams", "Liver"
        ]
    },
    "Vitamin_C": {
        "Diseases": [
            "Scurvy", "Bleeding gums", "Weakened immunity", "Frequent infections", "Dry skin", "Joint pain"
        ],
        "Precautions": [
            "Avoid smoking",
            "Minimize stress",
            "Eat fresh fruits and vegetables",
            "Avoid exposure to cold weather",
            "Consider vitamin C supplements during flu season"
        ],
        "Foods to Eat": [
            "Oranges", "Strawberries", "Bell peppers", "Broccoli", "Kiwi", "Brussels sprouts", "Cauliflower", "Tomatoes", "Cantaloupe"
        ]
    },
    "Vitamin_D": {
        "Diseases": [
            "Rickets", "Bone pain", "Muscle weakness", "Osteomalacia", "Osteoporosis", "Fatigue", "Increased risk of infections"
        ],
        "Precautions": [
            "Get sunlight exposure",
            "Maintain calcium levels",
            "Take supplements if needed",
            "Monitor vitamin D levels during winter months",
            "Engage in weight-bearing exercises"
        ],
        "Foods to Eat": [
            "Fatty fish", "Fortified milk", "Eggs", "Mushrooms", "Fortified orange juice", "Cod liver oil", "Cheese", "Beef liver"
        ]
    },
    "Vitamin_E": {
        "Diseases": [
            "Nerve damage", "Muscle weakness", "Vision issues", "Peripheral neuropathy", "Impaired immune function"
        ],
        "Precautions": [
            "Avoid excessive fat restriction",
            "Include antioxidants in diet",
            "Consume healthy fats like nuts and seeds",
            "Consider supplementing if pregnant or lactating"
        ],
        "Foods to Eat": [
            "Nuts", "Seeds", "Spinach", "Sunflower oil", "Avocados", "Almonds", "Peanut butter", "Olive oil", "Pumpkin seeds"
        ]
    },
    "Vitamin_K": {
        "Diseases": [
            "Bleeding disorders", "Weak bones", "Excessive bruising", "Impaired wound healing", "Osteoporosis", "Hemorrhaging"
        ],
        "Precautions": [
            "Avoid prolonged use of antibiotics",
            "Ensure a balanced diet",
            "Take vitamin K2 supplements if prescribed",
            "Be cautious with anticoagulant medications"
        ],
        "Foods to Eat": [
            "Leafy greens", "Broccoli", "Brussels sprouts", "Parsley", "Fish oil", "Kale", "Swiss chard", "Green beans", "Cabbage"
        ]
    },
}

# Streamlit app
st.title("HealthBuddy Vitamin Deficiency Tracker - Praveen Yaganti")
st.write("Enter up to 5 food names to analyze possible vitamin deficiencies.")

# User input for 5 food items
food_input_1 = st.text_input("Enter food 1:")
food_input_2 = st.text_input("Enter food 2:")
food_input_3 = st.text_input("Enter food 3:")
food_input_4 = st.text_input("Enter food 4:")
food_input_5 = st.text_input("Enter food 5:")

# Collect all food items into a list
food_inputs = [food_input_1, food_input_2, food_input_3, food_input_4, food_input_5]
food_names = [preprocess_text(food.strip()) for food in food_inputs if food.strip()]

if food_names:
    # Predict deficiencies using the model
    with st.spinner('Analyzing food...'):
        try:
            predictions = model.predict(food_names)
        except:
            st.write("Error: The food items may not be recognized by the model. Defaulting to Vitamin A deficiency.")
            predictions = [[0.0] * len(target_names)] * len(food_names)  # Dummy prediction

    deficiencies_for_day = []
    
    for i, food in enumerate(food_names):
        food_predictions = dict(zip(target_names, predictions[i]))
        deficiencies = [
            nutrient for nutrient, value in food_predictions.items()
            if value < deficiency_thresholds.get(nutrient, float('inf'))
        ]
        deficiencies_for_day.extend(deficiencies)

    deficiency_counts = Counter(deficiencies_for_day)

    if deficiency_counts:
        st.write("### Deficiencies Detected:")
        for vitamin, count in deficiency_counts.items():
            # Use card style for each deficiency
            st.markdown(f"""
            <div style="background-color:#f7f7f7; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <h3 style="color:#3c8c8c;">**{vitamin} Deficiency**: {count} occurrence(s)</h3>
                <h4><strong>Diseases:</strong> {', '.join(health_disease_data[vitamin].get('Diseases', ['No data available']))}</h4>
                <h4><strong>Foods to Eat:</strong> {', '.join(health_disease_data[vitamin].get('Foods to Eat', ['No data available']))}</h4>
                <h4><strong>Precautions:</strong> {', '.join(health_disease_data[vitamin].get('Precautions', ['No data available']))}</h4>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No deficiencies detected.")
else:
    st.write("Please enter some food names to analyze.")
