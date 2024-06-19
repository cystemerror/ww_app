# Weight Watchers PyCalc

## Introduction
Weight Watchers PyCalc is a Streamlit-based web application that allows users to calculate and log Weight Watchers points for different food items. The app fetches food data from the Nutritionix API and provides functionalities for user authentication, food entry logging, and admin management of user accounts. The app is completely built using Python.

## Features
- **User Authentication**: Users can log in and log out securely.
- **Admin Panel**: Admins can create and edit user accounts.
- **Food Search**: Users can search for food items and get nutritional information.
- **Points Calculation**: Calculates Weight Watchers points based on nutritional information.
- **Food Log**: Users can log their food entries and view their food log within a specified date range.
- **Deletion**: Users can delete individual entries from their food log.

## Installation

### Prerequisites
- Python 3.7 or higher
- MongoDB Atlas account

### Clone the Repository
```bash
git clone https://github.com/yourusername/ww-app.git
cd ww-app
```

### Install Dependencies
Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install the required packages:
```bash
pip install -r requirements.txt
```

### Configuration
1. **MongoDB Atlas**: 
   - Set up a MongoDB cluster on MongoDB Atlas.
   - Obtain your MongoDB connection string.

2. **Secrets**:
   - Create a `secrets.toml` file in the `.streamlit` directory.
   - Add your MongoDB URI and Nutritionix API credentials to the `secrets.toml` file.

```toml
# .streamlit/secrets.toml

[mongodb]
uri = "your_mongodb_connection_string"

[nutritionix]
app_id = "your_nutritionix_app_id"
app_key = "your_nutritionix_app_key"
```

### Running the App
Run the Streamlit app:
```bash
streamlit run app.py
```

## Usage

### Logging In
1. Enter your username and password.
2. Click the "Login" button.

### Admin Panel
1. After logging in as an admin, open the sidebar to access the Admin Panel.
2. Use the "Create User" section to add new users.
3. Use the "Edit User" section to update existing user information.

### Calculating Points
1. Enter a food name in the search bar and select the desired food item from the list.
2. Adjust the nutritional values if necessary.
3. Click the "Calculate Points" button to see the Weight Watchers points for the food item.
4. Optionally, log the food entry.

### Viewing and Managing Food Log
1. Use the date filters to specify the date range for your food log.
2. View the logged food entries in a table.
3. Delete entries using the "Delete" button next to each entry.

## Contributing
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Push to the branch.
5. Create a pull request.

## License
This project is licensed under the MIT License.

## Acknowledgements
- [Streamlit](https://www.streamlit.io/) for the web app framework.
- [Nutritionix](https://www.nutritionix.com/) for the food data API.
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) for the database hosting.

## Contact
For any questions or suggestions, feel free to open an issue or contact the repository owner.


