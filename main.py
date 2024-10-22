from flask import Flask, request, render_template, send_file
import sqlite3, json, io
import pandas as pd
from haversine import haversine, Unit

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

@app.route('/export-nearby-schools', methods=["POST"])
def export_nearby_schools():
    try:
        lat = float(request.json["lat"])
        long = float(request.json["long"])  
        if lat < -90 or lat > 90:
            return json.dumps({"error": "Invalid latitude. Must be between -90 and 90."}), 400
        if long < -180 or long > 180:
            return json.dumps({"error": "Invalid longitude. Must be between -180 and 180."}), 400
        target_coor = (lat, long)
        max_distance = float(request.json.get("max_distance", 10))
        conn = sqlite3.connect('db.sqlite')
        query = """
        SELECT 
            school_name,
            education_agency_name,
            location_address_street_1,
            location_address_street_2,
            location_city,
            location_state,
            location_5_digit_zip_code as location_zip,
            county_name,
            grades_offered_lowest,
            grades_offered_highest,
            total_of_free_lunch_and_reducedprice_lunch_eligible,
            total_students_all_grades_includes_ae as total_students,
            total_elementarysecondary_students_excludes_ae as total_elementary,
            latitude,
            longitude
        FROM school_data
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        df['distance'] = df.apply(lambda row: haversine(
            target_coor,
            (float(row['latitude']), float(row['longitude'])),
            unit=Unit.MILES
        ), axis=1)
        nearby_schools = df[df['distance'] <= max_distance].copy()
        nearby_schools = nearby_schools.sort_values('distance')
        nearby_schools['distance'] = nearby_schools['distance'].round(2)
        buffer = io.StringIO()
        nearby_schools.to_csv(buffer, index=False)
        buffer.seek(0)
        bytes_output = io.BytesIO(buffer.getvalue().encode())
        return send_file(bytes_output, as_attachment=True, download_name="export.csv", mimetype="text/csv")
    except Exception as e:
        return json.dumps({"error": str(e)}), 500

@app.route('/find-schools-query', methods=["POST"])
def find_schools_query():
    lat = float(request.json["lat"])
    long = float(request.json["long"])
    if lat < -90 or lat > 90:
        return json.dumps({"error": "Invalid latitude. Must be between -90 and 90."}), 400
    if long < -180 or long > 180:
        return json.dumps({"error": "Invalid longitude. Must be between -180 and 180."}), 400
    target_coor = (lat, long)
    max_distance = float(request.json.get("max_distance", 10))
    conn = sqlite3.connect('db.sqlite')
    query = """
    SELECT 
        school_name,
        education_agency_name,
        location_address_street_1,
        location_address_street_2,
        location_city,
        location_state,
        location_5_digit_zip_code as location_zip,
        county_name,
        grades_offered_lowest,
        grades_offered_highest,
        total_of_free_lunch_and_reducedprice_lunch_eligible,
        total_students_all_grades_includes_ae as total_students,
        total_elementarysecondary_students_excludes_ae as total_elementary,
        latitude,
        longitude
    FROM school_data
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['distance'] = df.apply(lambda row: haversine(
            target_coor,
            (float(row['latitude']), float(row['longitude'])),
            unit=Unit.MILES
        ), axis=1)
    nearby_schools = df[df['distance'] <= max_distance].copy()
    nearby_schools = nearby_schools.sort_values('distance')
    nearby_schools['distance'] = nearby_schools['distance'].round(2)
    return json.dumps(nearby_schools.to_dict(orient='records'))

@app.route("/", methods=["GET"])
def home():
    return render_template('index.html', title="Home")

@app.route("/find-schools", methods=["GET"])
def find_schools_page():
    return render_template('find-schools.html', title="Find Schools")

if __name__ == "__main__":
    app.run(debug=True)