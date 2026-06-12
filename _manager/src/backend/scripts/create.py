import uuid
import logging
import os
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo
from dataclasses import replace, asdict

from src.backend.models.server import Server, Metadata, Resources, Properties, Runtime
from src.util.manager.database import Database
from src.util.manager.config import Config
from src.util.request.mojang_api import get_player_by_name
from src.util.request.paper_api import get_latest_paper_version
from src.backend.scripts.start import main as start_server

logger = logging.getLogger(__name__)
config_manager = Config()
db_manager = Database()

def _converte_enums_to_values(obj):
    from enum import Enum
    if isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, dict):
        return {k: _converte_enums_to_values(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_converte_enums_to_values(i) for i in obj]
    return obj

def main(
        server_name: str,
        owner_username: str,
        server_version: str = None,
        ovr_metadata: dict = None,
        ovr_resources: dict = None,
        ovr_properties: dict = None,
        ovr_runtime: dict = None,
        created_at: datetime = datetime.now(ZoneInfo("Europe/Berlin")).isoformat(),
        updated_at: datetime = datetime.now(ZoneInfo("Europe/Berlin")).isoformat()
    ):
    # Generate UUID for the new server
    server_uuid = str(uuid.uuid4())

    # Check owner
    owner = get_player_by_name(owner_username)
    if not owner:
        return {"success": False, "error": f"No player found with name: {owner_username}"}

    # Get version
    if not server_version:
        server_version = get_latest_paper_version()
        if not server_version:
            return {"success": False, "error": "Failed to fetch latest Paper version"}

    # Prepare Metadata
    metadata = Metadata(
        name=server_name,
        version=server_version,
        owner = owner
    )
    if ovr_metadata:
        metadata = replace(metadata, **ovr_metadata)

    # Create Server Object with default values
    new_server = Server(
        uuid=server_uuid,
        metadata=metadata,
        resources=Resources(**(ovr_resources or {})),
        properties=Properties(**(ovr_properties or {})),
        runtime=Runtime(**(ovr_runtime or {})),
        created_at=created_at,
        updated_at=updated_at
    )

    # Save to Database
    server_dict = asdict(new_server)
    server_dict = _converte_enums_to_values(server_dict)
    db_manager.create(server_dict)

    # Create server directory
    server_type = metadata.type.value if metadata.type else "paper"
    servers_directory = config_manager.get("server_directory")

    dev_extension = config_manager.get("dev_extension")
    template_extension = config_manager.get("template_extension")

    template_path = f"{servers_directory}{template_extension}{server_type}{".dev" if metadata.dev_server else ''}"
    server_path = f"{servers_directory}{dev_extension if metadata.dev_server else ''}/{server_uuid}"

    try:
        # Copy template directory to new server directory
        if not os.path.exists(template_path):
            logger.error(f"Template path does not exist: {template_path}")
            return {"success": False, "error": f"Template path does not exist: {template_path}"}
        os.makedirs(server_path, exist_ok=True)
        for item in os.listdir(template_path):
            s = os.path.join(template_path, item)
            d = os.path.join(server_path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    except Exception as e:
        logger.error(f"Failed to create server directory: {e}")
        return {"success": False, "error": f"Failed to create server directory: {e}"}

    # Update serverUUID in plugins/ServerManagerChild/config.yml
    config_file_path = os.path.join(server_path, "plugins", "ServerManagerChild", "config.yml")
    try:
        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as f:
                config_content = f.read()
            config_content = config_content.replace('serverUUID: ""', f'serverUUID: "{server_uuid}"')
            with open(config_file_path, "w") as f:
                f.write(config_content)
        else:
            logger.warning(f"Config file not found at path: {config_file_path}")
            return {"success": False, "error": f"Config file not found at path: {config_file_path}"}
    except Exception as e:
        logger.error(f"Failed to update config.yml: {e}")
        return {"success": False, "error": f"Failed to update config.yml: {e}"}

    logger.info(f"Created new server with UUID: {server_uuid}")
    return {"success": True, "uuid": server_uuid, "server_path": server_path}
