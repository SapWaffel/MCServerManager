import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from src.util.manager.config import Config

logger = logging.getLogger(__name__)

class MongoDBClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.client = None
        self.db = None
        self.config = Config.get("mongodb")

        uri = self.config.get("uri")
        self._connect(uri)
        self._initialized = True

    def _connect(self, connection_string: str):
        try:
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client["service"]
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_db(self, db_name: str):
        try:
            db = self.client[db_name]
            if db is None:
                raise ValueError(f"Database '{db_name}' not found or not connected")
            return db
        except Exception as e:
            raise ValueError(f"Failed to access database '{db_name}': {e}")

    def disconnect(self) -> None:
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.client = MongoDBClient()

    @staticmethod
    def get(identifier: dict, return_field: str = None, default=None):
        try:
            manager = Database()
            db = manager.client.get_db("service")
            collection = db["minecraft"]

            result = collection.find_one(identifier)

            if not result:
                logger.warning(f"No document found for identifier: {identifier}")
                return default

            if result is None:
                return default

            if return_field is None:
                return result

            keys = return_field.split(".")
            value = result

            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return default

            return value if value is not None else default

        except Exception as e:
            logger.error(f"Error retrieving data from MongoDB: {e}")
            return default

    @staticmethod
    def set(identifier: dict, update_data: dict) -> bool:
        try:
            manager = Database()
            db = manager.client.get_db("service")
            collection = db["minecraft"]

            result = collection.update_one(identifier, {"$set": update_data}, upsert=True)
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            logger.error(f"Error updating data in MongoDB: {e}")
            return False

    @staticmethod
    def create(identifier: dict, data: dict) -> bool:
        #usage: Database.create({"uuid": "some-uuid"}, {"name": "PlayerName", "score": 100})
        try:
            manager = Database()
            db = manager.client.get_db("service")
            collection = db["minecraft"]

            if collection.find_one(identifier):
                logger.warning(f"Document with identifier {identifier} already exists.")
                return False

            collection.insert_one({**identifier, **data})
            return True
        except Exception as e:
            logger.error(f"Error creating document in MongoDB: {e}")
            return False

    @staticmethod
    def delete(identifier: dict) -> bool:
        try:
            manager = Database()
            db = manager.client.get_db("service")
            collection = db["minecraft"]

            result = collection.delete_one(identifier)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document from MongoDB: {e}")
            return False

