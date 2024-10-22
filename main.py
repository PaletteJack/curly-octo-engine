from flask import Flask, request, render_template, send_file
import sqlite3, json, io
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
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    bytes_output = io.BytesIO(buffer.getvalue().encode())
    return send_file(bytes_output, as_attachment=True, download_name="export.csv", mimetype='text/csv')

@app.route('/query', methods=["POST"])
def run_query():
    query = request.json["query"]
    conn = sqlite3.connect('db.sqlite')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return json.dumps(df.to_dict(orient='records'))

@app.route("/", methods=["GET"])
def home():
    return render_template('index.html', title="Home")

if __name__ == "__main__":
    app.run(debug=True)