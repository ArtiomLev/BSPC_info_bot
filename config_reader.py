from typing import *
from pydantic_settings import BaseSettings
from pydantic import SecretStr, ValidationError
import yaml


class Settings(BaseSettings):
    bot_token: SecretStr
    bells: Dict
    changes: Dict
    users: Dict


try:
    with open("token.txt") as file:
        raw_token = file.read().strip()
    with open("config.yaml") as file:
        raw_config = yaml.safe_load(file) or {}
except FileNotFoundError as err:
    raise RuntimeError(f"Missing configuration file: {err.filename()}")

try:
    config = Settings(
        bot_token=raw_token,
        **raw_config
    )

except ValidationError as err:
    raise RuntimeError(f"Configuration errors: {err.errors()}")


