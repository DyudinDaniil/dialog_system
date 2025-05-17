import json
import requests
import time
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Any
from datetime import datetime


class GameWorld:
    def __init__(self, lore_file: str, locations_file: str, npcs_file: str):
        with open(lore_file, 'r', encoding='utf-8') as f:
            self.lore = f.read().strip()

        # Загрузка с обработкой ошибок
        try:
            with open(locations_file, 'r', encoding='utf-8') as f:
                self.locations = json.load(f)
        except Exception as e:
            print(f"Error loading locations: {e}")
            self.locations = {}

        try:
            with open(npcs_file, 'r', encoding='utf-8') as f:
                self.npcs = json.load(f)
        except Exception as e:
            print(f"Error loading NPCs: {e}")
            self.npcs = {}

    def get_location_info(self, location_name: str) -> Dict[str, Any]:
        return self.locations.get(location_name, {})

    def get_npc_info(self, npc_name: str) -> Dict[str, Any]:
        # Возвращаем полную информацию о NPC или пустой словарь
        return self.npcs.get(npc_name, {})

    def get_npcs_in_location(self, location_name: str) -> List[str]:
        # Безопасное получение списка NPC для локации
        location = self.locations.get(location_name, {})
        return location.get("npcs", [])

    def visualize_relations(self):
        G = nx.Graph()

        # Добавляем NPC как узлы с проверкой наличия backstory
        for npc_name, npc_data in self.npcs.items():
            backstory = npc_data.get('backstory', 'No backstory available')
            G.add_node(npc_name, backstory=backstory)

        # Добавляем отношения с проверкой наличия
        for npc_name, npc_data in self.npcs.items():
            if 'relations' in npc_data:
                for relation in npc_data['relations']:
                    if 'target' in relation and 'type' in relation and 'value' in relation:
                        G.add_edge(npc_name, relation['target'],
                                   weight=relation['value'],
                                   type=relation['type'])

        # Создаем фигуру
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=42)  # Фиксируем seed для стабильности

        # Подготовка данных для визуализации
        node_labels = {}
        for node, data in G.nodes(data=True):
            backstory = data.get('backstory', '')
            node_labels[node] = f"{node}\n({backstory[:30]}...)" if backstory else node

        edge_colors = []
        edge_widths = []
        for u, v, d in G.edges(data=True):
            if 'weight' in d:
                edge_colors.append('green' if d['weight'] > 0 else 'red')
                edge_widths.append(abs(d['weight']) * 3)

        # Рисуем граф
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='skyblue', alpha=0.9)
        nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_colors, alpha=0.7)
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)

        # Добавляем подписи к ребрам
        edge_labels = {}
        for u, v, d in G.edges(data=True):
            if 'type' in d:
                edge_labels[(u, v)] = d['type']

        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

        plt.title("NPC Relationship Network")
        plt.axis('off')
        plt.tight_layout()

        # Сохраняем граф в файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relations_graph_{timestamp}.png"
        plt.savefig(filename)
        print(f"Graph saved as {filename}")

        plt.show()


class DialogueSystem:
    def __init__(self, lore_file: str, locations_file: str, npcs_file: str):
        self.world = GameWorld(lore_file, locations_file, npcs_file)
        self.current_location = None
        self.current_npc = None
        self.player_reputation = None
        self.dialogue_history = []
        self.max_history_length = 5
        self.analytics_data = {
            "dialogues": [],
            "response_times": [],
            "npc_interactions": {}
        }

    def start_chat(self):
        if not self.world.locations or not self.world.npcs:
            print("Error: Failed to load game data. Please check JSON files.")
            return
        print("Welcome to the game dialogue system!")
        self.current_location = self.choose_location()
        self.player_reputation = self.choose_reputation()
        self.current_npc = self.choose_npc()

        # Инициализация аналитики для NPC
        if self.current_npc not in self.analytics_data["npc_interactions"]:
            self.analytics_data["npc_interactions"][self.current_npc] = {
                "count": 0,
                "total_response_time": 0
            }

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
            npc_info = self.world.get_npc_info(npc)
            # Безопасное получение backstory с значением по умолчанию
            desc = npc_info.get("backstory", "No description available")
            print(f"{i}. {npc} ({desc[:50]}...)")  # Ограничиваем длину описания
        while True:
            try:
                choice = int(input("Select NPC (number): ")) - 1
                if 0 <= choice < len(npcs):
                    return npcs[choice]
                print("Invalid number. Try again.")
            except ValueError:
                print("Please enter a valid number.")

    def run_dialogue(self):
        npc_info = self.world.get_npc_info(self.current_npc)
        greeting = npc_info.get("greetings", {}).get(self.player_reputation, "Hello traveler.")

        print(f"\n{self.current_npc}: {greeting}")

        while True:
            user_input = input("You: ").strip().lower()

            if user_input == "exit":
                print("Dialogue ended.")
                break
            elif user_input == "show relations":
                try:
                    self.world.visualize_relations()
                except Exception as e:
                    print(f"Error visualizing relations: {str(e)}")
                continue
            elif user_input == "show analytics":
                self.display_analytics()
                continue

            # Добавляем в историю (с ограничением длины)
            self.dialogue_history.append(f"Player: {user_input}")
            if len(self.dialogue_history) > self.max_history_length:
                self.dialogue_history.pop(0)

            # Формируем контекст с историей
            context = (
                f"You are {self.current_npc}, {npc_info['backstory']}. "
                f"Player reputation: {self.player_reputation}. "
                f"Recent conversation history:\n{'\n'.join(self.dialogue_history)}\n"
                f"World context: {self.world.lore}\n"
                "Respond briefly (1-2 sentences). Keep character consistent."
            )

            # Генерация ответа с замером времени
            start_time = time.time()
            response = self.generate_response(f"{context}\nNPC:")
            response_time = time.time() - start_time

            # Сохраняем аналитику
            self.record_analytics(user_input, response, response_time)

            print(f"{self.current_npc}: {response}")
            self.dialogue_history.append(f"{self.current_npc}: {response}")

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

    def record_analytics(self, user_input: str, response: str, response_time: float):
        timestamp = datetime.now().isoformat()

        # Запись диалога
        self.analytics_data["dialogues"].append({
            "timestamp": timestamp,
            "npc": self.current_npc,
            "player_input": user_input,
            "npc_response": response,
            "response_time": response_time
        })

        # Статистика по NPC
        npc_stats = self.analytics_data["npc_interactions"][self.current_npc]
        npc_stats["count"] += 1
        npc_stats["total_response_time"] += response_time

        # Общая статистика по времени ответа
        self.analytics_data["response_times"].append(response_time)

    def display_analytics(self):
        print("\n=== Dialogue Analytics ===")

        # Общая статистика
        total_interactions = sum(stats["count"] for stats in self.analytics_data["npc_interactions"].values())
        avg_response_time = sum(self.analytics_data["response_times"]) / len(self.analytics_data["response_times"]) if \
        self.analytics_data["response_times"] else 0

        print(f"Total interactions: {total_interactions}")
        print(f"Average response time: {avg_response_time:.2f}s")

        # Статистика по NPC
        print("\nNPC Interaction Stats:")
        for npc, stats in self.analytics_data["npc_interactions"].items():
            avg_time = stats["total_response_time"] / stats["count"] if stats["count"] > 0 else 0
            print(f"- {npc}: {stats['count']} dialogues, avg response {avg_time:.2f}s")

        # Последние 3 диалога
        print("\nRecent Dialogues:")
        for dialogue in self.analytics_data["dialogues"][-3:]:
            print(f"[{dialogue['timestamp']}] Player: {dialogue['player_input']}")
            print(f"    {dialogue['npc']}: {dialogue['npc_response']} ({dialogue['response_time']:.2f}s)")


if __name__ == "__main__":
    system = DialogueSystem(
        lore_file="game_lore.txt",
        locations_file="locations.json",
        npcs_file="npcs.json"
    )

    try:
        system.start_chat()
    except KeyboardInterrupt:
        print("\nFinal Analytics Summary:")
        system.display_analytics()