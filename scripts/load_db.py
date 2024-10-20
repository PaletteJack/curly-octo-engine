import pandas as pd
import sqlite3

def seed_data(csv_file, db_file, table_name):
    df = pd.read_csv(csv_file)
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    
def main():
    try:
        seed_data("school_data.csv", "school_db.sqlite", "school_data")
        print("loaded csv to database")
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    main()