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
            "Maintain good hygiene", "Avoid smoking", "Use vitamin-enriched skin products", "Get regular eye exams", "Avoid excessive alcohol consumption"
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
            "Regular check-ups", "Avoid alcohol", "Consider supplements if vegetarian", "Monitor levels of folate and iron", "Get tested if pregnant or elderly"
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
            "Avoid smoking", "Minimize stress", "Eat fresh fruits and vegetables", "Avoid exposure to cold weather", "Consider vitamin C supplements during flu season"
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
            "Get sunlight exposure", "Maintain calcium levels", "Take supplements if needed", "Monitor vitamin D levels during winter months", "Engage in weight-bearing exercises"
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
            "Avoid excessive fat restriction", "Include antioxidants in diet", "Consume healthy fats like nuts and seeds", "Consider supplementing if pregnant or lactating"
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
            "Avoid prolonged use of antibiotics", "Ensure a balanced diet", "Take vitamin K2 supplements if prescribed", "Be cautious with anticoagulant medications"
        ],
        "Foods to Eat": [
            "Leafy greens", "Broccoli", "Brussels sprouts", "Parsley", "Fish oil", "Kale", "Swiss chard", "Green beans", "Cabbage"
        ]
    },
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
    st.title("Welcome to HealthBuddy by Praveen ")
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
