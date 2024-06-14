import os

def read_obsidian_note(file_path):
    """
    Read the content of an Obsidian note from the specified file path.

    Args:
        file_path (str): The path to the Obsidian note file.

    Returns:
        dict: A dictionary containing the filename and content of the note, or None if an error occurs.
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
    processed_notes = set()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    processed_notes.add(line.strip())
        except IOError as e:
            print(f"Error loading processed notes from {file_path}")
            print(f"Error details: {str(e)}")
    return processed_notes

def save_processed_note(file_path, note_path):
    """
    Append a processed note path to the processed notes file.

    Args:
        file_path (str): The path to the processed notes file.
        note_path (str): The path of the processed note to be appended.
    """
    try:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(f"{note_path}\n")
    except IOError as e:
        print(f"Error appending processed note to {file_path}")
        print(f"Error details: {str(e)}")

def delete_processed_note(file_path, note_path):
    """
    Delete a processed note path from the processed notes file.

    Args:
        file_path (str): The path to the processed notes file.
        note_path (str): The path of the processed note to be deleted.

    Returns:
        bool: True if the note was successfully deleted, False otherwise.
    """
    try:
        if not os.path.exists(file_path):
            print(f"Processed notes file not found: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open(file_path, 'w', encoding='utf-8') as file:
            for line in lines:
                if line.strip() != note_path:
                    file.write(line)

        return True
    except IOError as e:
        print(f"Error deleting processed note from {file_path}")
        print(f"Error details: {str(e)}")
        return False
