import pandas as pd
import sqlite3
import re
import numpy as np

def replace_nulls_with_zero(df):
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
    for col in numeric_columns:
        if df[col].dtype == 'float64' and df[col].notna().all() and (df[col] % 1 == 0).all():
            df[col] = df[col].astype(int)
    return df

def snake_case(word):
    base_word = re.sub(r'[^a-zA-Z0-9\s]', '', word.strip())
    words = base_word.lower().split()
    return '_'.join(words)
    
def seed_data(csv_file, db_file, table_name):
    df = pd.read_csv(csv_file)
    df.columns = [snake_case(col) for col in df.columns]
    df = replace_nulls_with_zero(df)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for column in numeric_columns:
        try:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN temp_{column} NUMERIC DEFAULT 0")
            cursor.execute(f"UPDATE {table_name} SET temp_{column} = {column}")
            cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column}")
            cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN temp_{column} TO {column}")
        except sqlite3.OperationalError as e:
            print(f"Error altering column {column}: {e}")
    conn.commit()
    conn.close()
    print(f"Database created: {db_file}")
    print(f"Table created: {table_name}")
    print(f"Number of rows: {len(df)}")
    print(f"Columns: {', '.join(df.columns)}")
    
def main():
    try:
        seed_data("../csvs/school_data.csv", "../db.sqlite", "school_data")
        print("loaded csv to database")
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    main()