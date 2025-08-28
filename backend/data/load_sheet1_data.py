import pandas as pd
import psycopg2
from psycopg2 import sql

# ---------------- config ----------------
config = {
    'excel_file': 'dummy_errors_40.xlsx',   
    'sheet_name': 'Sheet1',                 
    'db_name': 'internship_data',
    'db_user': 'postgres',
    'db_password': 'mitisha1',             
    'db_host': 'localhost',
    'db_port': '5432',
    'table_name': 'sheet1_errors'
}

# Columns in the Excel 
REQUIRED_COLS = [
    'error_description',
    'category',
    'customer_overview_type',
    'error_date',
    'error_count'
]

def load_excel_data():
    
    print(f"Reading {config['excel_file']} -> {config['sheet_name']} ...")
    df = pd.read_excel(config['excel_file'], sheet_name=config['sheet_name'], header=0)

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise KeyError(f"Missing expected columns in Excel: {missing}")

    df = df[REQUIRED_COLS].copy()

    
    df['error_count'] = pd.to_numeric(df['error_count'], errors='coerce')
   
    df['error_date'] = pd.to_datetime(df['error_date'], errors='coerce').dt.date

   
    df.dropna(subset=['error_description', 'category', 'customer_overview_type', 'error_date', 'error_count'], inplace=True)

    
    df['error_count'] = df['error_count'].astype(int)

    print(f"Prepared {len(df)} rows to insert.")
    print(df.head())
    return df

def connect_to_db():
   
    print("Connecting to PostgreSQL ...")
    return psycopg2.connect(
        dbname=config['db_name'],
        user=config['db_user'],
        password=config['db_password'],
        host=config['db_host'],
        port=config['db_port']
    )

def insert_data(conn, data: pd.DataFrame):
    
    cols = REQUIRED_COLS 
    query = sql.SQL("""
        INSERT INTO {} ({})
        VALUES ({})
    """).format(
        sql.Identifier(config['table_name']),
        sql.SQL(', ').join(map(sql.Identifier, cols)),
        sql.SQL(', ').join(sql.Placeholder() * len(cols))
    )

    records = [tuple(row) for row in data[cols].itertuples(index=False, name=None)]

    try:
        with conn.cursor() as cur:
            print(f"Inserting {len(records)} records ...")
            cur.executemany(query, records)
        conn.commit()
        print("Data inserted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Insert failed: {e}")
        raise

def main():
    conn = None
    try:
        df = load_excel_data()
        conn = connect_to_db()
        insert_data(conn, df)
    except Exception as e:
        print(f"Process failed: {e}")
    finally:
        if conn:
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    main()
