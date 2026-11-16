"""Database connection and query helper functions."""
import os

import mysql.connector
from dotenv import load_dotenv

# Read DB_HOST, DB_USER, DB_PASSWORD, DB_NAME from the .env file
load_dotenv()


def get_db():
    """Open a new connection to the MySQL database."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "job_tracker"),
    )


def fetch_all(sql, params=None):
    """Run a SELECT and return every row as a list of dicts."""
    conn = get_db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        return cursor.fetchall()
    finally:
        conn.close()


def fetch_one(sql, params=None):
    """Run a SELECT and return the first row as a dict (or None)."""
    conn = get_db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        return cursor.fetchone()
    finally:
        conn.close()


def execute(sql, params=None):
    """Run an INSERT/UPDATE/DELETE, commit it, and return the new row id."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()