import openai
import os
from dotenv import load_dotenv
import anthropic
from groq import Groq
import google.generativeai as genai
from google.api_core import retry
from google.api_core import exceptions
import requests
import json
import time
from datetime import datetime, timedelta

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
    os.getenv('GEMINI_API_KEY_11')
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
    current_api_key = gemini_api_keys[gemini_api_key_index]
    genai.configure(api_key=current_api_key)

    def is_500_error(exception):
        return isinstance(exception, exceptions.InternalServerError) and exception.code == 500

    @retry.Retry(predicate=is_500_error)
    def request_gemini_content():
        return model.generate_content(message).text

    retries = 0
    delay = initial_delay

    requests_per_minute = 2
    tokens_per_minute = 32000
    requests_per_day = 50

    api_key_counters = {
        "requests_this_minute": 0,
        "tokens_this_minute": 0,
        "requests_today": 0,
        "minute_start_time": datetime.now(),
        "day_start_time": datetime.now().date()
    }

    while retries < max_retries:
        if api_key_counters["requests_this_minute"] >= requests_per_minute:
            seconds_to_wait = 60 - (datetime.now() - api_key_counters["minute_start_time"]).seconds
            time.sleep(seconds_to_wait)
            api_key_counters["requests_this_minute"] = 0
            api_key_counters["tokens_this_minute"] = 0
            api_key_counters["minute_start_time"] = datetime.now()

        if api_key_counters["tokens_this_minute"] >= tokens_per_minute:
            seconds_to_wait = 60 - (datetime.now() - api_key_counters["minute_start_time"]).seconds
            time.sleep(seconds_to_wait)
            api_key_counters["requests_this_minute"] = 0
            api_key_counters["tokens_this_minute"] = 0
            api_key_counters["minute_start_time"] = datetime.now()

        if api_key_counters["requests_today"] >= requests_per_day:
            seconds_to_wait = (datetime.combine(datetime.now().date() + timedelta(days=1), datetime.min.time()) - datetime.now()).seconds
            time.sleep(seconds_to_wait)
            api_key_counters["requests_today"] = 0
            api_key_counters["day_start_time"] = datetime.now().date()

        try:
            response_text = request_gemini_content()
            api_key_counters["requests_this_minute"] += 1
            api_key_counters["tokens_this_minute"] += len(response_text)
            api_key_counters["requests_today"] += 1
            return response_text
        except exceptions.ResourceExhausted:
            retries += 1
            time.sleep(delay)
            delay *= 2

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
