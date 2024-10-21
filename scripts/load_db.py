import pandas as pd
import sqlite3
import pathlib
ROOT_DIR = pathlib.Path(__file__).parent.resolve()

def snake_case(word):
    return word.strip().lower().replace(" ", "_")

def seed_data(csv_file, db_file, table_name):
    df = pd.read_csv(csv_file)
    df.columns = [snake_case(col) for col in df.columns]
    print("New column names:")
    print(df.columns.tolist())
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    
def main():
    try:
        seed_data("../csvs/school_data.csv", "../db.sqlite", "school_data")
        print("loaded csv to database")
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    main()