from dataclasses import dataclass
from enum import Enum

from src.backend.models.player import Player

class Visibility(Enum):
    PUBLIC = "public"
    INVITE_ONLY = "invite_only"
    PRIVATE = "private"

class StartupPolicy(Enum):
    OWNER_ONLY = "owner_only"
    INVITE_ONLY = "invite_only"
    EVERYONE = "everyone"

@dataclass
class PrivacySettings:
    visibility: Visibility = Visibility.PRIVATE
    startup_policy: StartupPolicy = StartupPolicy.OWNER_ONLY
    invited_players: list[Player] = None