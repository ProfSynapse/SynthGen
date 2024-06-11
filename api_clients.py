import openai
import os
from dotenv import load_dotenv
import anthropic
from groq import Groq
import google.generativeai as genai
from google.api_core import exceptions
import requests
import time

load_dotenv()

gemini_api_keys = [
    os.getenv('GEMINI_API_KEY_1'),
    os.getenv('GEMINI_API_KEY_2'),
    os.getenv('GEMINI_API_KEY_3'),
    os.getenv('GEMINI_API_KEY_4'),
    os.getenv('GEMINI_API_KEY_5'),
    os.getenv('GEMINI_API_KEY_6'),
    os.getenv('GEMINI_API_KEY_7'),
    os.getenv('GEMINI_API_KEY_8'),
    os.getenv('GEMINI_API_KEY_9'),
    os.getenv('GEMINI_API_KEY_10'),
    os.getenv('GEMINI_API_KEY_11'),
    os.getenv('GEMINI_API_KEY_12'),
    os.getenv('GEMINI_API_KEY_13'),
    os.getenv('GEMINI_API_KEY_14'),
    os.getenv('GEMINI_API_KEY_15'),
    os.getenv('GEMINI_API_KEY_16'),
    os.getenv('GEMINI_API_KEY_17'),
    os.getenv('GEMINI_API_KEY_18')
]

def generate_response_openai(conversation_history, role, message, model_id, api_key, temperature, max_tokens):
    openai.api_key = api_key
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

def generate_response_claude(conversation_history, role, message, model_id, api_key, temperature, max_tokens):
    client = anthropic.Client(api_key=api_key)
    try:
        response = client.messages.create(
            model=model_id,
            messages=[{"role": message["role"], "content": message["content"]} for message in conversation_history] + [{"role": role, "content": message}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.content[0].text
    except Exception as e:
        print(f"Error generating response from Claude: {str(e)}")
        return None

def generate_response_groq(conversation_history, role, message, model_id, temperature, max_tokens):
    client = Groq()
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

def generate_response_gemini(message, model, gemini_api_key_index, max_retries=3, initial_delay=1):
    retries = 0
    delay = initial_delay
    max_api_key_cycles = len(gemini_api_keys)

    while gemini_api_key_index < max_api_key_cycles:
        current_api_key = gemini_api_keys[gemini_api_key_index]
        print(f"Trying Gemini API key: {current_api_key}")
        genai.configure(api_key=current_api_key)

        while retries < max_retries:
            try:
                response_text = model.generate_content(message).text
                print(f"Successfully generated response with Gemini API key index: {gemini_api_key_index}")
                return response_text
            except exceptions.ResourceExhausted:
                print(f"Rate limit exceeded for Gemini API key index: {gemini_api_key_index}. Retrying...")
                retries += 1
                time.sleep(delay)
                delay *= 2
            except Exception as e:
                print(f"An unexpected error occurred while generating response from Gemini API: {str(e)}")
                return None

        print(f"Reached maximum retries for Gemini API key index: {gemini_api_key_index}. Moving to the next API key...")
        gemini_api_key_index += 1
        retries = 0
        delay = initial_delay

    print("Reached maximum API key cycles. Please try again later.")
    return None


def generate_response_local(conversation_history, role, message, config, max_tokens=None, response_type=None):
    url = config['api_details']['url']
    if max_tokens is None:
        max_tokens = config['generation_parameters']['max_tokens']['default']

    mapped_conversation_history = [{"role": msg["role"], "content": msg["content"]} for msg in conversation_history]

    payload = {
        "model": config['api_details']['model'],
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
