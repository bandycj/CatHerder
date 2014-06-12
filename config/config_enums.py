from enum import Enum

__author__ = 'e83800'

class AutoNumberedEnum(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

class ConfigKey(AutoNumberedEnum):
    SERVICE_LOGIN_URL = ()
    ACCESS_TOKEN_URL = ()
    USER_INFO_URL = ()
    CLIENT_ID = ()
    CLIENT_SECRET = ()

class OAuthService(Enum):
    GOOGLE = 'google'
    FACEBOOK = 'facebook'