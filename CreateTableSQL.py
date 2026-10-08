#!/usr/bin/env python3

import os
import psycopg
import csv
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

## Make Header list for SQL table creation

DataFile = "mtda_18MDV.txt"
table_name = Path(DataFile).stem.lower()
#PathToDataFolder = Path("/mnt/c/Users/orang/OneDrive/My Publications/18MDV_Bacteria/VEBA_pipeline_output")
PathToDataFolder = Path("/mnt/c/Users/orang/OneDrive/My Publications/Finished Projects/Diss3_18MDV_PrtMtgnmSrvy/Analyses/Ch3_R-analyses/")
Data_Path = PathToDataFolder / DataFile

print(table_name)
print(PathToDataFolder)
print(Data_Path)

with open(Data_Path, 'r') as file:
    reader = csv.reader(file, delimiter = "\t")
    header = next(reader)

#print(len(header))

## Create list of sql table column descriptions
columns = [f'"{header[0]}" TEXT'] + [
    f'"{column}" INTEGER' for column in header[1:]
]

#print(columns)

## create sql table create command
create_table_sql = (
    "CREATE TABLE " + table_name + " (\n" \
    + ",\n".join(columns)
    + "\n);" \
)

#print(create_table_sql)

#exit()

## Push commands to postgresql server
conn = psycopg.connect(
    host=os.getenv("PGHOST", "localhost"),
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD")
)

cursor = conn.cursor()

cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
cursor.execute(create_table_sql)
conn.commit()

with conn.cursor() as cur:
    with open(Data_Path, "r") as f:
        with cur.copy(
            f"COPY {table_name} FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t', HEADER true)"
        )  as copy:
            while data := f.read(8192):
                copy.write(data)

cursor.close()
conn.close()
