import mysql.connector
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Establish the database connection"""
        if not self.connection:
            self.connection = mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                port=DB_CONFIG.get("port", 3306)  # Default port is 3306
            )
            self.cursor = self.connection.cursor()
            print("Database connected successfully!")

    def execute_query(self, query, params=None):
        """Execute a query (e.g., SELECT, INSERT, UPDATE)"""
        if not self.connection:
            self.connect()
        self.cursor.execute(query, params or ())
        self.connection.commit()

    def fetch_results(self, query, params=None):
        """Fetch results from a SELECT query"""
        if not self.connection:
            self.connect()
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def close(self):
        """Close the database connection"""
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Database connection closed.")