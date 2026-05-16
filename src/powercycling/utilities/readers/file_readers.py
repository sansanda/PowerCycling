def read_config_file(file_path):
    """
    Read configuration file and return a dictionary.

    File format:
        VARIABLE=VALUE

    Lines starting with '*' are ignored as comments.
    """

    config = {}

    with open(file_path, "r") as file:

        for line in file:

            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip comments
            if line.startswith("*"):
                continue

            # Skip malformed lines
            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            config[key.strip()] = value.strip()

    return config

