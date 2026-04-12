import yaml
from app.core.logging import Logger
logger = Logger(__name__)


def read_yaml(file_path: str) -> dict[str, list[str]]:
    logger.info(f"Entered read_yaml with file_path={file_path}")
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

        return data

    except Exception as e:
        print(f"Error reading YAML: {e}")

    return None
