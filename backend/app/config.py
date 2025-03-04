import os
import time
from enum import Enum

################################################
# from dotenv import load_dotenv
# ## Test with dotenv (Only Locally)
# parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# # .env path
# dotenv_path = os.path.join(parent_dir, '.env')
# print(f'Loading .env file from: {dotenv_path}')
# load_dotenv(dotenv_path=dotenv_path)
################################################

class AppEnvironment(Enum):
    DEV = ("dev", "Development environment")
    TEST = ("test", "Testing environment")
    PROD = ("prod", "Production environment")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    def __str__(self):
        return self.value

class EnvVariables(Enum):
    APP_ENV = ("APP_ENV", AppEnvironment.DEV.value)
    ORIGIN = ("ORIGIN", "*")  # Default to "*" for allowing all origins
    SCHEDULER = ("SCHEDULER", "True") # Default to true for activating schedulers

    def __new__(cls, key, default):
        obj = object.__new__(cls)
        obj._value_ = key  # Use _value_ for the key
        obj.key = key
        obj.default = default
        return obj

class SingletonMeta(type):
    """
    Singleton Meta Class to ensure only one instance of the class is created.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Config(metaclass=SingletonMeta):
    APP_NAME = "jonas-fastapi-master"
    APP_ENV = AppEnvironment.DEV
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    ORIGIN = os.getenv(EnvVariables.ORIGIN.key, EnvVariables.ORIGIN.default)
    SCHEDULER: bool = False if os.getenv(EnvVariables.SCHEDULER.key, EnvVariables.SCHEDULER.default) and os.getenv(EnvVariables.SCHEDULER.key, EnvVariables.SCHEDULER.default).lower() == "true" else False

    def __str__(self):
        # Define the string representation of the Config object
        return (f"Config(\n"
                f"  APP_NAME={self.APP_NAME},\n"
                f"  DEBUG={self.APP_ENV.value},\n"
                f"  DATABASE_URL={self.DATABASE_URL},\n"
                f"  SECRET_KEY={self.SECRET_KEY},\n"
                f"  ORIGIN={self.ORIGIN}\n"
                f"  ORIGIN={self.SCHEDULER}\n"
                f")")

class DevConfig(Config):
    APP_ENV = AppEnvironment.DEV
    DATABASE_URL = os.getenv("DEV_DATABASE_URL", "sqlite:///./dev.db")

class TestConfig(Config):
    APP_ENV = AppEnvironment.TEST
    DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

class ProdConfig(Config):
    APP_ENV = AppEnvironment.PROD
    DATABASE_URL = os.getenv("PROD_DATABASE_URL", "postgresql://user:pass@localhost/prod_db")

def get_config():
    """
    Get the appropriate configuration based on the APP_ENV environment variable.
    """
    env = os.getenv(EnvVariables.APP_ENV.key, EnvVariables.APP_ENV.default)
    if env == AppEnvironment.DEV.value:
        return DevConfig()
    elif env == AppEnvironment.TEST.value:
        return TestConfig()
    elif env == AppEnvironment.PROD.value:
        return ProdConfig()
    return Config()

def update_config():
    """
    Update the current configuration if there are changes.
    """
    global current_config
    new_config = get_config()
    if not isinstance(current_config, type(new_config)) or current_config.DATABASE_URL != new_config.DATABASE_URL:
        current_config = new_config

# Load initial configuration
current_config = get_config()

def watch_env_vars(interval=10):
    """
    Watch for changes in environment variables and update configuration if needed.
    """
    last_env = os.getenv(EnvVariables.APP_ENV.key, EnvVariables.APP_ENV.default)
    while True:
        current_env = os.getenv(EnvVariables.APP_ENV.key, EnvVariables.APP_ENV.default)
        if current_env != last_env:
            update_config()
            last_env = current_env
        time.sleep(interval)

# Start a separate thread to watch for environment variable changes
import threading
threading.Thread(target=watch_env_vars, daemon=True).start()
