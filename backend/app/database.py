import sqlite3
from flask import g, current_app
import logging

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config['DATABASE_PATH'])
        db.row_factory = sqlite3.Row
    return db

def init_db():
    try:
        with sqlite3.connect(current_app.config['DATABASE_PATH']) as conn:
            cursor = conn.cursor()
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    business_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Create business_strategies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS business_strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    business_type TEXT NOT NULL,
                    location_name TEXT NOT NULL,
                    location_coords TEXT NOT NULL,
                    trend_data TEXT,
                    competitor_data TEXT,
                    strategy TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            # Create analyzed_locations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analyzed_locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    location_coords TEXT NOT NULL,
                    location_name TEXT,
                    trend_data TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, location_coords)
                )
            ''')
            # Create heatmap_data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS heatmap_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    location TEXT NOT NULL,
                    category TEXT NOT NULL,
                    heatmap_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            # Create competitor_insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS competitor_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    location TEXT NOT NULL,
                    category TEXT NOT NULL,
                    insight_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            # Create landmark_data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS landmark_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    business TEXT NOT NULL,
                    location TEXT NOT NULL,
                    landmark_data TEXT,
                    recommendation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            # Create generated_reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generated_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    report_name TEXT NOT NULL,
                    report_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            conn.commit()
            logging.getLogger("market_research_api").info("Successfully initialized SQLite database")
    except Exception as e:
        logging.getLogger("market_research_api").error(f"Failed to initialize SQLite database: {e}")
        raise
