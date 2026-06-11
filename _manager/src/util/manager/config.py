import json
from pathlib import Path
from typing import Any
import logging

logger = logging.getLogger(__name__)

class Config:
    _instance = None
    _config = None
    _config_path = "/home/sap/minecraft/_manager/config.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if Config._config is not None:
            return

        self._config_path = Path(self._config_path)
        self._load_config()

    def _load_config(self):
        try:
            with open(self._config_path, 'r') as f:
                Config._config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            Config._config = {}

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        if Config._config is None:
            raise RuntimeError("Config not loaded. Initialize Config before accessing it.")

        keys = key.split('.')
        value = Config._config

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default

        return value if value is not None else default