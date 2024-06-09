import os
from dotenv import load_dotenv
import json
import requests
import random
import time
import sys
import threading
import uuid
import yaml
import openai
import anthropic
from groq import Groq
import google.generativeai as genai
from google.api_core import retry
from google.api_core import exceptions

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
claude_api_key = os.getenv('CLAUDE_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')

def is_500_error(exception):
    return isinstance(exception, exceptions.InternalServerError) and exception.code == 500

custom_retry = retry.Retry(
    predicate=is_500_error,
    initial=1.0,  # Initial delay in seconds
    maximum=60.0,  # Maximum delay in seconds
    multiplier=2.0,  # Delay multiplier per iteration
    deadline=300.0,  # Total timeout in seconds
)

genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

def generate_synapse_thought(thoughts):
    return random.choice(thoughts)

def read_obsidian_note(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return {"filename": os.path.basename(file_path), "content": content}

def display_synapse_thoughts(stop_event, thoughts):
    while not stop_event.is_set():
        thought = generate_synapse_thought(thoughts)
        for char in thought:
            sys.stdout.write(char)
            sys.stdout.flush()
            if stop_event.is_set():
                break
            time.sleep(0.05)
        sys.stdout.write("\n")
        if stop_event.is_set():
            break
        time.sleep(2)

def generate_response_openai(messages, model_id, openai_api_key, temperature=0.1, max_tokens=100):
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message['content']

def generate_response_claude(messages, model_id, claude_api_key, temperature=0.1, max_tokens=100):
    client = anthropic.Client(api_key=claude_api_key)
    response = client.messages.create(
        model=model_id,
        messages=[{"role": message["role"], "content": message["content"]} for message in messages],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.content[0].text

def generate_response_groq(messages, model_id, groq_api_key, temperature=0.1, max_tokens=100):
    client = Groq()
    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": message["role"], "content": message["content"]} for message in messages],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

def generate_response_gemini(message, model, max_tokens=100):
    @custom_retry
    def request_gemini_content():
        return model.generate_content(message).text

    try:
        response_text = request_gemini_content()
        return response_text
    except exceptions.InternalServerError as e:
        print(f"Error generating Gemini response: {e}")
        return None

def generate_response_local(payload, config):
    print(f"Sending API request to local model with payload: {payload}")

    stop_event = threading.Event()
    synapse_thoughts_thread = threading.Thread(target=display_synapse_thoughts, args=(stop_event, config['synapse_thoughts']))
    synapse_thoughts_thread.daemon = True
    synapse_thoughts_thread.start()

    try:
        response = requests.post(config['api_details']['url'], headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        stop_event.set()
        synapse_thoughts_thread.join()
        print(f"\nReceived response from local model: {response.json()}")
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        stop_event.set()
        synapse_thoughts_thread.join()
        print(f"\nError occurred while generating response: {e}")
        print(f"Request payload: {payload}")
        print(f"Response content: {response.content}")
        return None

def generate_conversation(note, output_file, config, use_openai, use_claude, use_groq, use_gemini):
    conversation_history = []
    conversation_id = str(uuid.uuid4())

    def generate_response(role, message, max_tokens, functions=None):
        payload = {
            "model": config['api_details']['model'],
            "messages": conversation_history + [{"role": role, "content": message}],
            "functions": functions,
            "temperature": config['generation_parameters']['temperature'],
            "max_tokens": max_tokens,
            "stream": False
        }
        if use_openai:
            return generate_response_openai(payload['messages'], config['openai_details']['model_id'], openai_api_key, config['generation_parameters']['temperature'], max_tokens)
        elif use_claude:
            return generate_response_claude(payload['messages'], config['claude_details']['model_id'], claude_api_key, config['generation_parameters']['temperature'], max_tokens)
        elif use_groq:
            return generate_response_groq(payload['messages'], config['groq_details']['model_id'], groq_api_key, config['generation_parameters']['temperature'], max_tokens)
        elif use_gemini:
            return generate_response_gemini(message, gemini_model, max_tokens)
        else:
            return generate_response_local(payload, config)

    user_problem = generate_response("user", f"{config['system_prompts']['user_system_prompt']}\n\nDocument:\n{note['content']}\n\n <generate problem, omit speaking for Professor Synapse, only output your problem and question>", config['generation_parameters']['max_tokens'])
    print(f"Generated user problem: {user_problem}")

    if user_problem is None:
        print("Failed to generate user problem.")
        return None

    conversation_history.append({"role": "user", "content": user_problem})
    append_conversation_to_json({"role": "user", "content": user_problem, "conversation_id": conversation_id, "turn": 0, "token_count": len(user_problem)}, output_file, conversation_id)

    num_turns = config['conversation_generation']['num_turns'] or random.randint(6, 8)

    for turn in range(num_turns):
        print(f"Turn {turn + 1}")
        
        print("Generating CoR response...")
        cor_prompt = f"{config['system_prompts']['cor_system_prompt']}\n\nDocument:\n{note['content']}\n\nConversation History:\n{conversation_history}\n\nFilled-in CoR:"
        cor_response = generate_response("assistant", cor_prompt, config['generation_parameters']['max_tokens'])
        print(f"Generated CoR response: {cor_response}")

        if cor_response is None:
            print("Failed to generate CoR response.")
            return conversation_history

        # Append CoR response to the conversation history
        conversation_history.append({"role": "cor", "content": cor_response})
        append_conversation_to_json({"role": "cor", "content": cor_response, "conversation_id": conversation_id, "turn": turn, "token_count": len(cor_response)}, output_file, conversation_id)

        print("Generating Synapse response...")
        synapse_prompt = f"{config['system_prompts']['synapse_system_prompt']}\n\nDocument:\n{note['content']}\n\nConversation History:\n{conversation_history}\n\nCoR:\n{cor_response}\n\n🧙🏿‍♂️'s response:"
        synapse_response = generate_response("assistant", synapse_prompt, config['generation_parameters']['max_tokens'])
        print(f"Generated Synapse response: {synapse_response}")

        if synapse_response is None:
            print("Failed to generate Synapse response.")
            return conversation_history

        synapse_response = f"🧙🏿‍♂️: {synapse_response}"
        conversation_history.append({"role": "assistant", "content": synapse_response})
        append_conversation_to_json({"role": "assistant", "content": synapse_response, "conversation_id": conversation_id, "turn": turn, "token_count": len(synapse_response)}, output_file, conversation_id)

        print("Generating user response...")
        user_prompt = f"{config['system_prompts']['user_system_prompt']}\n\nConversation History:\n{conversation_history}\n\nUser's response:"
        user_response = generate_response("user", user_prompt, config['generation_parameters']['max_tokens'])
        print(f"Generated user response: {user_response}")

        if user_response is None:
            print("Failed to generate user response.")
            return conversation_history

        conversation_history.append({"role": "user", "content": user_response})
        append_conversation_to_json({"role": "user", "content": user_response, "conversation_id": conversation_id, "turn": turn, "token_count": len(user_response)}, output_file, conversation_id)

        if "<requires_tool>" in user_response:
            tool_call = generate_response("assistant", f"To address the user's request, we need to make a tool call:\n\n<generate_tool_call>", config['generation_parameters']['max_tokens'], functions=[
                {
                    "name": "get_weather",
                    "description": "Get the current weather for a given location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA"
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"]
                            }
                        },
                        "required": ["location"]
                    }
                }
            ])
            if tool_call is None:
                print("Failed to generate tool call.")
                return conversation_history

            conversation_history.append({"role": "assistant", "content": tool_call})
            append_conversation_to_json({"role": "assistant", "content": tool_call, "conversation_id": conversation_id, "turn": turn, "token_count": len(tool_call)}, output_file, conversation_id)

            if turn == num_turns - 1:
                final_user_response = generate_response("user", f"{config['system_prompts']['user_system_prompt']}\n\nConversation History:\n{conversation_history}\n\nUser's final response:", config['generation_parameters']['max_tokens'])
                if final_user_response is None:
                    print("Failed to generate user's final response.")
                    return conversation_history

                conversation_history.append({"role": "user", "content": final_user_response})
                break

    return conversation_history

def print_conversation(conversation):
    print("\nConversation:")
    for message in conversation:
        role = "User" if message["role"] == "user" else "🧙🏿‍♂️"
        print(f"{role}: {message['content']}")
    print()

def format_output(conversation):
    return [{"role": message["role"], "content": message['content']} for message in conversation]

def append_conversation_to_json(message, output_file, conversation_id):
    try:
        message["conversation_id"] = conversation_id
        with open(output_file, 'a', encoding='utf-8') as file:
            json.dump(message, file, ensure_ascii=False)
            file.write('\n')
    except Exception as e:
        print(f"Failed to append message to {output_file}: {e}")

def main():
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    model_choice = input("Type the number of the model you wish to use: 1. OpenAi, 2. Claude, or 3. Groq 4. Gemini, 5. Local Model): ").strip().lower()
    use_openai = model_choice == "1"
    use_claude = model_choice == "2"
    use_groq = model_choice == "3"
    use_gemini = model_choice == "4"

    conversations = []
    for root, dirs, files in os.walk(config['file_paths']['obsidian_vault_path']):
        for file in files:
            if file.endswith(".md"):
                note_path = os.path.join(root, file)
                print(f"\nProcessing note: {note_path}")

                note = read_obsidian_note(note_path)

                for i in range(config['conversation_generation']['num_conversations']):
                    print(f"\nGenerating conversation {i + 1} for note: {note['filename']}")
                    conversation = generate_conversation(note, config['file_paths']['output_file'], config, use_openai, use_claude, use_groq, use_gemini)
                    if conversation:
                        formatted_output = format_output(conversation)
                        conversations.append(formatted_output)

    print(f"\nGenerated synthetic conversations saved to {config['file_paths']['output_file']}")
    print("Script finished.")

if __name__ == "__main__":
    main()
