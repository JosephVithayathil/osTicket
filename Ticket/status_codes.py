from enum import IntEnum, unique, auto

@unique
class StatusCode(IntEnum):
    OK = 0
    ERROR = auto()
    INVALID_CREDENTIALS = auto()
    AUTHENTICATION_SERVER_NOT_AVAILABLE = auto()
    STAKEHOLDER_NOT_IN_DATABASE = auto()
    LEAVES_OVERLAPING = auto()
    
