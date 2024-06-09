# Synthetic Conversation Generator
Welcome to the Synthetic Conversation Generator! This project helps you read notes from Obsidian and generate synthetic conversations based on the content of those notes using a language model.

## Description
This project provides tools to read notes from Obsidian and generate synthetic conversations based on the content of those notes. It uses a language model to simulate interactions and generate responses, making it ideal for creating training data, testing dialogue systems, or exploring conversational AI capabilities.

## Installation
Make sure you have [VS Code](https://code.visualstudio.com/download) downloaded and the latest version of [Python](https://www.python.org/downloads/).

You will also need to download [LM Studio](https://lmstudio.ai/) if you want to run locally. This code optionally uses local models to generate the synthetic data, which means you will need to download a model, and identify it in the code. This also means you will need a GPU that can run the model locally.

### Step 1: Get the code into VS Code
To get started, choose one of the following:

1. Clone the Repository in VS code by opening a new window (file>new window) and pasting the below link into the top search bar that pops up:
```
https://github.com/ProfSynapse/Synth_Prof.git
```

OR

2. Download the zip version by clicking `<> Code` in the top right, and clicking the **Download .zip**. Uncompress and save to a folder you have easy access to, or one to keep your code in. Go into VS code and open a new folder (File>New Folder) and open the actual folder into the environment.

*Note: Make sure the folder isn't doubled up (e.g. Synth_Prof folder is inside another Synth_Prof Folder)*

### Step 2: Choose your Model
1. Download your preferred model in LM Studio, and open the local server tab (it looks kind of like ⬅️➡️).
2. Set your context length, make sure GPU Offload is on and set it somewhere in the middle.
3. Take note of the server port (probably 1234) and make sure that lines up in the code where it says `http://localhost:1234/v1/chat/completions`
4. Make sure the name of the model you chose is the same in LM Studio and the code. Example if I chose the Phi 3 Medium model (as it is in the code) it should look like the following:
   `"model": "bartowski/Phi-3-medium-128k-instruct-GGUF"`

   OR

If you plan to use OpenAI for the generations:
1. Create an API key from your [OpenAI account](https://platform.openai.com/api-keys) (note you will need to set up billing as this will cost money).
2. Create `.env` file and type in OPENAI_API_KEY=insert_your_API_Key_here

### Step 3: Find the path to your note folder
Ensure you have an Obsidian note folder filled with .md file you want to read and generate conversations from in the `config.yaml` file. Update the path in the script accordingly where it says:
`obsidian_vault_path:`

An example path my looks like **C:/Users/Name/Documents/My Vault/My Folder**

Optionally you can also change the `num_conversations:`, which will run a conversation on each note that number of times. It is set to 1 by default.

### Step 4 (optional):
1. Update the `generation_parameters`, which include the max tokens depending on who's generating (user, chain of reason, or the professor)
2. Update the `conversation_generation` `num_conversations` - this will define the number of conversations you want to generate about each note.
3. Update the `[model]_details` by changing the model name in "" to the model you want from that provider. You can find the proper names of models by googling them.

### Step 5: Update your prompts
In the `config.yaml` file you will see 3 different system prompts:
1. **cor_system_prompt**: I would not recommend changing this, as I would like to keep it standardized, but this is the chain of reason module, that will generate prior to the assistant output (in this case the Professor). That being said, feel free to experiment to see if there is a way you prefer the chain of reason to generate.
2. **synapse_system_prompt**: Right now this is set to the Professor and my preferences, but think of this as a fill in the blank worksheet. Under each "# HEADING" you can change things to your liking. Something things to consider:
   - Replace the Professor and his emoji's with your own name for an assistant throughout the prompt
   - Replace my name with your name
   - Update the context to include things about yourself
   - Update all of the traits like personality, philosophy, and values
   - Change the output samples to align more with how you want your assistant to talk
3. **user_system_prompt**: Similar to the Synapse prompt, update this one to make it all about you! In particular update the "# CHARACTER" section, and replace my name and the Professors with yours and your assistant.

### Step 6: Set Up a Virtual Environment in VS Code
1. Open a new terminal (terminal>new), and type:
`python -m venv venv`
2. Click Enter/Return
3. Then for MAC:
`source venv/bin/activate`

On Windows
`venv\Scripts\activate`

### Step 5: Install Dependencies
Type
`pip install -r requirements.txt`

### Step 7: Run the Main Script:
In your terminal, execute the main script to generate synthetic conversations.

In your terminal type:
`python main.py`

Choose the model you want to use.

You can watch it generate the conversations in LM Studio, or it will output directly into the terminal for openai.

# Step 7: Check the Output
The generated conversations will be saved to a JSON file specified in the script (synthetic_conversations.json by default) in the VS code folder.
