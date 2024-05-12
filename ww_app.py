import streamlit as st
import requests

# Function to fetch food data from Nutritionix
def fetch_food_data(query):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": st.secrets["NUTRITIONIX"]["APP_ID"],
        "x-app-key": st.secrets["NUTRITIONIX"]["APP_KEY"],
        "x-remote-user-id": "0"
    }
    response = requests.post(url, headers=headers, json={"query": query})
    return response.json()

# Calculate Weight Watchers points
def calculate_points(calories, sat_fat, sugar, protein):
    points = (calories / 33) + (sat_fat / 9) + (sugar / 9) - (protein / 10)
    return round(points, 1)

# Streamlit app layout
st.title(':pie: Weight Watchers PyCalc :pie:')

# Food search
food_query = st.text_input('Enter a food name to search:')
initial_values = {
    'calories': 0,
    'sat_fat': 0.0,
    'sugar': 0.0,
    'protein': 0.0
}

if food_query:
    food_data = fetch_food_data(food_query)
    if 'foods' in food_data:
        # Create a selectbox with the names of the foods including serving details
        food_options = {
            f"{item['food_name']} ({item['serving_unit']}, {item['serving_weight_grams']}g/{item['serving_weight_grams']/28:.2f}oz)": item
            for item in food_data['foods']
        }
        selected_food = st.selectbox('Select a food:', list(food_options.keys()))

        # Update initial values based on selected food
        if selected_food:
            food_details = food_options[selected_food]
            initial_values['calories'] = food_details.get('nf_calories', 0)
            initial_values['sat_fat'] = food_details.get('nf_saturated_fat', 0.0)
            initial_values['sugar'] = food_details.get('nf_sugars', 0.0)
            initial_values['protein'] = food_details.get('nf_protein', 0.0)
    else:
        st.error("Failed to fetch data. Please check the food name or try another query.")

# Display the input fields with initial values
calories = st.number_input('Enter calories:', min_value=0, value=int(initial_values['calories']))
sat_fat = st.number_input('Enter saturated fat (grams):', min_value=0.0, value=float(initial_values['sat_fat']), format='%.1f')
sugar = st.number_input('Enter sugar (grams):', min_value=0.0, value=float(initial_values['sugar']), format='%.1f')
protein = st.number_input('Enter protein (grams):', min_value=0.0, value=float(initial_values['protein']), format='%.1f')

# Button to calculate points
if st.button('Calculate Points'):
    points = calculate_points(calories, sat_fat, sugar, protein)
    st.subheader(f'The Weight Watchers points for this food are: {points}')

# Copyright and creator info
st.markdown("""
<footer style='text-align: center; color: gray; font-size: small'>
    &copy; 2024 Weight Watchers PyCalc. All rights reserved. <br>
    Created by Chris K.
</footer>
""", unsafe_allow_html=True)
