import logging

from src.util.manager.config import Config

logger = logging.getLogger(__name__)


class Port:
    ACTIVE_PORTS = []

    def __init__(self):
        self.config_manager = Config()
        self._get_port_range()

    def _get_port_range(self, server_type: str = "default") -> list:
        port_range = self.config_manager.get("ports", {}).get(server_type)
        if not port_range:
            raise ValueError(f"Port range for server type '{server_type}' not defined in configuration.")
        return port_range

    @staticmethod
    def allocate(server_type: str = "default") -> int:
        port_range = Port()._get_port_range(server_type)
        if not port_range:
            raise ValueError("Port range not defined in configuration.")
        
        allocated_port = min(port_range)
        while allocated_port in Port.ACTIVE_PORTS:
            allocated_port += 1
            if allocated_port > max(port_range):
                raise ValueError(f"No available ports in the {server_type} range.")

        Port.ACTIVE_PORTS.append(allocated_port)
        return allocated_port

    @staticmethod
    def release(port: int):
        if port in Port.ACTIVE_PORTS:
            Port.ACTIVE_PORTS.remove(port)

    @staticmethod
    def block(port: int) -> bool:
        if port not in Port.ACTIVE_PORTS:
            Port.ACTIVE_PORTS.append(port)
            return True
        return False

    @staticmethod
    def check_availability(port: int) -> bool:
        return port not in Port.ACTIVE_PORTS