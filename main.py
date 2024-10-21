from flask import Flask, request, jsonify, render_template, send_file
import sqlite3
import pandas as pd

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

@app.route('/export', methods=["POST"])
def export_csv():
    query = request.json["query"]
    conn = sqlite3.connect('db.sqlite')
    df = pd.read_sql_query(query, conn)
    conn.close()
    csv_file = df.to_csv('query_export.csv', index=False)
    return send_file(csv_file, as_attachment=True, attachment_filename='query_export.csv', mimetype='text/csv')

@app.route('/query', methods=["POST"])
def run_query():
    query = request.json["query"]
    conn = sqlite3.connect('db.sqlite')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return jsonify(df.to_dict(orient='records'))

@app.route("/", methods=["GET"])
def home():
    return render_template('index.html', title="Home")

if __name__ == "__main__":
    app.run(debug=True)