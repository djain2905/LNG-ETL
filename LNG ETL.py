import pandas as pd
import os 

#Export
csv_url =  "https://raw.githubusercontent.com/djain2905/LNG-ETL/main/lng_raw.csv"     
csv_df = pd.read_csv(csv_url, encoding="latin-1")   

print(csv_df.head())

#Transform
csv_df = csv_df.replace("\xa0", " ", regex=True)    #Fixes invisible broken spaces

for column in csv_df.select_dtypes(include = "object").columns:     #Strips messy spaces from words and turns them into strings
    csv_df[column] = csv_df[column].astype(str).str.strip()

csv_df["region"] = csv_df["region"].str.upper()
csv_df["benchmark"] = csv_df["benchmark"].str.upper()    #Standardizes uppercase for region + benchmark 

csv_df["date"] = pd.to_datetime(csv_df["date"], errors = "coerce")     #Converts date text to a real date type 

number_cols = ["price_usd_mmbtu",
    "volume_mmt",
    "freight_usd_mmbtu",
    "liquefaction_utilization_pct"]
for col in number_cols: csv_df[col] = pd.to_numeric(csv_df[col], errors = "coerce")      #Converts number text to real numbers

before_dupe = len(csv_df)      
csv_df = csv_df.drop_duplicates()
after_dupe = len(csv_df)
print("Removed duplicates:", before_dupe - after_dupe)        #Removes duplicates

print("Rows:", len(csv_df))
print("Columns:", len(csv_df.columns))
print("Missing cells:", int(csv_df.isna().sum().sum()))       #Print number of rows, columns, missing cells

#Load
from sqlalchemy import create_engine
engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

table = "raw_LNG_data"
csv_df.to_sql(table, engine, index = False, if_exists = "append")
print("Loaded into", table)


