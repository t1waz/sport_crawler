import yaml


def load_schedule_config(schedule_file_path: str) -> dict:
    with open(schedule_file_path, "r") as file:
        data = file.read()

    return yaml.safe_load(data)


def parse_duration_to_seconds(duration: str) -> int:
    duration = duration.lower()
    if duration.endswith("h"):
        base = 3600
    elif duration.endswith("m"):
        base = 60
    elif duration.endswith("s"):
        base = 1
    else:
        base = 1

    return int(duration.strip("h").strip("m").strip("s")) * base
