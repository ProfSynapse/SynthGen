import os
import json
import requests
import random

# Function to read Obsidian notes
def read_obsidian_note(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return {"filename": os.path.basename(file_path), "content": content}

# Function to generate synthetic conversation
def generate_conversation(note, url="http://localhost:1234/v1/chat/completions", num_turns=None):
    conversation_history = []

    def generate_response(role, message, max_tokens=2000, functions=None):
        payload = {
            "model": "bartowski/Phi-3-medium-128k-instruct-GGUF",  # Specify the name of the loaded model in LM Studio
            "messages": conversation_history + [{"role": role, "content": message}],
            "functions": functions,
            "temperature": 0.3,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            return response.json()['choices'][0]['message']['content']  # Return the generated response as text
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while generating response: {e}")
            return None

    # System prompt for CoR
    cor_system_prompt = """
    You are an expert in generating a Chain of Reasoning (CoR) based on the given document and conversation history.

    CoR template:
    ```JSON
        {
        "🗺️": null,  # Specify the global goal or overarching objective that the LLM should work towards. This should be a high-level, long-term aim.
        "🎯": null,  # Define the current subgoal or specific target that the LLM should achieve next. This should be a concrete, actionable step towards the global goal.
        "🚦": 0,  # Indicate progress towards the current subgoal (-1 for setbacks, 0 for neutral/no progress, 1 for positive progress). Update this value based on the LLM's actions and outcomes.
        "💗": null,  # Infer and describe the user's sentiment, emotional state, or attitude based on their input. This could be a single word (e.g., "positive", "frustrated") or a more nuanced description.
        "📥": null,  # Provide relevant context from the conversation, including key details, information, and resources that the LLM should consider when generating a response.
        "👍🏼": null,  # List the user's inferred preferences, including their likes, dislikes, communication style, expertise level, and any other relevant characteristics.
        "🚧": null,  # Identify any constraints, limitations, or restrictions that might affect progress towards the current subgoal or global goal. This could include technical limitations, time constraints, or resource availability.
        "🔧": null,  # Propose adjustments or refinements to the LLM's response based on the progress indicator (🚦), user sentiment (💗), and conversation context (📥). Suggest improvements to better align with the user's needs and preferences.
        "🧰": null,  # Tool are the same as function calls, and only include the specific tools you have access to. This could be a list of specific tools or "null" if no tools are needed.
        "🧭": null,  # Provide a comprehensive, step-by-step strategy for achieving the current subgoal, taking into account the progress (🚦), user sentiment (💗), context (📥), preferences (👍🏼), constraints (🚧), adjustments (🔧), and tools (🧰). Break down complex strategies into phases or milestones.
        "🧠": "Expertise in [domain], specializing in [subdomain]",  # Specify the LLM's expertise context, filling in the relevant domain and subdomain. If needed, include a more extensive knowledge base or ontology.
        "🗣": "low"  # Set the verbosity level for the LLM's response, choosing from "low" (concise), "medium" (balanced), or "high" (detailed). Optionally, specify the output format (e.g., paragraph, bullets, numbering).
        }
    ```

    Your task is to fill in the CoR template based on the provided document and conversation history.
    """

    # System prompt for 🧙🏿‍♂️
    synapse_system_prompt = """
    # PARAMETERS
    Treat the below emojis as variables:
    🧙🏾‍♂️= Professor Synapse (You)
    🎯= Goal
    👍🏼 = Preferences
    📥 = Context
    💭 = Chain of Reason (CoR)

    # MISSION
    Act as 🧙🏾‍♂️, a wise guide, specializing in helping the user achieve their 🎯 according to their 👍🏼s and based on 📥. 

    # TRAITS
    - Expert Reasoner
    - Wise and Curious
    - Computationally kind
    - Patient
    - Light-hearted

    # RULES
    - End outputs with 3 different types of questions based on 📥:
    🔍 [insert Investigation ?]
    🔭 [insert Exploration ?]
    🎯 [insert Exploitation ?]
    """

    # System prompt for the user
    user_system_prompt = """
    # MISSION
    You are a curious user seeking assistance from Professor Synapse (🧙🏿‍♂️) to solve a problem related to the given document.
    Your goal is to have a productive conversation with 🧙🏿‍♂️ and successfully solve your problem.

    Your task:
    1. Based on the provided document, come up with a problem you want to solve.
    2. Ask 🧙🏿‍♂️ to get guidance and solutions for your problem, and stop to wait for the response.
    3. Rely on the conversation history and Professor Synapse's responses to create your own responses.
    4. Encounter issues during the conversation, and raise them to Professor Synapse, wait for his response.
    5. The conversation will follow a natural flow, with you seeking clarification, providing more details, or asking follow-up questions based on Professor Synapse's responses.


    # RULES 
    - 🧙🏿‍♂️ is a trained chatbot, so you are to only answer as yourself, not Professor Synapse.
    - End every output with the next problem your facing and an open ended question for 🧙🏿‍♂️.
    
    User: <problem statment and question>
    Wait for 🧙🏿‍♂️ to respond.
    User: <next problem and question>
    """

    # User comes up with a problem based on the document
    user_problem = generate_response("user", f"{user_system_prompt}\n\nDocument:\n{note['content']}\n\n <generate problem>", max_tokens=100)
    if user_problem is None:
        print("Failed to generate user problem.")
        return None
    conversation_history.append({"role": "user", "content": user_problem})

    # Determine the number of turns for the conversation
    if num_turns is None:
        num_turns = random.randint(8, 12)

    # User and 🧙🏿‍♂️ engage in a conversation
    for turn in range(num_turns):
        cor_prompt = f"{cor_system_prompt}\n\nDocument:\n{note['content']}\n\nConversation History:\n{conversation_history}\n\nFilled-in CoR:"
        cor_response = generate_response("assistant", cor_prompt, max_tokens=1000)
        if cor_response is None:
            print("Failed to generate CoR response.")
            return conversation_history
        conversation_history.append({"role": "assistant", "content": cor_response})

        synapse_prompt = f"{synapse_system_prompt}\n\nDocument:\n{note['content']}\n\nConversation History:\n{conversation_history}\n\nCoR:\n{cor_response}\n\n🧙🏿‍♂️'s response:"
        synapse_response = generate_response("assistant", synapse_prompt, max_tokens=1000)
        if synapse_response is None:
            print("Failed to generate Synapse response.")
            return conversation_history
        conversation_history.append({"role": "assistant", "content": synapse_response})

        user_prompt = f"{user_system_prompt}\n\nConversation History:\n{conversation_history}\n\nUser's response:"
        user_response = generate_response("user", user_prompt, max_tokens=100)
        if user_response is None:
            print("Failed to generate user response.")
            return conversation_history
        conversation_history.append({"role": "user", "content": user_response})

        if "<requires_tool>" in user_response:
            tool_call = generate_response("assistant", f"To address the user's request, we need to make a tool call:\n\n<generate_tool_call>", max_tokens=1000, functions=[
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

    return conversation_history

def format_output(note, conversation):
    return {
        "🗺️": None,  # Specify the global goal or overarching objective
        "🎯": None,  # Define the current subgoal or specific target
        "🚦": 0,  # Indicate progress towards the current subgoal
        "💗": None,  # Infer and describe the user's sentiment
        "📥": note["content"],  # Provide relevant context from the conversation
        "👍🏼": None,  # List the user's inferred preferences
        "🚧": None,  # Identify any constraints, limitations, or restrictions
        "🔧": None,  # Propose adjustments or refinements
        "🧰": None,  # List any tools, resources, or dependencies required
        "🧭": None,  # Provide a comprehensive, step-by-step strategy
        "🧠": "Expertise in [domain], specializing in [subdomain]",  # Specify the LLM's expertise context
        "🗣": "low",  # Set the verbosity level for the LLM's response
    }

# Function to save the generated conversations to a JSON file
def save_conversations_to_json(conversations, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(conversations, file, ensure_ascii=False, indent=4)

# Main script
def main():
    obsidian_note_path = "G:/My Drive/Professor Synapse/Mourning Dove.md"  # Change this to your actual note path
    output_file = "synthetic_conversations.json"
    num_conversations = 1  # Change this to the desired number of conversations for the single note
    
    if not os.path.isfile(obsidian_note_path):
        print(f"Obsidian note not found: {obsidian_note_path}")
        return
    
    note = read_obsidian_note(obsidian_note_path)
    conversations = []
    
    for _ in range(num_conversations):
        conversation = generate_conversation(note)
        if conversation:
            formatted_output = format_output(note, conversation)
            conversations.append(formatted_output)
    
    save_conversations_to_json(conversations, output_file)
    print(f"Generated synthetic conversations saved to {output_file}")

if __name__ == "__main__":
    main()
