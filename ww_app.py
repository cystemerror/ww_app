import streamlit as st

def calculate_points(calories, sat_fat, sugar, protein):
    """
    Calculate Weight Watchers points based on the given nutrients.
    """
    points = (calories / 33) + (sat_fat / 9) + (sugar / 9) - (protein / 10)
    return round(points, 1)

# Streamlit app layout
st.title('Weight Watchers Points Calculator')

calories = st.number_input('Enter calories:', min_value=0, value=0)
sat_fat = st.number_input('Enter saturated fat (grams):', min_value=0.0, value=0.0, format='%.1f')
sugar = st.number_input('Enter sugar (grams):', min_value=0.0, value=0.0, format='%.1f')
protein = st.number_input('Enter protein (grams):', min_value=0.0, value=0.0, format='%.1f')

if st.button('Calculate Points'):
    points = calculate_points(calories, sat_fat, sugar, protein)
    st.subheader(f'The Weight Watchers points for this food are: {points}')
