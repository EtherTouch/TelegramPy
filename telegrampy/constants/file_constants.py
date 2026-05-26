import os.path
from pathlib import Path

USER_DATA_DIR = os.path.join(Path(__file__).parent.parent.parent, "user_data")
DEFAULT_CONFIG_JSON = os.path.join(USER_DATA_DIR, "config.json")
DEFAULT_TASKS_FOLDER = os.path.join(USER_DATA_DIR, "tasks")
