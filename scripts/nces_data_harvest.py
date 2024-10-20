import requests, csv, time, random

def extract_rows(dict_list):
    return [list(item['attributes'].values()) for item in dict_list]

def query_api(offset=0):
    url = f"https://nces.ed.gov/opengis/rest/services/K12_School_Locations/EDGE_ADMINDATA_PUBLICSCH_2223/MapServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=LSTATE%20ASC&resultOffset={offset}&resultRecordCount=50"
    try:
        r = requests.get(url)
        return r.json()
    except requests.RequestException as e:
        print(f"Error querying api: {e}")
        return None

def write_data(output_file):
    loop_count = 0
    max_size = 50
    total_records = 0
    try:
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            r_headers = query_api(offset=0)
            if r_headers is None:
                return
            headers = list(r_headers["fieldAliases"].values())
            writer.writerow(headers)
            while True:
                api_offset = loop_count * max_size
                r_data = query_api(api_offset)
                if r_data is None:
                    break
                data_row = r_data['features']
                cell_rows = extract_rows(data_row)
                writer.writerows(cell_rows)
                csvfile.flush()
                records_written = len(data_row)
                total_records += records_written
                print(f"Wrote {records_written} records. Total records: {total_records}")
                loop_count += 1
                random_num = random.randint(2,5)
                time.sleep(random_num)
                if records_written < max_size:
                    break
        print(f"Complete. Total records written: {total_records}")
    except IOError as e:
        print(f"Error writing to file: {e}")
        
write_data("school_data.csv")