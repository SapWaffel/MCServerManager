from dataclasses import dataclass, field
from enum import Enum

from src.backend.models.player import Player
from src.backend.models.privacy import PrivacySettings

class ServerType(Enum):
    VANILLA = "vanilla"
    SPIGOT = "spigot"
    PAPER = "paper"
    FORGE = "forge"
    FABRIC = "fabric"

@dataclass
class Metadata:
    name: str
    version: str
    privacy: PrivacySettings = field(default_factory=PrivacySettings)
    description: str = ""
    owner: Player = None
    type: ServerType = ServerType.PAPER
    player_count: int = 0
    dev_server: bool = False

@dataclass
class Resources:
    ram_min_mb: int = 1024
    ram_max_mb: int = 1024
    port: int | None = None

@dataclass
class Properties:
    difficulty: str = "hard"
    gamemode: str = "survival"
    max_players: int = 20
    spawn_protection: int = 16
    hardcore: bool = False
    generate_structures: bool = True
    level_seed: str = ""
    level_type: str = "minecraft:normal"

@dataclass
class Runtime:
    status: str = "stopped"
    pid: int | None = None
    started_at: str | None = None
    stopped_at: str | None = None
    graceful_shutdown_requested: bool = False

@dataclass
class Server:
    uuid: str
    metadata: Metadata
    resources: Resources
    properties: Properties
    runtime: Runtime
    created_at: str
    updated_at: str