import logging
import os
import threading
import subprocess
from pathlib import Path

from src.util.manager.port import Port
from src.util.manager.database import Database
from src.util.manager.config import Config

logger = logging.getLogger(__name__)
port_manager = Port()
db_manager = Database()
config_manager = Config()

def main(uuid: str, port: int = None):

    # Get Database
    server_data = Database.get({"uuid": uuid})
    if not server_data:
        return {"success": False, "error": f"No server found with UUID: {uuid}"}

    # Get Flags & Resources
    dev_server = server_data.get("metadata", {}).get("dev_server", False)
    ram_min_mb = server_data.get("resources", {}).get("ram_min_mb", 1024)
    ram_max_mb = server_data.get("resources", {}).get("ram_max_mb", 2048)

    server_directory = Config.get("server_directory")
    dev_extension = Config.get("dev_extension")
    server_path = f"{server_directory}{dev_extension if dev_server else ''}/{uuid}"
    # Allocate Port
    if port:
        if port_manager.check_availability(port):
            allocated_port = port
            port_manager.ACTIVE_PORTS.append(allocated_port)
        else:
            return {"success": False, "error": f"Port {port} is already in use."}
    else:    
        allocated_port = port_manager.allocate(server_type="default" if not dev_server else "dev")

    if not allocated_port:
        return {"success": False, "error": "No available ports to allocate."}

    Database.set({"uuid": uuid}, {"resources.port": allocated_port})

    # Update server.properties
    update_server_properties(uuid, server_data, server_path, allocated_port, dev_server)

    # get server jar file
    server_jar_file = next((f for f in os.listdir(server_path) if f.startswith("server") and f.endswith(".jar")), None)
    if not server_jar_file:
        return {"error": f"No server jar file found in path: {server_path}"}
    
    # Start Server
    java_cmd = [
        "java",
        f"-Xms{ram_min_mb}M",
        f"-Xmx{ram_max_mb}M",
        "-jar",
        server_jar_file,
        "nogui"
    ]
    server_thread = threading.Thread(target=run_server, args=(java_cmd, server_path, uuid), daemon=True, name=f"minecraft-{uuid}")
    server_thread.start()

    logger.info(f"Server with UUID {uuid} started on port {allocated_port}")
    return {"success": True, "uuid": uuid, "port": allocated_port}

def update_server_properties(uuid: str, server_data: dict, server_path: str, port: int, dev_server: bool = False):
    

    properties_path = f"{server_path}/server.properties"

    if not os.path.exists(properties_path):
        logger.error(f"server.properties not found at path: {properties_path}")
        return

    # Read existing properties
    properties = {}
    with open(properties_path, "r") as f:
        for line in f:
            line = line.strip()

            if not "=" in line:
                continue

            key, value = line.split("=", 1)
            properties[key] = value

    # Update port
    properties["server-port"] = str(port)

    # update properties
    for prop, value in server_data.get("properties", {}).items():
        properties[prop.replace("_", "-")] = str(value)
        print(f"Updated property {prop} to {value}")

    # Write back properties
    with open(properties_path, "w") as f:
        for key, value in properties.items():
            f.write(f"{key}={value}\n")

def run_server(java_cmd: list, server_path: str, uuid: str):
    try:
        process = subprocess.Popen(
            java_cmd,
            cwd=server_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Started server process with PID: {process.pid}")
        Database.set({"uuid": uuid}, {"runtime.pid": process.pid, "runtime.status": "starting"}) 
    except subprocess.CalledProcessError as e:
        logger.error(f"Server process exited with error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error running server process: {e}")
        return None