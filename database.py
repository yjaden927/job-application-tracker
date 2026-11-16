# database.py
import os
import mysql.connector
from dotenv import load_dotenv

# load environment variables
load_dotenv()

def get_db():
    # open a connection to the job_tracker database
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "job_tracker")
    )

def fetch_all(sql, params=None):
    # run a select query and return all rows as a list of dictionaries
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
        
    results = cursor.fetchall()
    
    # make sure to close the connections
    cursor.close()
    conn.close()
    
    return results

def fetch_one(sql, params=None):
    # run a select query but only get the first row back
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
        
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return result

def execute(sql, params=None):
    # run insert, update, or delete queries and save the changes
    conn = get_db()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
        
    # have to commit to actually save the changes
    conn.commit()
    row_id = cursor.lastrowid
    
    cursor.close()
    conn.close()
    
    return row_id