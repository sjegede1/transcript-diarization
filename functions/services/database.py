from pymongo import MongoClient
from pymongo.database import Database


def initialize_db(mongodb_uri: str, db_name:str ="transcription") -> Database:
    print(f"MongoDB URI: {mongodb_uri}")
    try:
        client = MongoClient(mongodb_uri)
        db = client[db_name]
        print(f"Database connected {db_name}")
        return db
    except Exception as e:
        print(f"Database connection failed {e}")
        return None
