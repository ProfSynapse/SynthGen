# api_clients.py

import openai
import os
from dotenv import load_dotenv
import anthropic
from groq import Groq
import google.generativeai as genai
from google.api_core import exceptions
import requests
import time

# Load environment variables from a .env file
load_dotenv()

# Load API keys from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
claude_api_key = os.getenv('CLAUDE_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')
local_api_url = os.getenv('LOCAL_API_URL')
local_api_model = os.getenv('LOCAL_API_MODEL')

def generate_response_openai(conversation_history, role, message, model_id, temperature, max_tokens):
    """
    Generate a response using OpenAI's API.

    Args:
        conversation_history (list): History of the conversation.
        role (str): Role of the responder (e.g., user, assistant).
        message (str): The message to generate a response for.
        model_id (str): The model ID for OpenAI.
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum number of tokens to generate.

    Returns:
        str: The generated response.
    """
    openai.api_key = openai_api_key
    try:
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=conversation_history + [{"role": role, "content": message}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error generating response from OpenAI: {str(e)}")
        return None

def generate_response_claude(conversation_history, role, message, model_id, temperature, max_tokens):
    """
    Generate a response using Claude's API.

    Args:
        conversation_history (list): History of the conversation.
        role (str): Role of the responder (e.g., user, assistant).
        message (str): The message to generate a response for.
        model_id (str): The model ID for Claude.
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum number of tokens to generate.

    Returns:
        str: The generated response.
    """
    client = anthropic.Client(api_key=claude_api_key)
    try:
        # Prepare the messages for Claude API
        claude_messages = [{"role": msg["role"], "content": msg["content"]} for msg in conversation_history]
        claude_messages.append({"role": role, "content": message})

        response = client.messages.create(
            model=model_id,
            messages=claude_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.content[0].text
    except Exception as e:
        print(f"Error generating response from Claude: {str(e)}")
        return None

def generate_response_groq(conversation_history, role, message, model_id, temperature, max_tokens):
    """
    Generate a response using Groq's API.

    Args:
        conversation_history (list): History of the conversation.
        role (str): Role of the responder (e.g., user, assistant).
        message (str): The message to generate a response for.
        model_id (str): The model ID for Groq.
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum number of tokens to generate.

    Returns:
        str: The generated response.
    """
    client = Groq(api_key=groq_api_key)
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": message["role"], "content": message["content"]} for message in conversation_history] + [{"role": role, "content": message}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response from Groq: {str(e)}")
        return None

def generate_response_gemini(message, model, max_retries=3, initial_delay=1):
    """
    Generate a response using Gemini's API.

    Args:
        message (str): The message to generate a response for.
        model (GenerativeModel): The GenerativeModel object for Gemini.
        max_retries (int): Maximum number of retries.
        initial_delay (int): Initial delay between retries.

    Returns:
        str: The generated response.
    """
    retries = 0
    delay = initial_delay
    genai.configure(api_key=gemini_api_key)

    while retries < max_retries:
        try:
            response_text = model.generate_content(message).text
            print(f"Successfully generated response with Gemini API")
            time.sleep(1)
            return response_text
        except exceptions.ResourceExhausted:
            print(f"Rate limit exceeded for Gemini API. Retrying...")
            retries += 1
            time.sleep(delay)
            delay *= 5
        except Exception as e:
            print(f"An unexpected error occurred while generating response from Gemini API: {str(e)}")
            return None

    print("Reached maximum retries. Please try again later.")
    return None

def generate_response_local(conversation_history, role, message, config, max_tokens=None, response_type=None):
    """
    Generate a response using a local API.

    Args:
        conversation_history (list): History of the conversation.
        role (str): Role of the responder (e.g., user, assistant).
        message (str): The message to generate a response for.
        config (dict): Configuration settings.
        max_tokens (int, optional): Maximum number of tokens to generate.
        response_type (str, optional): The type of response to generate.

    Returns:
        str: The generated response.
    """
    url = local_api_url
    if max_tokens is None:
        max_tokens = config['generation_parameters']['max_tokens']['default']

    mapped_conversation_history = [{"role": msg["role"], "content": msg["content"]} for msg in conversation_history]

    payload = {
        "model": local_api_model,
        "messages": [{"role": "system", "content": config['system_prompts']['synapse_system_prompt']}] + mapped_conversation_history + [{"role": role, "content": message}],
        "temperature": config['generation_parameters']['temperature'],
        "max_tokens": max_tokens,
        "stream": False
    }

    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        response_data = response.json()
        generated_response = response_data['choices'][0]['message']['content']
        return generated_response
    except requests.exceptions.RequestException as e:
        print(f"Error generating response from local model for {role} ({response_type}): {str(e)}")
        return None
    except KeyError as e:
        print(f"KeyError in response data: {str(e)}")
        print(f"Response data: {response_data}")
        return None
