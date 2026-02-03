import pandas as pd
import os
import psycopg2
from psycopg2.extras import execute_values
import logging
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

pg_user = os.getenv('PG_USER')
pg_pass = os.getenv('PG_PASS')
def extract_latest_file():
    prefix = f'extracted/Airbnb_Open_Data.csv'
def transform_data(df):
    missing_vals = ["", " ", "NULL", "null", "Null", "N/A", "n/a", "na", "NaN", "nan", "?", "none", "None"]
    try:
        df.columns = df.columns.str.strip().str.lower().str.replace(r'[\s\-]+','_', regex=True)
        df = df.dropna(axis=1, how='all')
        df = df.dropna(axis=0, how='all')
        df = df.drop_duplicates()
        df = df.replace(missing_vals, pd.NA)

        df['last_review'] = pd.to_datetime(df['last_review'], errors ='coerce')

        for col in df.columns:

            if df[col].dtype == 'object' or df[col].dtype == 'string':
                try:
                    cleaned = df[col].astype(str).str.replace(r'[\$,()\s]','', regex=True)
                    converted = pd.to_numeric(cleaned, errors='coerce')
                    if converted.notna().sum() > 0.9*len(df):
                        df[col] = converted
                    else:
                        df[col] = df[col].astype(str).str.strip()
                except Exception as e:
                    raise

            unique = df[col].dropna().unique()
            print(f'============== Columns of {df[col]}: ===============\n', unique)
                

        bookable_val = {'t': True, 'f': False,
                        'y': True, 'n': False, 
                        'yes':True, 'no': False,
                        'true': True, 'false': False}
        df['instant_bookable'] = (df['instant_bookable'].astype(str).str.strip().str.lower().map(bookable_val))
        
        df['host_identity_verified'] = (df['host_identity_verified'].astype(str).str.strip().str.lower().map({'verified': True,'unconfirmed':False}))

        df['cancellation_policy'] = df['cancellation_policy'].str.strip().str.lower().map({
            'flexible' : 'Flexible',
            'moderate' : 'Moderate',
            'strict' : 'Strict'
        })
        """
        Convert categorical fields (room_type, instant_bookable, cancellation_policy) to consistent formats.
        """

        df["room_type"] = df["room_type"].str.strip().str.title()

        min_lat, max_lat = 18.910, 71.390
        min_long, max_long = -179.148, -66.934570
        df = df[
            (df['lat'] >= min_lat) &
            (df['lat'] <= max_lat) &
            (df['long'] >= min_long) &
            (df['long'] <= max_long)
            ]
        print('========= BEFORE ==========\n',df.shape) 
        df = df[(df['price'] > 0 ) & (df['price'] <= 2000)]
        df = df[(df['service_fee'] >= 0) & (df['service_fee'] <= 500)]
        df = df[(df['minimum_nights'] > 0) & (df['minimum_nights'] <= 365)]
        df = df[df["availability_365"].between(0, 365)]
        print('========= AFTER ==========\n',df.shape) 

        # If duplicates by (host_id, lat, long, listing_name) keep the most recently reviewed.
        df = df.sort_values(by=['last_review', 'review_rate_number'], ascending=[False, False])
        df = df.drop_duplicates(subset=['host_id', 'lat', 'long', 'name'], keep='first')
        
        df['effective_nightly_price'] = df['price'] + df['service_fee']
        df['minimum_booking'] = df['effective_nightly_price'] * df['minimum_nights']
        df['calendar_openness'] = df['availability_365'] / 365.0

        rv = df["reviews_per_month"].fillna(0)
        norm_rv = (rv - rv.min()) / (rv.max() - rv.min() + 1e-9)
        df["dpi"] = (100 * (0.7*norm_rv + 0.3*(1 - df["calendar_openness"].fillna(0)))).round(1)

        # price bucket (quartiles)
        df["price_bucket"] = pd.qcut(df["effective_nightly_price"], 4,
                             labels=["Low","Mid","High","Luxury"])
        
        df['is_multi_listing_host'] = df['calculated_host_listings_count'] > 1
        
        today = pd.to_datetime(datetime.today().date())
        df = df[df['last_review'] <= today]
        df['review_recency_days'] = (today - df['last_review']).dt.days

        bool_cols = ['instant_bookable', 'host_identity_verified', 'is_multi_listing_host']
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].replace(["nan", "NaN", "None", "none", ""], pd.NA)
                df[col] = df[col].astype('boolean')   # nullable boolean dtype

        return df
    except Exception as e:
        raise
def sql_ready(df):
    """Convert pandas DataFrame to pure Python objects (replace <NA> with None)."""
    return df.astype(object).where(pd.notna(df), None)

    
def load_to_pg(df):
    conn = None
    cur = None
    try:
        
        dim_location_cols = sql_ready(df[['country', 'country_code', 'neighbourhood', 'neighbourhood_group','lat','long']].copy()).drop_duplicates() 
        dim_location_cols['location_id'] = dim_location_cols.index + 1

        dim_host_cols     = sql_ready(df[['host_id','host_name','host_identity_verified','is_multi_listing_host', 'calculated_host_listings_count']].copy()).drop_duplicates(subset=['host_id']) 
        dim_listing_cols  = sql_ready(df[['id','name','room_type','cancellation_policy','construction_year','house_rules']].copy()).drop_duplicates() 
        
        df = df.merge(
            dim_location_cols,
            on=['country','country_code','neighbourhood','neighbourhood_group','lat','long'],
            how='left'
        )

        fact_listing_cols = sql_ready(df[['id','location_id','host_id','price','service_fee','effective_nightly_price',
                            'minimum_nights','number_of_reviews','last_review','reviews_per_month','availability_365',
                            'review_rate_number','calendar_openness','minimum_booking','dpi','price_bucket','review_recency_days']].copy())   
        
        conn = psycopg2.connect(
            dbname = 'airbnb',
            host = 'localhost',
            user = pg_user,
            password = pg_pass,
            port = 5432
        )
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_location(
            location_id SERIAL PRIMARY KEY,
            country TEXT, country_code TEXT,
            neighbourhood TEXT, neighbourhood_group TEXT,
            lat DOUBLE PRECISION, long DOUBLE PRECISION,
            loaded_at TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_host(
            host_id BIGINT PRIMARY KEY,     
            host_name TEXT,
            host_identity_verified BOOLEAN,
            is_multi_listing_host BOOLEAN,
            calculated_host_listings_count INT,
            loaded_at TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_listing(
            id BIGINT PRIMARY KEY,
            name TEXT,
            room_type TEXT,
            cancellation_policy TEXT,
            construction_year INT,
            house_rules TEXT,
            loaded_at TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS fact_listing(
            id BIGINT PRIMARY KEY REFERENCES dim_listing(id),
            location_id INT REFERENCES dim_location(location_id),
            host_id BIGINT REFERENCES dim_host(host_id),
            price NUMERIC,
            service_fee NUMERIC,
            effective_nightly_price NUMERIC,
            minimum_nights INT,
            number_of_reviews INT,
            last_review DATE,
            reviews_per_month NUMERIC,
            availability_365 INT,
            review_rate_number NUMERIC,
            calendar_openness NUMERIC,
            minimum_booking NUMERIC,
            dpi NUMERIC,
            price_bucket TEXT,
            review_recency_days INT,
            loaded_at TIMESTAMP
        );
        """)
      
        load_time = datetime.now()

        if not dim_location_cols.empty:
            dim_location_cols['loaded_at'] = load_time
            columns = dim_location_cols.columns.tolist()

            values = [tuple(row) for row in dim_location_cols[columns].to_numpy()]
            execute_values(
                cur,
                f"""
                INSERT INTO dim_location ({','.join(columns)})
                VALUES %s;
                """,
                values
            )

        if not dim_host_cols.empty:
            dim_host_cols['loaded_at'] = load_time
            columns = dim_host_cols.columns.tolist()

            values = [tuple(row) for row in dim_host_cols[columns].to_numpy()]
            execute_values(
                cur,
                f"""
                INSERT INTO dim_host ({','.join(columns)})
                VALUES %s;
                """,
                values
            )

        if not dim_listing_cols.empty:
            dim_listing_cols['loaded_at'] = load_time
            columns = dim_listing_cols.columns.tolist()

            values = [tuple(row) for row in dim_listing_cols[columns].to_numpy()]
            execute_values(
                cur,
                f"""
                INSERT INTO dim_listing ({','.join(columns)})
                VALUES %s;
                """,
                values
            )

        if not fact_listing_cols.empty:
            fact_listing_cols['loaded_at'] = load_time
            columns = fact_listing_cols.columns.tolist()
            values = [tuple(row) for row in fact_listing_cols[columns].to_numpy()]

            execute_values(
                cur,
                f"""
                INSERT INTO fact_listing ({','.join(columns)})
                VALUES %s
                ON CONFLICT (id) DO NOTHING;
                """,
                values
            )

        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error loading to PostgreSQL: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def main_pipeline():
    file_path = r"D:\Python_Project\trial_folder\extracted\Airbnb_Open_Data.csv"
    df = pd.read_csv(file_path)
    cleaned = transform_data(df)

    cleaned.to_csv("cleaned_airbnb.csv", index=False)
    print("First 5 records:", cleaned.head())
    load_to_pg(cleaned)
    
if __name__ == "__main__":
    main_pipeline()