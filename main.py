# main.py

import os
from config import load_config
from conversation import generate_conversation, format_output
from file_utils import read_obsidian_note, load_processed_notes, save_processed_note
from google.api_core import exceptions
from datetime import datetime

def process_note(note_path, config, use_openai, use_claude, use_groq, use_gemini, use_openrouter, processed_notes_file, max_usage):
    """
    Process a single note and generate conversations.

    Args:
        note_path (str): Path to the note file.
        config (dict): Configuration settings.
        use_openai (bool): Flag to use OpenAI.
        use_claude (bool): Flag to use Claude.
        use_groq (bool): Flag to use Groq.
        use_gemini (bool): Flag to use Gemini.
        use_openrouter (bool): Flag to use OpenRouter.
        processed_notes_file (str): File to track processed notes.
        max_usage (int): Maximum usage per API key.

    Returns:
        list: List of generated conversations.
    """
    # Create the synth_conversations folder if it doesn't exist
    synth_conversations_folder = "synth_conversations"
    os.makedirs(synth_conversations_folder, exist_ok=True)
    
    # Generate a unique output file name based on the current date/time
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(synth_conversations_folder, f"synthgen_{current_datetime}.json")
    
    conversations = []
    
    for i in range(config['conversation_generation']['num_conversations']):
        print(f"\nGenerating conversation {i + 1} for note: {note_path}")
        try:
            note = read_obsidian_note(note_path)
            conversation = generate_conversation(
                note,
                output_file,
                config,
                use_openai,
                use_claude,
                use_groq,
                use_gemini,
                use_openrouter,
            )
            if conversation:
                formatted_output = format_output(conversation)
                conversations.append(formatted_output)
                save_processed_note(processed_notes_file, note_path)
                print(f"Processed note {note_path} and appended to processed_notes.txt")
        except exceptions.ResourceExhausted as e:
            print(str(e))
            print("Exhausted API key usage. Please try again later.")
            return conversations
    
    print(f"Finished processing note: {note_path}")
    return conversations

def main():
    """
    The main function to run the script.
    """
    config = load_config('config.yaml')
    processed_notes_file = 'processed_notes.txt'
    processed_notes = load_processed_notes(processed_notes_file)

    model_choice = input("Type the number of the model you wish to use: 1. OpenAI, 2. Claude, 3. Groq, 4. Gemini, 5. OpenRouter, 6. Local Model: ").strip()
    print(f"User selected model choice: {model_choice}")
    use_openai = model_choice == "1"
    use_claude = model_choice == "2"
    use_groq = model_choice == "3"
    use_gemini = model_choice == "4"
    use_openrouter = model_choice == "5"
    use_local = model_choice == "6"

    print("Starting to process notes...")
    
    notes = []
    for root, dirs, files in os.walk(config['file_paths']['obsidian_vault_path']):
        for file in files:
            if file.endswith(".md"):
                note_path = os.path.join(root, file)
                if note_path in processed_notes:
                    print(f"\nSkipping already processed note: {note_path}")
                    continue

                notes.append(note_path)

    try:
        max_usage = config['gemini_details']['max_usage_per_key']  # Define max usage per key
    except KeyError:
        print("Error: 'max_usage_per_key' not found in 'gemini_details' section of the config file.")
        return

    # Process notes sequentially
    for note in notes:
        process_note(note, config, use_openai, use_claude, use_groq, use_gemini, use_openrouter, processed_notes_file, max_usage)

    print("Script finished.")

if __name__ == "__main__":
    main()
