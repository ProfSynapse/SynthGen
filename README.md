# Synthetic Conversation Generator
Welcome to the Synthetic Conversation Generator! This project helps you read notes from Obsidian and generate synthetic conversations based on the content of those notes using a language model.

## Description
This project provides tools to read notes from Obsidian and generate synthetic conversations based on the content of those notes. It uses a language model to simulate interactions and generate responses, making it ideal for creating training data, testing dialogue systems, or exploring conversational AI capabilities.

## Installation
Make sure you have [VS Code](https://code.visualstudio.com/download) downloaded and the latest version of [Python](https://www.python.org/downloads/).

You will also need to download [LM Studio](https://lmstudio.ai/). This code uses local models to generate the synthetic data, which means you will need to download a model, and identify it in the code. This also means you will need a GPU that can run the model locally.

### Step 1: Get the code into VS Code
To get started, choose one of the following:

1. Clone the Repository in VS code by opening a new window (file>new window) and pasting the below link into the top search bar that pops up:
```
https://github.com/ProfSynapse/Synth_Prof.git
```

OR

2. Download the zip version by clicking `<> Code` in the top right, and clicking the **Download .zip**. Uncompress and save to a folder you have easy access to, or one to keep your code in.

*Note: Make sure the folder isn't doubled up (e.g. Synth_Prof folder is inside another Synth_Prof Folder)*

### Step 2: Set Up a Virtual Environment in VS Code
1. Open a new terminal (terminal>new), and type:
`python -m venv venv`
2. Click Enter/Return
3. Then for MAC:
`source venv/bin/activate`

On Windows
`venv\Scripts\activate`

### Step 3: Install Dependencies
Type
`pip install -r requirements.txt`

### Step 4: Choose your Model
1. Download your preferred model in LM Studio, and open the local server tab (it looks kind of like ⬅️➡️).
2. Set your context length, make sure GPU Offload is on and set it somewhere in the middle.
3. Take note of the server port (probably 1234) and make sure that lines up in the code where it says `http://localhost:1234/v1/chat/completions`
4. Make sure the name of the model you chose is the same in LM Studio and the code. Example if I chose the Phi 3 Medium model (as it is in the code) it should look like the following:
   `"model": "bartowski/Phi-3-medium-128k-instruct-GGUF"`

### Step 5: Find the path to your note
Ensure you have an Obsidian note (.md file) you want to read and generate conversations from. Update the path in the script accordingly where it says:
`INSERT_NOTE_PATH`

An example path my looks like **C:/Users/Name/Documents/My Vault/Note1.md**

### Step 6: Run the Main Script:
Execute the main script to generate synthetic conversations.

In your terminal type:
`python gen_prof.py`

You can watch it generate the conversations in LM Studio

# Step 7: Check the Output
The generated conversations will be saved to a JSON file specified in the script (synthetic_conversations.json by default) in the VS code folder.
