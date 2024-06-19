import streamlit as st
import requests
import pymongo
from pymongo import MongoClient
import hashlib
from datetime import datetime
import pandas as pd
from bson.objectid import ObjectId

# MongoDB setup
mongo_uri = st.secrets["mongodb"]["uri"]
client = MongoClient(mongo_uri)
db = client['ww-app']
users_collection = db['users']
food_logs_collection = db['food_logs']

# Authentication setup
def get_hashed_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == get_hashed_password(provided_password)

def authenticate_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and verify_password(user['password'], password):
        return user['name'], True, username
    return None, False, None

# Function to fetch food data from Nutritionix
def fetch_food_data(query):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": st.secrets["NUTRITIONIX"]["APP_ID"],
        "x-app-key": st.secrets["NUTRITIONIX"]["APP_KEY"],
        "x-remote-user-id": "0"
    }
    response = requests.post(url, headers=headers, json={"query": query}, timeout=300)
    return response.json()

# Calculate Weight Watchers points
def calculate_points(calories, sat_fat, sugar, protein):
    points = (calories / 33) + (sat_fat / 9) + (sugar / 9) - (protein / 10)
    return round(points, 1)

# Streamlit app layout
st.title(':pie: Weight Watchers PyCalc :pie:')

# Initialize session state variables
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'points' not in st.session_state:
    st.session_state.points = None
if 'log_food_button' not in st.session_state:
    st.session_state.log_food_button = False

# Login Section
if st.session_state.authentication_status != True:
    st.subheader("Login")

    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        name, authentication_status, username = authenticate_user(username_input, password_input)
        if authentication_status:
            st.session_state.authentication_status = True
            st.session_state.name = name
            st.session_state.username = username
            st.success(f"Welcome, {name}!")
        else:
            st.session_state.authentication_status = False
            st.error("Username or password is incorrect")
else:
    name = st.session_state.name
    username = st.session_state.username

if st.session_state.authentication_status == True:
    st.button("Logout", on_click=lambda: [st.session_state.update(authentication_status=None), st.rerun()])
    
    if users_collection.find_one({"username": username})["access_level"] == "admin":
        st.sidebar.title("Admin Panel")
        admin_action = st.sidebar.selectbox("Select Action", ["Create User", "Edit User"])

        if admin_action == "Create User":
            new_user_name = st.text_input("Enter name")
            new_user_username = st.text_input("Enter username")
            new_user_password = st.text_input("Enter password", type="password")
            new_user_access_level = st.selectbox("Select access level", ["user", "admin"])
            
            if st.button("Create User"):
                if new_user_name and new_user_username and new_user_password:
                    hashed_password = get_hashed_password(new_user_password)
                    users_collection.insert_one({
                        "name":new_user_name,
                        "username": new_user_username,
                        "password": hashed_password,
                        "access_level": new_user_access_level
                    })
                    st.success("User created successfully!")
                else:
                    st.error("Please fill out all fields")

        elif admin_action == "Edit User":
            existing_users = users_collection.find()
            user_to_edit = st.selectbox("Select user", [user["username"] for user in existing_users])
            if user_to_edit:
                user_details = users_collection.find_one({"username": user_to_edit})
                new_user_name = st.text_input("Enter name", value=user_details["name"])
                new_user_password = st.text_input("Enter new password (leave blank to keep current)", type="password")
                new_user_access_level = st.selectbox("Select access level", ["user", "admin"], index=["user", "admin"].index(user_details["access_level"]))
                
                if st.button("Update User"):
                    updated_values = {
                        "name": new_user_name,
                        "access_level": new_user_access_level
                    }
                    if new_user_password:
                        updated_values["password"] = get_hashed_password(new_user_password)
                    users_collection.update_one({"username": user_to_edit}, {"$set": updated_values})
                    st.success("User updated successfully!")

    st.subheader(f"Welcome, {name}!")
    
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
    
    # Display the input fields with initial values in two columns
    col1, col2 = st.columns(2)

    with col1:
        calories = st.number_input('Enter calories:', min_value=0, value=int(initial_values['calories']))
        sat_fat = st.number_input('Enter saturated fat (grams):', min_value=0.0, value=float(initial_values['sat_fat']), format='%.1f')

    with col2:
        sugar = st.number_input('Enter sugar (grams):', min_value=0.0, value=float(initial_values['sugar']), format='%.1f')
        protein = st.number_input('Enter protein (grams):', min_value=0.0, value=float(initial_values['protein']), format='%.1f')

    # Button to calculate points
    if st.button('Calculate Points'):
        st.session_state.points = calculate_points(calories, sat_fat, sugar, protein)
        st.subheader(f'The Weight Watchers points for this food are: {st.session_state.points}')
        
        # Set session state to show the log food button
        st.session_state.log_food_button = True

    # Display the log food button only after points are calculated
    if st.session_state.log_food_button:
        if st.button('Log Food Entry'):
            if selected_food:
                try:
                    # Ensure selected_food is a string
                    if isinstance(selected_food, str):
                        log_entry = {
                            "username": username,
                            "food_name": selected_food,
                            "calories": calories,
                            "sat_fat": sat_fat,
                            "sugar": sugar,
                            "protein": protein,
                            "points": st.session_state.points,
                            "timestamp": datetime.now()
                        }
                        food_logs_collection.insert_one(log_entry)
                        st.success("Food entry logged successfully!")
                        # Reset the button state
                        st.session_state.log_food_button = False
                    else:
                        st.error("Selected food is not a valid string")
                except Exception as e:
                    st.error(f"An error occurred while logging the food entry: {e}")
            else:
                st.error("No food selected")

    # Display logged food entries
    st.subheader("Your Food Log")
    # Get all logs for the current user
    logs = list(food_logs_collection.find({"username": username}))

    if logs:
        # Convert logs to DataFrame
        log_df = pd.DataFrame(logs)

        # Display date filter in 2 separate columns
        col3, col4 = st.columns(2)

        with col3:
            start_date = st.date_input('Start date', value=datetime.today())
        with col4:
            end_date = st.date_input('End date', value=datetime.today())

        if start_date > end_date:
            st.error("Error: End date must fall after start date.")
        else:
            # Filter the DataFrame by the selected date range
            log_df['date'] = pd.to_datetime(log_df['timestamp']).dt.date
            mask = (log_df['date'] >= start_date) & (log_df['date'] <= end_date)
            filtered_df = log_df.loc[mask]

            if not filtered_df.empty:
                # Display the headers
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write("**Food Name**")
                with col2:
                    st.write("**Points**")
                with col3:
                    st.write("**Date**")
                with col4:
                    st.write("**Delete**")

                for index, row in filtered_df.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.write(f"{row['food_name']}")
                    with col2:
                        st.write(f"{row['points']}")
                    with col3:
                        st.write(f"{row['date']}")
                    with col4:
                        if st.button('Delete', key=f"delete_{index}"):
                            food_logs_collection.delete_one({"_id": row["_id"]})
                            st.rerun()  # Refresh the app to reflect the deletion

                total_points = filtered_df['points'].sum()
                st.write(f"Total Points for the selected date range: {total_points}")
            else:
                st.write("No entries found for the selected date range.")

elif st.session_state.authentication_status == False:
    st.error("Username or password is incorrect")
elif st.session_state.authentication_status == None:
    st.warning("Please enter your username and password")

# Copyright and creator info
st.markdown("""
<footer style='text-align: center; color: gray; font-size: small'>
    &copy; 2024 Weight Watchers PyCalc. All rights reserved. <br>
    Created by Chris K.
</footer>
""", unsafe_allow_html=True)
