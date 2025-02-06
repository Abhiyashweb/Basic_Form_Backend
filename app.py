from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app, origins=["http://localhost:4200"])

# Configure MySQL connection using PyMySQL
db = pymysql.connect(
    host="localhost",
    port=3306,  
    user="root",
    password="abhi@0024",
    database="form_db"
)
cursor = db.cursor()

# Function to fetch results as a dictionary
def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]  # Fetch column names
    rows = cursor.fetchall()  # Fetch all rows
    return [dict(zip(columns, row)) for row in rows]  # Convert to a list of dictionaries

# API to submit form data
@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.json
    sql = "INSERT INTO users (name, address, phone, email) VALUES (%s, %s, %s, %s)"
    values = (data['name'], data['address'], data['phone'], data['email'])
    cursor.execute(sql, values)
    db.commit()
    return jsonify({"message": "Data inserted successfully!"}), 201

# API to retrieve all data
@app.route('/users', methods=['GET'])
def get_users():
    cursor.execute("SELECT * FROM users")
    users = dict_fetchall(cursor)  # Fetch results as a dictionary
    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True)
