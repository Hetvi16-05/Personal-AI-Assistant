import json
import os

MEMORY_FILE = "data/memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def add_memory(text):
    memory = load_memory()
    memory.append(text)
    save_memory(memory)

def get_memory():
    return load_memory()
