import yaml

def load_config(file_path):
    """
    Load the configuration from a YAML file.

    Args:
        file_path (str): The path to the YAML configuration file.

    Returns:
        dict: The loaded configuration dictionary.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"Configuration file not found: {file_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error loading configuration file: {str(e)}")
        return None