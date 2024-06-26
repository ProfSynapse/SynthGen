# conversation.py

import os
import json
import random
import uuid
from api_clients import (
    generate_response_openai,
    generate_response_claude,
    generate_response_groq,
    generate_response_gemini,
    generate_response_local
)
from google.api_core import exceptions
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Load API keys from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
claude_api_key = os.getenv('CLAUDE_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')
local_api_url = os.getenv('LOCAL_API_URL')
local_api_model = os.getenv('LOCAL_API_MODEL')

def generate_response(role, message, response_type=None, model_conversation_history=None, config=None, use_openai=False, use_claude=False, use_groq=False, use_gemini=False, use_local=False, gemini_model=None):
    """
    Generate a response using the selected AI model.

    Args:
        role (str): The role of the responder (e.g., user, assistant).
        message (str): The message to generate a response for.
        response_type (str, optional): The type of response to generate.
        model_conversation_history (list, optional): The history of the conversation for the model.
        config (dict, optional): Configuration settings.
        use_openai (bool): Flag to use OpenAI.
        use_claude (bool): Flag to use Claude.
        use_groq (bool): Flag to use Groq.
        use_gemini (bool): Flag to use Gemini.
        use_local (bool): Flag to use local model.
        gemini_model (GenerativeModel, optional): The Gemini model object.

    Returns:
        str: The generated response.
    """
    if not isinstance(config['generation_parameters']['max_tokens'], dict):
        raise ValueError("config['generation_parameters']['max_tokens'] should be a dictionary")

    max_tokens = config['generation_parameters']['max_tokens'].get(response_type or role, config['generation_parameters']['max_tokens']['default'])

    if use_openai:
        return generate_response_openai(model_conversation_history, role, message, config['openai_details']['model_id'], config['generation_parameters']['temperature'], max_tokens)
    elif use_claude:
        return generate_response_claude(model_conversation_history, role, message, config['claude_details']['model_id'], config['generation_parameters']['temperature'], max_tokens)
    elif use_groq:
        return generate_response_groq(model_conversation_history, role, message, config['groq_details']['model_id'], config['generation_parameters']['temperature'], max_tokens)
    elif use_gemini:
        print(f"Attempting to generate response with Gemini API.")
        response = generate_response_gemini(message, gemini_model)
        if response is None:
            raise exceptions.ResourceExhausted("All Gemini API keys have been exhausted. Please try again later.")
        return response
    elif use_local:
        return generate_response_local(model_conversation_history, role, message, config, max_tokens, response_type)
    else:
        raise ValueError("No valid AI model selected for response generation.")

def append_conversation_to_json(conversation, output_file, conversation_id):
    """
    Append a conversation entry to a JSON file.

    Args:
        conversation (dict): The conversation entry to append.
        output_file (str): Path to the output JSON file.
        conversation_id (str): The ID of the conversation.
    """
    if not os.path.exists(output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([], f)

    with open(output_file, 'r', encoding='utf-8') as f:
        try:
            conversations = json.load(f)
        except json.JSONDecodeError:
            conversations = []

    conversations.append(conversation)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, indent=4)

def generate_and_append_response(role, prompt, model_conversation_history, user_conversation_history, output_file, conversation_id, turn, response_type, name, last_role, config, use_openai, use_claude, use_groq, use_gemini, use_local, gemini_model):
    """
    Generate a response and append it to the conversation history.

    Args:
        role (str): The role of the responder (e.g., user, assistant).
        prompt (str): The prompt for generating the response.
        model_conversation_history (list): The history of the conversation for the model.
        user_conversation_history (list): The history of the user's conversation.
        output_file (str): The output file path.
        conversation_id (str): The conversation ID.
        turn (int): The turn number in the conversation.
        response_type (str): The type of response to generate.
        name (str): The name of the responder.
        last_role (str): The role of the last message in the conversation.
        config (dict): Configuration settings.
        use_openai (bool): Flag to use OpenAI.
        use_claude (bool): Flag to use Claude.
        use_groq (bool): Flag to use Groq.
        use_gemini (bool): Flag to use Gemini.
        use_local (bool): Flag to use local model.
        gemini_model (GenerativeModel, optional): The Gemini model object.

    Returns:
        tuple: The generated response and the new last_role.
    """
    print(f"Conversation ID: {conversation_id}, Turn: {turn}, Role: {role}")
    print(random.choice(config['synapse_thoughts']))

    # Ensure alternating roles for Claude API
    if use_claude and role == last_role:
        # If the roles would be the same, insert a user message
        interim_prompt = f"Based on the last response, what would be a good follow-up question or comment?"
        interim_response = generate_response("user", interim_prompt, model_conversation_history=model_conversation_history, config=config, use_claude=use_claude)
        model_conversation_history.append({"role": "user", "content": interim_response, "name": "System"})
        user_conversation_history.append({"role": "user", "content": interim_response, "name": "System"})
        append_conversation_to_json({"role": "user", "name": "System", "content": interim_response, "conversation_id": conversation_id, "turn": turn, "token_count": len(interim_response)}, output_file, conversation_id)
        last_role = "user"

    response = generate_response(role, prompt, response_type, model_conversation_history, config, use_openai, use_claude, use_groq, use_gemini, use_local, gemini_model)
    if response is None:
        print(f"Failed to generate {role} response.")
        return None, last_role

    if name == "Professor":
        response = f"🧙🏿‍♂️: {response}"

    model_conversation_history.append({"role": role, "content": response, "name": name})
    
    if role == "user" or name == "Professor":
        user_conversation_history.append({"role": role, "content": response, "name": name})
    
    append_conversation_to_json({"role": role, "name": name, "content": response, "conversation_id": conversation_id, "turn": turn, "token_count": len(response)}, output_file, conversation_id)
    
    return response, role

def generate_conversation(note, output_file, config, use_openai, use_claude, use_groq, use_gemini, use_local):
    """
    Generate a synthetic conversation based on a user's note.

    Args:
        note (dict): Note content to base the conversation on.
        output_file (str): Path to the output file for saving the conversation.
        config (dict): Configuration settings.
        use_openai (bool): Flag to use OpenAI.
        use_claude (bool): Flag to use Claude.
        use_groq (bool): Flag to use Groq.
        use_gemini (bool): Flag to use Gemini.
        use_local (bool): Flag to use local model.

    Returns:
        list: The generated conversation history.
    """
    model_conversation_history = []
    user_conversation_history = []
    conversation_id = str(uuid.uuid4())
    last_role = "system"  # Initialize with system to ensure the first message is from the user

    gemini_model = None
    if use_gemini:
        gemini_model = genai.GenerativeModel(config['gemini_details']['model_id'])

    # Initial user problem generation with document access
    print(f"Generating user problem for note: {note['filename']}")
    user_problem, last_role = generate_and_append_response(
        "user",
        f"{config['system_prompts']['user_system_prompt']}\n\nDocument:\n{note['content']}\n\n**You are now Joseph!**, and are about to begin your conversation with Prof. Come up with the problem you face based on the provided text, and respond in the first person as Joseph:**",
        model_conversation_history,
        user_conversation_history,
        output_file,
        conversation_id,
        0,
        response_type="user",
        name="Joseph",
        last_role=last_role,
        config=config,
        use_openai=use_openai,
        use_claude=use_claude,
        use_groq=use_groq,
        use_gemini=use_gemini,
        use_local=use_local,
        gemini_model=gemini_model
    )
    
    if user_problem is None or not user_problem.strip():
        print("Failed to generate user problem or user problem is empty.")
        return None

    num_turns = random.randint(6, 10)  # Randomly choose the number of turns between 6 and 10

    for turn in range(1, num_turns + 1):
        print(f"Generating CoR response for turn {turn}")
        cor_prompt = f"{config['system_prompts']['cor_system_prompt']}\n\nConversation History:\n{model_conversation_history}\n\nFilled-in CoR:"
        cor_response, last_role = generate_and_append_response(
            "assistant",
            cor_prompt,
            model_conversation_history,
            user_conversation_history,
            output_file,
            conversation_id,
            turn,
            response_type="cor",
            name="CoR",
            last_role=last_role,
            config=config,
            use_openai=use_openai,
            use_claude=use_claude,
            use_groq=use_groq,
            use_gemini=use_gemini,
            use_local=use_local,
            gemini_model=gemini_model
        )
        if cor_response is None or not cor_response.strip():
            return model_conversation_history

        print(f"Generating Professor Synapse response for turn {turn}")
        synapse_prompt = f"{config['system_prompts']['synapse_system_prompt']}\n\nConversation History:\n{model_conversation_history}\n\n🧙🏿‍♂️:"
        synapse_response, last_role = generate_and_append_response(
            "assistant",
            synapse_prompt,
            model_conversation_history,
            user_conversation_history,
            output_file,
            conversation_id,
            turn,
            response_type="professor_synapse",
            name="Professor",
            last_role=last_role,
            config=config,
            use_openai=use_openai,
            use_claude=use_claude,
            use_groq=use_groq,
            use_gemini=use_gemini,
            use_local=use_local,
            gemini_model=gemini_model
        )
        if synapse_response is None or not synapse_response.strip():
            return model_conversation_history

        # User follow-up prompt without document access but using the system prompt and previous user conversation history
        user_followup_prompt = f"{config['system_prompts']['user_system_prompt']}\n\nConversation History:\n{user_conversation_history}\n\nBased on Professor Synapse's previous response, ask a specific NEW question that builds upon the information provided and helps deepen your understanding of the topic. Respond in first person as Joseph:"
        user_followup_response, last_role = generate_and_append_response(
            "user",
            user_followup_prompt,
            model_conversation_history,
            user_conversation_history,
            output_file,
            conversation_id,
            turn,
            response_type="user",
            name="Joseph",
            last_role=last_role,
            config=config,
            use_openai=use_openai,
            use_claude=use_claude,
            use_groq=use_groq,
            use_gemini=use_gemini,
            use_local=use_local,
            gemini_model=gemini_model
        )
        if user_followup_response is None or not user_followup_response.strip():
            return model_conversation_history

    return model_conversation_history

def format_output(conversation):
    """
    Format the output of the conversation.

    Args:
        conversation (list): The conversation history.

    Returns:
        list: The formatted conversation history.
    """
    return conversation

def finalize_json_output(output_file):
    """
    Finalize the JSON output file.

    Args:
        output_file (str): Path to the output JSON file.
    """
    pass