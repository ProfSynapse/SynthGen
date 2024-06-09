import os
from config import load_config
from conversation import generate_conversation, format_output, finalize_json_output
from file_utils import read_obsidian_note, load_processed_notes, save_processed_notes
from google.api_core import exceptions
from api_clients import gemini_api_keys

def main():
    """
    The main function to run the script.
    """
    config = load_config('config.yaml')
    processed_notes_file = 'processed_notes.txt'
    processed_notes = load_processed_notes(processed_notes_file)

    model_choice = input("Type the number of the model you wish to use: 1. OpenAI, 2. Claude, 3. Groq, 4. Gemini, 5. Local Model: ").strip()
    print(f"User selected model choice: {model_choice}")
    use_openai = model_choice == "1"
    use_claude = model_choice == "2"
    use_groq = model_choice == "3"
    use_gemini = model_choice == "4"
    use_local = model_choice == "5"

    gemini_api_key_index = 0

    conversations = []
    print("Starting to process notes...")
    gemini_api_key_index = 0
    max_api_key_cycles = len(gemini_api_keys)

    try:
        for root, dirs, files in os.walk(config['file_paths']['obsidian_vault_path']):
            for file in files:
                if file.endswith(".md"):
                    note_path = os.path.join(root, file)
                    if note_path in processed_notes:
                        print(f"\nSkipping already processed note: {note_path}")
                        continue

                    print(f"\nProcessing note: {note_path}")

                    note = read_obsidian_note(note_path)

                    for i in range(config['conversation_generation']['num_conversations']):
                        print(f"\nGenerating conversation {i + 1} for note: {note['filename']}")
                        conversation = generate_conversation(
                            note,
                            config['file_paths']['output_file'],
                            config,
                            use_openai,
                            use_claude,
                            use_groq,
                            use_gemini,
                            gemini_api_key_index,
                            max_api_key_cycles=max_api_key_cycles
                        )
                        if conversation:
                            formatted_output = format_output(conversation)
                            conversations.append(formatted_output)
                            processed_notes.add(note_path)
                            save_processed_notes(processed_notes_file, processed_notes)
    except exceptions.ResourceExhausted as e:
        print(str(e))
        return

    finalize_json_output(config['file_paths']['output_file'])

    print(f"\nGenerated synthetic conversations saved to {config['file_paths']['output_file']}")
    print("Script finished.")

if __name__ == "__main__":
    main()
