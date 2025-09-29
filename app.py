from flask import Flask, jsonify
import mysql.connector
import os

app = Flask(__name__)

# Ambil konfigurasi database dari environment variable
DB_HOST = os.getenv("DB_HOST", "10.1.10.14")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASS = os.getenv("DB_PASS", "AppPass123")
DB_NAME = os.getenv("DB_NAME", "testdb")

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route("/")
def hello():
    return "Tes Python dan MySQL"

@app.route("/users")
def get_users():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Cannot connect to database"}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM users;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
