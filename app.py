from flask import Flask, render_template, request, jsonify, redirect
import csv
from model import chat
import json
import os
app = Flask(__name__)

chat_history = []
print(os.listdir())
# Display home page
@app.route('/')
def home():
    return render_template('index.html')

# Display login page
@app.route('/login')
def login():
    return render_template('login.html')

# Process login form submission
@app.route('/process_login', methods=['POST','GET'])
def process_login():
    username = request.form['username']
    password = request.form['password']

    # Validate credentials against CSV data
    if validate_credentials(username, password):
        return redirect('/chatbot')
    else:
        return redirect('/login')

@app.route('/register')  # Add the route for register
def register():
    return render_template('register.html')

# Process registration form submission
@app.route('/process_register', methods=['POST'])
def process_register():
    # Extract form data
    # userid = request.form['userid']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    age = request.form['age']
    gender = request.form['gender']

     # Prepare user data as a dictionary
    user_data = {
        
        'username': username,
        'email': email,
        'password': password,
        'age': age,
        'gender': gender
    }

    # Check if email already exists
    if email_exists(email):
        return redirect('/register')

    # Save user data to CSV file
    save_user_data(user_data)

   

    # Here you can add logic to save the registration data to a database or file

    return redirect('/login')


# Function to save user data to CSV file
def save_user_data(user_data):
    csv_file = 'CSV/user.csv'
    fieldnames = ['username', 'email', 'password', 'age', 'gender']

    # Write user data to CSV file
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Check if file is empty, write headers if needed
        if file.tell() == 0:
            writer.writeheader()

        # Write user data to CSV file
        writer.writerow(user_data)

# Function to validate credentials against CSV data
def validate_credentials(username, password):
    import csv
    with open('CSV/user.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username and row['password'] == password:
                return True
    return False

# Helper function to check if email exists in CSV
def email_exists(email):
    with open('CSV/user.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['email'] == email:
                return True
    return False


@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    chat_history = []
    if request.method == 'GET':
        return render_template('chatbot.html')
    elif request.method == 'POST':
        # Retrieve the user input from the request
        user_input = request.form.get('user-input')

        # Process the user input using the chat module
        bot_response = chat.chatbot(user_input)

        # Append the user input and bot response to the chat history
        chat_history.append({'sender': 'user', 'message': user_input})
        chat_history.append({'sender': 'model', 'message': bot_response})

        # Return the updated chat history
        return jsonify(chat_history=chat_history)
@app.route('/article')
def article():
    return render_template('article.html')
    
@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/video')
def video():
    return render_template('video.html')

@app.route('/flappybird')
def game():
    return render_template('flappy-bird-master/flappyBird.html')


if __name__ == '__main__':
    app.run(debug=True)