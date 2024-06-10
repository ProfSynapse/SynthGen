import os
from config import load_config
from conversation import generate_conversation, format_output, finalize_json_output
from file_utils import read_obsidian_note, load_processed_notes, save_processed_notes
from google.api_core import exceptions
from api_clients import gemini_api_keys
from datetime import datetime

def main():
    """
    The main function to run the script.
    """
    config = load_config('config.yaml')
    processed_notes_file = 'processed_notes.txt'
    processed_notes = load_processed_notes(processed_notes_file)

    # Create the synth_conversations folder if it doesn't exist
    synth_conversations_folder = "synth_conversations"
    os.makedirs(synth_conversations_folder, exist_ok=True)

    # Generate a new synthgen.json filename with the current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(synth_conversations_folder, f"synthgen_{current_datetime}.json")

    model_choice = input("Type the number of the model you wish to use: 1. OpenAI, 2. Claude, 3. Groq, 4. Gemini, 5. OpenRouter, 6. Local Model: ").strip()
    print(f"User selected model choice: {model_choice}")
    use_openai = model_choice == "1"
    use_claude = model_choice == "2"
    use_groq = model_choice == "3"
    use_gemini = model_choice == "4"
    use_openrouter = model_choice == "5"
    use_local = model_choice == "6"

    conversations = []
    print("Starting to process notes...")

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
                            output_file,  # Pass the new output_file variable
                            config,
                            use_openai,
                            use_claude,
                            use_groq,
                            use_gemini,
                            use_openrouter
                        )
                        if conversation:
                            formatted_output = format_output(conversation)
                            conversations.append(formatted_output)
                            processed_notes.add(note_path)
                            save_processed_notes(processed_notes_file, processed_notes)
    except exceptions.ResourceExhausted as e:
        print(str(e))
        return

    finalize_json_output(output_file)  # Pass the new output_file variable

    print(f"\nGenerated synthetic conversations saved to {output_file}")  # Print the new output_file variable
    print("Script finished.")

if __name__ == "__main__":
    main()