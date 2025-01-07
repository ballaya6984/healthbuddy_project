import streamlit as st
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

# Vitamin deficiency dataset
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

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'day_inputs' not in st.session_state:
    st.session_state.day_inputs = [""] * 5

# Custom CSS for styling
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
    }
    h1, h2, h3 {
        color: #4CAF50;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Analyze deficiencies
def analyze_deficiencies(day_inputs):
    deficiencies_count = Counter()
    for day_input in day_inputs:
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
    return deficiencies_count

# App logic
st.title("Health Buddy: Vitamin Deficiency Tracker")

if st.session_state.page == 1:
    st.header("Enter your daily food intake: Days 1 to 3")
    for i in range(3):
        st.text_area(f"Day {i+1} Intake:", key=f"day_{i+1}")
    if st.button("Next"):
        for i in range(3):
            st.session_state.day_inputs[i] = st.session_state.get(f"day_{i+1}", "")
        st.session_state.page = 2

elif st.session_state.page == 2:
    st.header("Enter your daily food intake: Days 4 and 5")
    for i in range(3, 5):
        st.text_area(f"Day {i+1} Intake:", key=f"day_{i+1}")
    if st.button("Analyze"):
        for i in range(3, 5):
            st.session_state.day_inputs[i] = st.session_state.get(f"day_{i+1}", "")
        st.session_state.page = 3

elif st.session_state.page == 3:
    st.header("Analysis Results")
    deficiencies_count = analyze_deficiencies(st.session_state.day_inputs)
    if deficiencies_count:
        for vitamin, count in deficiencies_count.items():
            st.subheader(f"{vitamin} Deficiency")
            st.write("Diseases:", ", ".join(health_disease_data[vitamin]["Diseases"]))
            st.write("Precautions:", ", ".join(health_disease_data[vitamin]["Precautions"]))
            st.write("Foods to Eat:", ", ".join(health_disease_data[vitamin]["Foods to Eat"]))
    else:
        st.write("No significant deficiencies detected.")
    if st.button("Restart"):
        st.session_state.page = 1
