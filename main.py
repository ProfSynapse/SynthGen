import os
from config import load_config
from conversation import generate_conversation, format_output
from file_utils import read_obsidian_note, load_processed_notes, save_processed_note
from google.api_core import exceptions
from api_clients import gemini_api_keys
from datetime import datetime
import multiprocessing

def process_note(note_path, process_id, config, use_openai, use_claude, use_groq, use_gemini, use_openrouter, processed_notes_file, api_key_usage, max_usage, lock):
    # Function to process a single note and generate conversations
    
    # Create the synth_conversations folder if it doesn't exist
    synth_conversations_folder = "synth_conversations"
    os.makedirs(synth_conversations_folder, exist_ok=True)
    
    # Generate a unique output file name based on the process ID and current date/time
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(synth_conversations_folder, f"synthgen_{current_datetime}_process_{process_id}.json")
    
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
                process_id,
            )
            if conversation:
                formatted_output = format_output(conversation)
                conversations.append(formatted_output)
                with lock:
                    save_processed_note(processed_notes_file, note_path)
                print(f"Processed note {note_path} and appended to processed_notes.txt")
        except exceptions.ResourceExhausted as e:
            print(str(e))
            # Switch API key and retry
            with lock:
                api_key_usage[process_id] += 1
            if api_key_usage[process_id] >= max_usage:
                print(f"Exhausted API key for process {process_id}. Switching key.")
                with lock:
                    api_key_usage[process_id] = 0  # Reset usage for the new key
                process_id = (process_id + 1) % len(gemini_api_keys)
            return conversations
    
    print(f"Finished processing note: {note_path}")
    print(f"Switching to Gemini API key index: {process_id}")
    
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
    print(f"Available Gemini API keys: {gemini_api_keys}")

    notes = []
    for root, dirs, files in os.walk(config['file_paths']['obsidian_vault_path']):
        for file in files:
            if file.endswith(".md"):
                note_path = os.path.join(root, file)
                if note_path in processed_notes:
                    print(f"\nSkipping already processed note: {note_path}")
                    continue

                notes.append(note_path)

    # Create a pool of processes and a manager to track API key usage and a lock for synchronized access
    num_processes = len(gemini_api_keys)
    manager = multiprocessing.Manager()
    api_key_usage = manager.list([0] * num_processes)  # Shared list to track API key usage
    lock = manager.Lock()  # Lock for synchronized access to shared resources

    try:
        max_usage = config['gemini_details']['max_usage_per_key']  # Define max usage per key
    except KeyError:
        print("Error: 'max_usage_per_key' not found in 'gemini_details' section of the config file.")
        return

    pool = multiprocessing.Pool(processes=num_processes)

    # Process notes in parallel and pass the process ID to each process
    results = pool.starmap(process_note, [(note, i % num_processes, config, use_openai, use_claude, use_groq, use_gemini, use_openrouter, processed_notes_file, api_key_usage, max_usage, lock) for i, note in enumerate(notes)])

    # Close the pool and wait for all processes to finish
    pool.close()
    pool.join()

    # Combine the results from all processes
    conversations = []
    for result in results:
        conversations.extend(result)

    print("Script finished.")

if __name__ == "__main__":
    multiprocessing.freeze_support()  # Required for Windows
    main()