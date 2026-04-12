import yaml


def read_yaml(file_path: str) -> dict[str, list[str]]:
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

        return data

    except Exception as e:
        print(f"Error reading YAML: {e}")

    return None
