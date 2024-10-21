import pandas as pd
import sqlite3
import re

def snake_case(word):
    base_word = re.sub(r'[^a-zA-Z0-9\s]', '', word.strip())
    words = base_word.lower().split()
    return '_'.join(words)
    
def seed_data(csv_file, db_file, table_name):
    df = pd.read_csv(csv_file)
    df.columns = [snake_case(col) for col in df.columns]
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print("database created")
    
def main():
    try:
        seed_data("../csvs/school_data.csv", "../db.sqlite", "school_data")
        print("loaded csv to database")
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    main()