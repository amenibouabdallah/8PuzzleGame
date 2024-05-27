import tkinter as tk
from tkinter import messagebox, font
import random
from queue import Queue
import heapq
import time

# Configuration du jeu 8-puzzle
goal_state = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # État final du jeu (case vide représentée par 0)
grid_size = 3  # Taille de la grille 3x3

# Générer un état initial aléatoire et vérifiable
def generate_random_state():
    state = list(range(9))  # Liste de 0 à 8
    random.shuffle(state)  # Mélangez les tuiles pour créer un état aléatoire

    # Vérifiez si l'état mélangé est solvable
    while not is_solvable(state):
        random.shuffle(state)

    return state

# Vérifiez si un état est solvable
def is_solvable(state):
    inversions = 0
    for i in range(len(state)):
        for j in range(i + 1, len(state)):
            if state[i] > state[j] and state[i] != 0 and state[j] != 0:
                inversions += 1
    return inversions % 2 == 0

# Convertit l'état à un index de grille
def state_to_grid_indices(state):
    return [state[i * grid_size:(i + 1) * grid_size] for i in range(grid_size)]

# Classe pour créer l'interface graphique du jeu 8-puzzle
class PuzzleGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8-Puzzle Game")
        self.configure(bg="#112b52")

        # Initialize play_again_button as None initially
        self.play_again_button = None

        # Générer un état initial aléatoire
        self.state = generate_random_state()
        
        # Créer la grille à partir de l'état initial
        self.grid = state_to_grid_indices(self.state)

        # Charger la police "Poppins"
        self.poppins_font = font.Font(family="Poppins", size=14)

        # Définir des couleurs pour l'interface
        self.bg_color = "#112b52"  # Couleur de fond
        self.tile_color = "#d3d3d3"  # Couleur des tuiles
        self.empty_tile_color = "#ffffff"  # Couleur de la case vide
       
        
        # Créez la grille dans la fenêtre principale
        self.grid_frame = tk.Frame(self, bg=self.bg_color)
        self.grid_frame.grid(row=0, column=0, padx=20, pady=20)

        # Créez les boutons pour chaque case de la grille
        self.buttons = []
        for i in range(grid_size):
            row_buttons = []
            for j in range(grid_size):
                value = self.grid[i][j]
                text = str(value) if value != 0 else ""
                tile_color = self.tile_color if value != 0 else self.empty_tile_color
                button = tk.Button(
                    self.grid_frame,
                    text=text,
                    font=self.poppins_font,
                    width=6,
                    height=2,
                    bg=tile_color,
                    fg="#000000",
                    
                    command=lambda r=i, c=j: self.on_tile_click(r, c),
                    
                )
                button.grid(row=i, column=j, padx=5, pady=5)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

        # Créez les labels pour les informations de jeu
        self.info_frame = tk.Frame(self, bg=self.bg_color)
        self.info_frame.grid(row=0, column=1, padx=20, pady=20)

        self.moves_label = tk.Label(self.info_frame, text="Moves: 0", font=self.poppins_font, bg=self.bg_color, fg="#ffffff")
        self.moves_label.pack(anchor="w")

        self.time_label = tk.Label(self.info_frame, text="Time: 0 seconds", font=self.poppins_font, bg=self.bg_color, fg="#28a745")
        self.time_label.pack(anchor="w")

        self.moves_used_label = tk.Label(self.info_frame, text="Moves used: ", font=self.poppins_font, bg=self.bg_color, fg="#28a745")
        self.moves_used_label.pack(anchor="w")

        self.status_label = tk.Label(self.info_frame, text="", font=self.poppins_font, bg=self.bg_color, fg="#ffffff")
        self.status_label.pack(anchor="w")

        # Créez les boutons pour les actions de jeu
        self.actions_frame = tk.Frame(self, bg=self.bg_color)
        self.actions_frame.grid(row=1, column=0, columnspan=2, pady=20)

        self.solve_manual_button = tk.Button(self.actions_frame, text="Solve Manually", font=self.poppins_font, bg="#007bff", fg="#ffffff", command=self.solve_manual)
        self.solve_manual_button.grid(row=0, column=0, padx=10, pady=10)

        self.reset_button = tk.Button(self.actions_frame, text="Reset", font=self.poppins_font, bg="#28a745", fg="#ffffff", command=self.restart_game)
        self.reset_button.grid(row=0, column=1, padx=10, pady=10)

        self.shuffle_button = tk.Button(self.actions_frame, text="Shuffle", font=self.poppins_font, bg="#dc3545", fg="#ffffff", command=self.shuffle_game)
        self.shuffle_button.grid(row=0, column=2, padx=10, pady=10)

        self.solve_astar_button = tk.Button(self.actions_frame, text="Solve using A* algorithm", font=self.poppins_font, bg="#fd7e14", fg="#ffffff", command=self.solve_puzzle_astar)
        self.solve_astar_button.grid(row=0, column=3, padx=10, pady=10)

        self.solve_bfs_button = tk.Button(self.actions_frame, text="Solve using BFS algorithm", font=self.poppins_font, bg="#28a745", fg="#ffffff", command=self.solve_puzzle_bfs)
        self.solve_bfs_button.grid(row=0, column=4, padx=10, pady=10)


        # Initialize variables for tracking moves and time
        self.moves_count = 0
        self.start_time = None
        self.timer_running = False

        # Liez les événements de touches à l'interface
        self.bind("<Up>", self.move_empty_tile)
        self.bind("<Down>", self.move_empty_tile)
        self.bind("<Left>", self.move_empty_tile)
        self.bind("<Right>", self.move_empty_tile)

    # Met à jour la grille avec l'état actuel
    def update_grid(self):
        for i in range(grid_size):
            for j in range(grid_size):
                value = self.grid[i][j]
                text = str(value) if value != 0 else ""
                tile_color = self.tile_color if value != 0 else self.empty_tile_color
                if self.buttons[i][j]:  # Check if the button still exists
                    self.buttons[i][j].configure(text=text, bg=tile_color)

    # Gère le clic sur une tuile
    def on_tile_click(self, row, col):
        if not self.timer_running:
            self.start_timer()
        
        empty_row, empty_col = self.find_empty_tile()

        # Vérifiez si la tuile cliquée est adjacente à la case vide
        if (abs(empty_row - row) == 1 and empty_col == col) or (abs(empty_col - col) == 1 and empty_row == row):
            # Déplacez la tuile cliquée dans la case vide
            self.grid[empty_row][empty_col], self.grid[row][col] = self.grid[row][col], self.grid[empty_row][empty_col]
            self.moves_count += 1
            self.update_grid()
            self.update_moves_label()

            # Vérifiez si l'utilisateur a résolu le puzzle
            if self.is_goal_state():
                self.show_victory_message()

    # Trouvez la position de la case vide
    def find_empty_tile(self):
        for i in range(grid_size):
            for j in range(grid_size):
                if self.grid[i][j] == 0:
                    return i, j

    # Vérifiez si l'état actuel est l'état final
    def is_goal_state(self):
        current_state = [self.grid[i][j] for i in range(grid_size) for j in range(grid_size)]
        return current_state == goal_state

    # Affiche un message de victoire avec un bouton "Jouer à nouveau"
    def show_victory_message(self):
        self.stop_timer()
        self.update_status_label("Congratulations! You solved the puzzle!")
        messagebox.showinfo("Victory", "Congratulations! You solved the puzzle!")
        
        # Disable Solve and Shuffle buttons
        self.solve_manual_button.config(state=tk.DISABLED)
        self.shuffle_button.config(state=tk.DISABLED)
        self.solve_astar_button.config(state=tk.DISABLED)
        self.solve_bfs_button.config(state=tk.DISABLED)
        
        # Remove the existing Play Again button if it exists
        if self.play_again_button:
            self.play_again_button.destroy()

        # Create a Play Again button
        self.play_again_button = tk.Button(self.actions_frame, text="Play Again", font=self.poppins_font, bg="#ffc107", fg="#000000", command=self.play_again)
        self.play_again_button.grid(row=1, column=0, columnspan=6, pady=10)

    # Redémarrer le jeu avec un nouvel état aléatoire
    def restart_game(self):
        self.state = generate_random_state()
        self.grid = state_to_grid_indices(self.state)
        self.moves_count = 0
        self.update_grid()
        self.update_moves_label()
        self.update_status_label("")
        self.reset_timer()
        self.start_timer()
        self.moves_used_label.config(text="")
        self.timer_running = False

        # Enable Solve and Shuffle buttons
        self.solve_manual_button.config(state=tk.NORMAL)
        self.shuffle_button.config(state=tk.NORMAL)
        self.solve_astar_button.config(state=tk.NORMAL)
        self.solve_bfs_button.config(state=tk.NORMAL)

    # Mélanger le jeu
    def shuffle_game(self):
        self.restart_game()

    # Met à jour l'étiquette du nombre de mouvements
    def update_moves_label(self):
        self.moves_label.config(text=f"Moves: {self.moves_count}")

    # Met à jour l'étiquette de l'état du jeu
    def update_status_label(self, status):
        self.status_label.config(text=status)

    # Commence le minuteur
    def start_timer(self):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

    # Met à jour le minuteur
    def update_timer(self):
        if self.timer_running:
            elapsed_time = int(time.time() - self.start_time)
            self.time_label.config(text=f"Time: {elapsed_time} seconds")
            self.after(1000, self.update_timer)

    # Arrête le minuteur
    def stop_timer(self):
        self.timer_running = False

    # Réinitialise le minuteur
    def reset_timer(self):
        self.start_time = None
        self.timer_running = False
        self.time_label.config(text="Time: 0 seconds")

    # Joue à nouveau
    def play_again(self):
        self.restart_game()
        if self.play_again_button:
            self.play_again_button.destroy()

    # Déplace la case vide en réponse aux touches fléchées
    def move_empty_tile(self, event):
        if not self.timer_running:
            self.start_timer()
        
        empty_row, empty_col = self.find_empty_tile()
        if event.keysym == "Up" and empty_row < grid_size - 1:
            self.on_tile_click(empty_row + 1, empty_col)
        elif event.keysym == "Down" and empty_row > 0:
            self.on_tile_click(empty_row - 1, empty_col)
        elif event.keysym == "Left" and empty_col < grid_size - 1:
            self.on_tile_click(empty_row, empty_col + 1)
        elif event.keysym == "Right" and empty_col > 0:
            self.on_tile_click(empty_row, empty_col - 1)

    # Implémentation de l'algorithme de résolution manuelle (juste un exemple)
    def solve_manual(self):
        messagebox.showinfo("Manual Solver", "Please use the arrow keys to solve the puzzle manually.")

    # Implémentation de l'algorithme A* pour résoudre le puzzle
    def solve_puzzle_astar(self):
        start_state = [self.grid[i][j] for i in range(grid_size) for j in range(grid_size)]
        solution = self.a_star_search(start_state)
        self.display_solution(solution)

    # Implémentation de l'algorithme BFS pour résoudre le puzzle
    def solve_puzzle_bfs(self):
        start_state = [self.grid[i][j] for i in range(grid_size) for j in range(grid_size)]
        solution = self.bfs_search(start_state)
        self.display_solution(solution)


    # Fonction pour afficher la solution trouvée
    def display_solution(self, solution):
        if not solution:
            messagebox.showinfo("No Solution", "No solution found.")
            return

        for move in solution['moves']:
            row, col, direction = move
            self.on_tile_click(row, col)
            self.update()
            time.sleep(0.5)  # Pause pour visualiser chaque mouvement

        self.show_victory_message()
        self.moves_used_label.config(text=f"Moves used: {solution['moves']}",wraplength=561)

    # Fonction de recherche A* pour résoudre le puzzle
    def a_star_search(self, start_state):
        def heuristic(state):
            return sum(abs((val - 1) % grid_size - j) + abs((val - 1) // grid_size - i)
                       for i, row in enumerate(state) for j, val in enumerate(row) if val)

        def get_neighbors(state):
            empty_row, empty_col = next((i, j) for i, row in enumerate(state) for j, val in enumerate(row) if val == 0)
            neighbors = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = empty_row + dr, empty_col + dc
                if 0 <= nr < grid_size and 0 <= nc < grid_size:
                    new_state = [list(row) for row in state]
                    new_state[empty_row][empty_col], new_state[nr][nc] = new_state[nr][nc], new_state[empty_row][empty_col]
                    neighbors.append((new_state, (nr, nc, 'Up' if dr == -1 else 'Down' if dr == 1 else 'Left' if dc == -1 else 'Right')))
            return neighbors

        start = state_to_grid_indices(start_state)
        goal = state_to_grid_indices(goal_state)

        open_set = []
        heapq.heappush(open_set, (0 + heuristic(start), 0, start, []))
        closed_set = set()

        while open_set:
            _, cost, current_state, path = heapq.heappop(open_set)
            if current_state == goal:
                return {'moves': path, 'cost': cost}

            closed_set.add(tuple(tuple(row) for row in current_state))

            for neighbor, move in get_neighbors(current_state):
                neighbor_tuple = tuple(tuple(row) for row in neighbor)
                if neighbor_tuple not in closed_set:
                    heapq.heappush(open_set, (cost + 1 + heuristic(neighbor), cost + 1, neighbor, path + [move]))

        return None

    # Fonction de recherche BFS pour résoudre le puzzle
    def bfs_search(self, start_state):
        def get_neighbors(state):
            empty_row, empty_col = next((i, j) for i, row in enumerate(state) for j, val in enumerate(row) if val == 0)
            neighbors = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = empty_row + dr, empty_col + dc
                if 0 <= nr < grid_size and 0 <= nc < grid_size:
                    new_state = [list(row) for row in state]
                    new_state[empty_row][empty_col], new_state[nr][nc] = new_state[nr][nc], new_state[empty_row][empty_col]
                    neighbors.append((new_state, (nr, nc, 'Up' if dr == -1 else 'Down' if dr == 1 else 'Left' if dc == -1 else 'Right')))
            return neighbors

        start = state_to_grid_indices(start_state)
        goal = state_to_grid_indices(goal_state)

        queue = Queue()
        queue.put((start, []))
        visited = set()

        while not queue.empty():
            current_state, path = queue.get()
            if current_state == goal:
                return {'moves': path}

            visited.add(tuple(tuple(row) for row in current_state))

            for neighbor, move in get_neighbors(current_state):
                neighbor_tuple = tuple(tuple(row) for row in neighbor)
                if neighbor_tuple not in visited:
                    queue.put((neighbor, path + [move]))

        return None

   

# Démarrez le jeu
if __name__ == "__main__":
    game = PuzzleGame()
    game.mainloop()
