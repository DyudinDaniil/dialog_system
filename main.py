import json
import requests
from typing import Dict, Any


class GameWorld:
    def __init__(self, lore_file: str, locations_file: str, npcs_file: str):
        with open(lore_file, 'r', encoding='utf-8') as f:
            self.lore = f.read().strip()
        with open(locations_file, 'r', encoding='utf-8') as f:
            self.locations = json.load(f)
        with open(npcs_file, 'r', encoding='utf-8') as f:
            self.npcs = json.load(f)

    def get_location_info(self, location_name: str) -> Dict[str, Any]:
        return self.locations.get(location_name, {})

    def get_npc_info(self, npc_name: str) -> Dict[str, Any]:
        return self.npcs.get(npc_name, {})

    def get_npcs_in_location(self, location_name: str) -> list:
        return self.locations.get(location_name, {}).get("npcs", [])


class DialogueSystem:
    def __init__(self, lore_file: str, locations_file: str, npcs_file: str):
        self.world = GameWorld(lore_file, locations_file, npcs_file)
        self.current_location = None
        self.current_npc = None
        self.player_reputation = None

    def start_chat(self):
        print("Welcome to the game dialogue system!")
        self.current_location = self.choose_location()
        self.player_reputation = self.choose_reputation()
        self.current_npc = self.choose_npc()

        print(f"\nLocation: {self.current_location}")
        print(f"Your reputation: {self.player_reputation}")
        print(f"Talking to: {self.current_npc}\n")

        self.run_dialogue()

    def choose_location(self) -> str:
        locations = list(self.world.locations.keys())
        print("\nAvailable locations:")
        for i, loc in enumerate(locations, 1):
            print(f"{i}. {loc}")
        while True:
            try:
                choice = int(input("Select location (number): ")) - 1
                return locations[choice]
            except (ValueError, IndexError):
                print("Invalid input. Try again.")

    def choose_reputation(self) -> str:
        reputations = self.world.get_location_info(self.current_location)["reputation_levels"]
        print("\nSelect your reputation:")
        for i, rep in enumerate(reputations, 1):
            print(f"{i}. {rep}")
        while True:
            try:
                choice = int(input("Your choice (number): ")) - 1
                return reputations[choice]
            except (ValueError, IndexError):
                print("Invalid input. Try again.")

    def choose_npc(self) -> str:
        npcs = self.world.get_npcs_in_location(self.current_location)
        print("\nAvailable NPCs:")
        for i, npc in enumerate(npcs, 1):
            desc = self.world.get_npc_info(npc)["backstory"]
            print(f"{i}. {npc} ({desc})")
        while True:
            try:
                choice = int(input("Select NPC (number): ")) - 1
                return npcs[choice]
            except (ValueError, IndexError):
                print("Invalid input. Try again.")

    def run_dialogue(self):
        npc_info = self.world.get_npc_info(self.current_npc)
        location_info = self.world.get_location_info(self.current_location)

        # Get attitude and greeting based on reputation
        attitude = npc_info["attitude"].get(self.player_reputation, "neutral")
        greeting = npc_info["greetings"].get(attitude, "Hello traveler.")

        context = (
            f"You are {self.current_npc}, {npc_info['backstory']}. "
            f"Current attitude: {attitude}. "
            f"Location context: {location_info['description']}. "
            f"World lore: {self.world.lore}\n"
            "Respond briefly (1-2 sentences). Keep character consistent.\n"
            "Current conversation:\n"
        )

        print(f"\n{self.current_npc}: {greeting}")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Dialogue ended.")
                break

            prompt = f"{context}Player: {user_input}\n{self.current_npc}:"
            response = self.generate_response(prompt)
            print(f"{self.current_npc}: {response}")

    def generate_response(self, prompt: str) -> str:
        api_url = "http://localhost:11434/api/chat"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "llama3",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": 0.7
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()["message"]["content"]
            return f"API Error: {response.text}"
        except Exception as e:
            return f"Error: {str(e)}"


if __name__ == "__main__":
    system = DialogueSystem(
        lore_file="game_lore.txt",
        locations_file="locations.json",
        npcs_file="npcs.json"
    )
    system.start_chat()