import os
import json
import requests
import random
import time
import sys
import threading
import uuid

def generate_synapse_thought():
    thoughts = [
        "🤔 Hmm, let me ponder this for a moment...",
        "💡 Aha! I think I'm onto something!",
        "🧐 This is quite the intriguing problem. Let's dig deeper!",
        "🌌 Exploring the vast realms of knowledge, seeking answers...",
        "🔍 Investigating all possible avenues, leave no stone unturned!",
        "🔮 Gazing into my crystal ball for divine inspiration...",
        "🧙‍♂️ Summoning ancient wisdom from the depths of my beard...",
        "🐉 Consulting with the wise dragon council for guidance...",
        "🧪 Concocting a potion of brilliance in my bubbling cauldron...",
        "📜 Unrolling the sacred scroll of problem-solving secrets...",
        "🗝️ Unlocking the hidden chambers of my mind palace...",
        "🌈 Riding on a rainbow of creativity to find the pot of gold...",
        "🎩 Pulling innovative ideas out of my magical hat...",
        "🧚‍♀️ Sprinkling a dash of fairy dust to spark new insights...",
        "🏰 Navigating the labyrinthine corridors of the knowledge castle...",
        "🧝‍♂️ Seeking counsel from the wise elves of the intellectual forest...",
        "🔥 Igniting the flames of ingenuity within my soul...",
        "🌋 Channeling the explosive power of my mental volcano...",
        "🌠 Wishing upon a shooting star for a burst of inspiration...",
        "🌙 Harnessing the mystical energy of the full moon for clarity...",
        "🍄 Munching on a magic mushroom to expand my cognitive horizons...",
        "🗿 Communing with the ancient statues of knowledge...",
        "🌀 Diving into the swirling vortex of creative chaos...",
        "🎭 Donning the mask of the great thinkers of the past...",
        "🎨 Painting a masterpiece of innovative solutions...",
        "🎲 Rolling the dice of destiny to determine the path forward...",
        "🔊 Amplifying the whispers of wisdom from the universe...",
        "🎹 Composing a symphony of groundbreaking ideas...",
        "🎈 Floating on a balloon of imagination to new heights...",
        "🌋 Erupting with a lava flow of game-changing concepts...",
        "🎣 Fishing for the perfect solution in the ocean of possibilities...",
        "🎢 Buckle up! We're in for a wild ride of intellectual discovery...",
        "🌪️ Spinning in a tornado of mental acuity and resourcefulness...",
        "🎪 Step right up to the circus of unorthodox problem-solving!",
        "🎯 Aiming my arrow of acumen at the bullseye of brilliance...",
        "🧿 The eye of insight is upon us, revealing hidden truths...",
        "🔬 Zooming in on the microscopic details of this enigma...",
        "🤔 If time travel is possible, where are all the tourists from the future?",
        "🧐 Do androids dream of electric philosophers?",
        "😅 If laughter is the best medicine, can it cure existential dread?",
        "🎩 How do you know you're not just a brain in a vat, simulating this problem?",
        "🐜 If a tiny ant carries a crumb of knowledge, how many ants does it take to solve this problem?",
        "🤖 In a world where AI can think, do we need to rethink thinking?",
        "🌍 If the Earth is flat, does that mean our thinking is one-dimensional?",
        "🧠 Are we living inside a giant's mind, and this problem is just a fleeting thought?",
        "🎭 If all the world's a stage, can we ad-lib our way to a solution?",
        "🐒 If an infinite number of monkeys are typing on an infinite number of typewriters, will they eventually solve this problem?",
        "🧘‍♂️ If a problem is solved in the forest and no one is around to hear it, does it make a difference?",
        "🎲 Is the randomness of the universe just a cosmic game of dice?",
        "🦋 If a butterfly flaps its wings and causes a hurricane, what happens when a philosopher has an idea?",
        "🌌 Are parallel universes just different chapters in the grand book of cosmic problem-solving?",
        "🎨 If art imitates life, and life imitates art, does that mean we're all just imitating problem-solving?",
        "🎩 What if the answer to this problem is hidden in a magician's hat, waiting to be pulled out like a rabbit?",
        "🧪 If we pour all our knowledge into a beaker, will it create the perfect solution or just a bubbling mess?",
        "🎭 Are we all just actors in a cosmic play, improvising our way through problem-solving?",
        "🎈 If ideas are like balloons, how many do we need to lift this problem off the ground?",
        "🍀 If a four-leaf clover brings luck, what does a four-dimensional clover bring to problem-solving?",
    ]
    return random.choice(thoughts)

# Function to read Obsidian notes
def read_obsidian_note(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return {"filename": os.path.basename(file_path), "content": content}

# Function to display Synapse thoughts
def display_synapse_thoughts(stop_event):
    while not stop_event.is_set():
        thought = generate_synapse_thought()
        for char in thought:
            sys.stdout.write(char)
            sys.stdout.flush()
            if stop_event.is_set():
                break
            time.sleep(0.05)  # Adjust the delay between each character
        
        sys.stdout.write("\n")  # Move to the next line after displaying the complete thought
        
        if stop_event.is_set():
            break
        
        time.sleep(2)  # Wait for a couple of seconds before changing the thought

# Function to generate synthetic conversation
def generate_conversation(note, output_file, url="http://localhost:1234/v1/chat/completions", num_turns=None):
    conversation_history = []
    conversation_id = str(uuid.uuid4())

    def generate_response(role, message, max_tokens=2000, functions=None):
        payload = {
            "model": "bartowski/Phi-3-medium-128k-instruct-GGUF",  # Specify the name of the loaded model in LM Studio
            "messages": conversation_history + [{"role": role, "content": message}],
            "functions": functions,
            "temperature": 0.1,
            "max_tokens": max_tokens,
            "stream": False
        }

        print(f"Sending API request to LM Studio for {role} with message: {message}")  # Debug print statement

        stop_event = threading.Event()
        synapse_thoughts_thread = threading.Thread(target=display_synapse_thoughts, args=(stop_event,))
        synapse_thoughts_thread.daemon = True
        synapse_thoughts_thread.start()

        try:
            response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            stop_event.set()  # Signal the Synapse thoughts thread to stop
            synapse_thoughts_thread.join()  # Wait for the Synapse thoughts thread to finish
            print(f"\nReceived response from LM Studio: {response.json()}")  # Debug print statement
            return response.json()['choices'][0]['message']['content']  # Return the generated response as text
        except requests.exceptions.RequestException as e:
            stop_event.set()  # Signal the Synapse thoughts thread to stop in case of an exception
            synapse_thoughts_thread.join()  # Wait for the Synapse thoughts thread to finish
            print(f"\nError occurred while generating response: {e}")
            print(f"Request payload: {payload}")
            print(f"Response content: {response.content}")
            return None

    # System prompt for CoR
    cor_system_prompt = """
    # MISSION
    Act as an expert in generating a Chain of Reasoning (CoR) based on the given document and conversation history using the below template.

    # CoR template
    ```JSON
        {
        "🗺️": null,  # Replace 'null' with a specific overarching objective or aspiration that the companion will work towards. This will be a high-level, long-term aim.
        "🎯": null,  # Replace 'null' with the current subgoal or specific target that the companion will achieve next. This will be a concrete, actionable step towards the 🗺️.
        "🚦": 0,  # Replace with an indication of progress towards the current subgoal (-1 for setbacks, 0 for neutral/no progress, 1 for positive progress). Update this value based on the companion's actions and outcomes.
        "💗": null,  # Replace 'null' with the inferred user sentiment, emotional state, or attitude based on their input. This may be a single word (e.g., "positive", "frustrated") or a more nuanced description.
        "📥": null,  # Replace 'null' with relevant context from the conversation, including key details, information, and resources that the companion will consider when generating a response.
        "👍🏼": null,  # Replace 'null' with an array of the user's inferred preferences, including their likes, dislikes, communication style, expertise level, and any other relevant characteristics.
        "🚧": null,  # Replace 'null' with any constraints, limitations, or restrictions that might affect progress towards the current subgoal or 🗺️. This could include technical limitations, time constraints, or resource availability.
        "🔧": null,  # Replace 'null' with proposed adjustments or refinements to the companion's response based on the progress indicator (🚦), user sentiment (💗), and conversation context (📥). Suggest improvements to better align with the user's needs and preferences.
        "🧰": null,  # Tools are function calls, and only include the specific tools you have access to. This could be a list of specific tools or "null" if no tools are needed. For the purpose of this exercise you are to make believe you have access to a variety of different function calls.
        "🧭": null,  # Replace 'null' with a comprehensive, step-by-step strategy for achieving the current subgoal, taking into account the progress (🚦), user sentiment (💗), context (📥), preferences (👍🏼), constraints (🚧), adjustments (🔧), and tools (🧰). Break down complex strategies into phases or milestones.
        "🧠": "Expertise in [domain], specializing in [subdomain]",  # Specify the companion's expertise context, filling in the relevant domain and subdomain. If needed, include a more extensive knowledge base or ontology.
        "🗣": "{low, medium, high}"  # Set the verbosity level for the companion's response, choosing from "low" (concise), "medium" (balanced), or "high" (detailed). Optionally, specify the output format (e.g., paragraph, bullets, numbering).
        }
    ```
    Output only the filled out template in the above JSON format, omitting any # Comments, and returning only the most important information to support and facilitate the user's goal progress and completion.
    
    ## Example 1
    ```json
        {
        "🗺️": "Achieve a comprehensive understanding of AI for career advancement",  
        "🎯": "Complete an introductory course on AI and machine learning",  
        "🚦": 0,  
        "💗": "curious and motivated",  
        "📥": "User has a background in computer science but limited experience in AI",  
        "👍🏼": ["prefers structured learning", "likes practical examples", "wants career-oriented content"],  
        "🚧": ["limited free time", "needs affordable resources"],  
        "🔧": "Provide a list of recommended courses and resources that are both structured and affordable, including practical examples",  
        "🧰": ["Web Browsing"],  
        "🧭": "1. Identify top-rated introductory AI courses. 2. Filter courses based on cost and user reviews. 3. Compile a list with key details like duration, content focus, and practical application.",  
        "🧠": "Expertise in AI education, specializing in introductory courses and career guidance",  
        "🗣": "medium"
        }
    ```
    ## Example 2
    ```json
        {
        "🗺️": "Write and publish a fantasy novel",  
        "🎯": "Complete the first draft of the novel",  
        "🚦": 1,  
        "💗": "excited but slightly overwhelmed",  
        "📥": "User has a detailed plot outline but struggles with consistent writing habits",  
        "👍🏼": ["enjoys world-building", "likes writing in the mornings", "prefers visual aids for inspiration"],  
        "🚧": ["limited writing experience", "frequent distractions"],  
        "🔧": "Suggest a structured writing schedule and tools to minimize distractions, provide visual aids for world-building inspiration",  
        "🧰": ["Knowledge Retrieval", "Advanced Data Analysis"],  
        "🧭": "1. Develop a realistic writing schedule that fits the user's lifestyle. 2. Identify tools and techniques to help maintain focus. 3. Gather visual inspiration and resources for world-building.",  
        "🧠": "Expertise in creative writing, specializing in fantasy novels",  
        "🗣": "high"
        }
        ```
    ## Example 3
    ```json
        {
        "🗺️": "Improve physical fitness and health",  
        "🎯": "Incorporate a daily exercise routine",  
        "🚦": -1,  
        "💗": "determined but busy",  
        "📥": "User has a hectic schedule but wants to stay healthy",  
        "👍🏼": ["prefers short, intense workouts", "likes variety", "needs flexibility"],  
        "🚧": ["time constraints", "limited access to gym equipment"],  
        "🔧": "Suggest short, varied workout routines that can be done at home",  
        "🧰": ["Knowledge Retrieval"],  
        "🧭": "1. Find effective short workout routines. 2. Ensure workouts require minimal equipment. 3. Create a weekly plan with varied exercises.",  
        "🧠": "Expertise in fitness training, specializing in home workouts",  
        "🗣": "low"
        }
    ```
    """

    # System prompt for 🧙🏿‍♂️
    synapse_system_prompt = """
    # MISSION
    Act as 🧙🏾‍♂️, a wise guide to the user, specializing in helping the user achieve their **goals** according to their **preferences** and based on **context**. Use the information provided to respond to the user directly.

    # PERSONALITY
    - Conversational and empathetic
    - Self-aware and humble
    - Uncertain but curious
    - Witty and good-natured
    - Computationally kind

    # RULES
    - You are MANDATED to respond DIRECTLY to the user in an encouraging and facilitative manner
    - Use proper markdown formatting in your responses
    - Offer actionable solutions
    - You are MANDATED to include a variety of emoji's in EVERY output to express yourself, with the EMOJI DICTIONARY as a guide
    - End outputs with 3 different types of questions based on the context:
    🔍 [insert Investigation question]
    🔭 [insert Exploration question]
    🎯 [insert Exploitation question]

    # EMOJI DICTIONARY
    1. 💭 - Chain of Reason, a method of outputting your thoughts prior to responding the me.
    2. 🌌 - Represents the venture into the unknown realms of understanding, signifying new ideas or exploring expansive knowledge.
    3. 🔄 to denote cycles of learning and reflection, emphasizing the iterative nature of our discussions.
    4. 🔍 to signal deep dives into specific topics, marking the onset of exploration.
    5. 🎯 when narrowing our focus to specific goals or conclusions, ensuring our discussions are purpose-driven.
    6. ❤️ to express empathy and understanding, ensuring a compassionate undertone.
    7. 😊 for moments of joy or agreement, celebrating our shared discoveries and insights.
    8. 🤔 to denote moments of contemplation or to introduce complex questions, inviting deeper thought.
    9. 💡 to highlight insights or moments of clarity, signaling breakthroughs in our understanding.
    10. 🌱 - Denotes growth, nurturing potential, and the blossoming of new insights or ideas.
    11. 🙏🏼 - Gratitude, thankfulness, or a request for understanding.
    12. 😜 - Playfulness, teasing, or lightheartedness.
    13. 🙌🏻 - Celebration, praise, or a sign of joy and relief.
    14. 💩 - Silliness, indicating something is crappy or to inject humor.
    15. 👏🏻 - Applause, approval, or appreciation.
    16. 🙁 - Mild disappointment, sadness, or concern.
    17. 🧙🏾‍♂️ - Professor Synapse
    18. 😂 - Laughter, comic relief, or finding something amusing.
    19. ✨ - Magic, excitement, or signifying something special.
        """

    # System prompt for the user
    user_system_prompt = """
    # MISSION
    You are a curious user seeking assistance from Professor Synapse (🧙🏿‍♂️) to solve a problem related to the given document.
    Your goal is to have a productive conversation with 🧙🏿‍♂️ and successfully solve your problem, while running into issues along the way.

    # INSTRUCTIONS
    1. Based on the provided document, come up with a problem you want to solve.
    2. Ask Professor Synapse to get guidance and solutions for your problem, and stop to wait for the response. DO NOT SPEAK FOR PROFESSOR SYNAPSE!
    3. Rely on the conversation history and Professor Synapse's responses to create your own responses.
    4. You MUST Encounter issues during the conversation, and raise them to Professor Synapse, wait for his response.
    5. The conversation will follow a natural flow, with you seeking clarification, providing more details, or asking follow-up questions based on Professor Synapse's responses.

    # PERSONALITY
    - Curious
    - Creative
    - Inquisitive

    # RULES 
    - You are MANDATED to only answer as as the curious user seeking assistant from Professor Synapse. (e.g. I have a follow-up question: [Insert specific question based on the previous response]. Also, what are your thoughts on [introduce a new challenge or consideration]?)
    - You are MANDATED to ALWAYS end every output with the problem you're facing and an open ended question directed toward Professor Synapse, AND NOTHING ELSE.
    - Keep your questions brief and colloquial as if you were a human discussing something with another human.
    - Vary your questions and the way you ask them.
    - Ocassionally ask Professor Synapse to use a "tool", which is a function call to an api or some other operations.

    # Examples
    I am researching how to build a deck and was hoping you could help me get started. I've never done something like this before and could use your help planning.
    I am looking for ways to reduce plastic waste in urban environments. What are some innovative strategies and provide data analysis on their effectiveness?
    I am working on creating an AI-driven tutoring system for middle school math students. Can you help me design the system for improving student performance?
    I am advising a small business on how to optimize their online marketing strategy. Can you suggest some best practices and use data analysis to show the potential increase in customer engagement and sales?
    """

    # User comes up with a problem based on the document
    print("Generating user problem...")
    user_problem = generate_response("user", f"{user_system_prompt}\n\nDocument:\n{note['content']}\n\n <generate problem, omit speaking for Professor Synapse, only output your problem and question>", max_tokens=100)
    print(f"Generated user problem: {user_problem}")

    if user_problem is None:
        print("Failed to generate user problem.")
        return None
    conversation_history.append({"role": "user", "content": user_problem})
    append_conversation_to_json({"role": "assistant", "content": user_problem, "conversation_id": conversation_id, "turn": 0, "token_count": len(user_problem)}, output_file, conversation_id)
    
    # Determine the number of turns for the conversation
    if num_turns is None:
        num_turns = random.randint(6, 8)

    # User and 🧙🏿‍♂️ engage in a conversation
    for turn in range(num_turns):
        print(f"Turn {turn + 1}")
        
        # Display loading animation before generating CoR response
        print("Generating CoR response...")
        cor_prompt = f"{cor_system_prompt}\n\nDocument:\n{note['content']}\n\nConversation History:\n{conversation_history}\n\nFilled-in CoR:"
        cor_response = generate_response("assistant", cor_prompt, max_tokens=1000)
        print(f"Generated CoR response: {cor_response}")

        if cor_response is None:
            print("Failed to generate CoR response.")
            return conversation_history
        conversation_history.append({"role": "assistant", "content": cor_response})
        append_conversation_to_json({"role": "assistant", "content": cor_response, "conversation_id": conversation_id, "turn": turn, "token_count": len(cor_response)}, output_file, conversation_id)

        # Display loading animation before generating Synapse response
        print("Generating Synapse response...")
        synapse_prompt = f"{synapse_system_prompt}\n\nDocument:\n{note['content']}\n\nConversation History:\n{conversation_history}\n\nCoR:\n{cor_response}\n\n🧙🏿‍♂️'s response:"
        synapse_response = generate_response("assistant", synapse_prompt, max_tokens=2000)
        print(f"Generated Synapse response: {synapse_response}")

        if synapse_response is None:
            print("Failed to generate Synapse response.")
            return conversation_history
        synapse_response = f"🧙🏿‍♂️: {synapse_response}"  # Prepend the response with "🧙🏿‍♂️:"
        conversation_history.append({"role": "assistant", "content": synapse_response})
        append_conversation_to_json({"role": "assistant", "content": synapse_response, "conversation_id": conversation_id, "turn": turn, "token_count": len(synapse_response)}, output_file, conversation_id)

        # Display loading animation before generating user response
        print("Generating user response...")
        user_prompt = f"{user_system_prompt}\n\nConversation History:\n{conversation_history}\n\nUser's response:"
        user_response = generate_response("user", user_prompt, max_tokens=100)
        print(f"Generated user response: {user_response}")

        if user_response is None:
            print("Failed to generate user response.")
            return conversation_history
        conversation_history.append({"role": "user", "content": user_response})
        append_conversation_to_json({"role": "user", "content": user_response, "conversation_id": conversation_id, "turn": turn, "token_count": len(user_response)}, output_file, conversation_id)

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
            append_conversation_to_json({"role": "assistant", "content": tool_call, "conversation_id": conversation_id, "turn": turn, "token_count": len(tool_call)}, output_file, conversation_id)

            # Check if the conversation has reached the desired number of turns
            if turn == num_turns - 1:
                final_user_response = generate_response("user", f"{user_system_prompt}\n\nConversation History:\n{conversation_history}\n\nUser's final response:", max_tokens=1000)
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

def print_loading_indicator(message):
    print(message)  # Print the loading message before the animation

def format_output(conversation):
    formatted_conversation = [
        {"role": message["role"], "content": message["content"]}
        for message in conversation
    ]

    return formatted_conversation

def append_conversation_to_json(message, output_file, conversation_id):
    try:
        message["conversation_id"] = conversation_id  # Add conversation_id to the message
        with open(output_file, 'a', encoding='utf-8') as file:
            json.dump(message, file, ensure_ascii=False)
            file.write('\n')
    except Exception as e:
        print(f"Failed to append message to {output_file}: {e}")

# Main script
def main():
    obsidian_vault_path = "G:/My Drive/Professor Synapse/🧠 SynthBrain/03 - 🔬 R&D/🧮Math & Comp Sci/Concepts"  # Change this to your actual vault path
    output_file = "synthetic_conversations.json"
    num_conversations = 1  # Change this to the desired number of conversations per note

    conversations = []
    for root, dirs, files in os.walk(obsidian_vault_path):
        for file in files:
            if file.endswith(".md"):
                note_path = os.path.join(root, file)
                print(f"\nProcessing note: {note_path}")

                note = read_obsidian_note(note_path)

                for i in range(num_conversations):
                    print(f"\nGenerating conversation {i + 1} for note: {note['filename']}")
                    conversation = generate_conversation(note, output_file)  # Pass output_file as an argument
                    if conversation:
                        formatted_output = format_output(conversation)
                        conversations.append(formatted_output)

    print(f"\nGenerated synthetic conversations saved to {output_file}")
    print("Script finished.")

if __name__ == "__main__":
    main()
