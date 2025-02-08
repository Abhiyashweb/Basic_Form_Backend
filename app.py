from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql


app = Flask(__name__)


CORS(app, supports_credentials=True, resources={r"/*": {
    "origins": "http://localhost:4200",  
    "allow_headers": ["Content-Type", "Authorization"],  
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]  
}})


@app.after_request
def apply_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:4200"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"  
    return response


@app.route('/submit', methods=['OPTIONS'])
@app.route('/users', methods=['OPTIONS'])
@app.route('/update/<int:user_id>', methods=['OPTIONS'])
@app.route('/delete/<int:user_id>', methods=['OPTIONS'])
def handle_options(user_id=None):
    return jsonify({"message": "CORS preflight successful"}), 200


db = pymysql.connect(
    host="localhost",
    port=3306,  
    user="root",
    password="abhi@0024",
    database="form_db"
)


def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]  
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        sql = "INSERT INTO users (name, address, phone, email) VALUES (%s, %s, %s, %s)"
        values = (data['name'], data['address'], data['phone'], data['email'])

        with db.cursor() as cursor:
            cursor.execute(sql, values)
            db.commit()

        return jsonify({"message": "Data inserted successfully!"}), 201
    except pymysql.MySQLError as e:
        db.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500


@app.route('/users', methods=['GET'])
def get_users():
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = dict_fetchall(cursor)
        return jsonify(users), 200
    except pymysql.MySQLError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500


@app.route('/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        sql = "UPDATE users SET name=%s, address=%s, phone=%s, email=%s WHERE id=%s"
        values = (data['name'], data['address'], data['phone'], data['email'], user_id)

        with db.cursor() as cursor:
            cursor.execute(sql, values)
            db.commit()

        return jsonify({"message": "User data updated successfully"}), 200
    except pymysql.MySQLError as e:
        db.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500


@app.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        sql = "DELETE FROM users WHERE id=%s"
        with db.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            db.commit()

        return jsonify({"message": "User deleted successfully"}), 200
    except pymysql.MySQLError as e:
        db.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
