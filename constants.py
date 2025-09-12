from enum import Enum

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
BASE_URL = "https://auth.dev-cinescope.coconutqa.ru"
LOGIN_ENDPOINT = "/login"
REGISTER_ENDPOINT = "/register"
USER_ENDPOINT = '/user'

MOVIES_URL = "https://api.dev-cinescope.coconutqa.ru"
MOVIES_ENDPOINT = "/movies"


class Roles(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"