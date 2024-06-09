import os

def read_obsidian_note(file_path):
    """
    Read the content of an Obsidian note from the specified file path.

    Args:
        file_path (str): The path to the Obsidian note file.

    Returns:
        dict: A dictionary containing the filename and content of the note.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return {"filename": os.path.basename(file_path), "content": content}
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except IOError as e:
        print(f"Error reading file: {file_path}")
        print(f"Error details: {str(e)}")
        return None

def load_processed_notes(file_path):
    """
    Load the processed notes from a file.

    Args:
        file_path (str): The path to the processed notes file.

    Returns:
        set: A set containing the processed note paths.
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return set(file.read().splitlines())
        except IOError as e:
            print(f"Error loading processed notes from {file_path}")
            print(f"Error details: {str(e)}")
    return set()

def save_processed_notes(file_path, processed_notes):
    """
    Save the processed notes to a file.

    Args:
        file_path (str): The path to the processed notes file.
        processed_notes (set): A set containing the processed note paths.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(processed_notes))
    except IOError as e:
        print(f"Error saving processed notes to {file_path}")
        print(f"Error details: {str(e)}")