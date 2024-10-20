from flask import Flask, request, jsonify, render_template
import sqlite3
import pandas as pd

app = Flask(__name__)

@app.route('/query', methods=["POST"])
def run_query():
    query = request.json["query"]
    conn = sqlite3.connect('school_db.sqlite')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return jsonify(df.to_dict(orient='records'))

@app.route("/", methods=["GET"])
def home():
    return render_template('index.html', title="Home")

if __name__ == "main":
    app.run(debug=True)