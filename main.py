import pygame
import sys
import os
import math

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna gry
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Gra Point-and-Click z Siatką")

# Inicjalizacja postaci
player_image_paths = [f"ruch{i}.png" for i in range(1, 9)]
player_images = [pygame.transform.scale(pygame.image.load(os.path.join("images", img)), (100, 100)) for img in
                 player_image_paths]
player_images_flipped = [pygame.transform.flip(image, True, False) for image in player_images]  # Lustrzane odbicie
player_rect = player_images[0].get_rect()
player_rect.topleft = (100, height // 2)
player_speed = 2

# Inicjalizacja tła
background = pygame.image.load("background.png")
background_rect = background.get_rect()

# Ustawienia animacji
animation_speed = 0.2  # Szybkość animacji
animation_count = 0
moving = False
moving_direction = 1  # 1 dla prawo, -1 dla lewo

# Definicja siatki
cell_size = 100  # Rozmiar pojedynczego kwadratu (100x100)

# Definicja mapy dozwolonych obszarów (0 - można iść, 1 - przeszkoda)
movement_map = [
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

# Obliczanie liczby wierszy i kolumn
rows = len(movement_map)  # Ustal liczbę wierszy
cols = len(movement_map[0]) if rows > 0 else 0  # Ustal liczbę kolumn


# Obliczenie możliwych ruchów
def get_neighbors(position):
    neighbors = []
    x, y = position
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Lewo, Prawo, Góra, Dół
        nx, ny = x + dx, y + dy
        if 0 <= nx < cols and 0 <= ny < rows and movement_map[ny][nx] == 0:
            neighbors.append((nx, ny))
    return neighbors


# Algorytm A* do znajdowania najkrótszej ścieżki
def a_star(start, goal):
    open_set = {start}
    came_from = {}

    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))

        if current == goal:
            return reconstruct_path(came_from, current)

        open_set.remove(current)
        for neighbor in get_neighbors(current):
            tentative_g_score = g_score[current] + 1  # Przykład: koszt ruchu 1
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                open_set.add(neighbor)

    return []


# Funkcja heurystyczna do A*
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan Distance


# Rekonstrukcja ścieżki
def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path[::-1]  # Odwróć, aby uzyskać od początku do końca


# Główna pętla gry
clock = pygame.time.Clock()
running = True
target_cell = None
path = []

# Zmienne do śledzenia kliknięć
feedback_position = None
feedback_color = None
feedback_time = 0

while running:
    # Obsługa zdarzeń
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Ustalanie celu na siatkę w miejscu kliknięcia
            mouse_x, mouse_y = event.pos
            target_cell = (mouse_x // cell_size, mouse_y // cell_size)

            # Sprawdzanie, co kliknięto
            if 0 <= target_cell[0] < cols and 0 <= target_cell[1] < rows:
                if movement_map[target_cell[1]][target_cell[0]] == 1:
                    # Kliknięcie na przeszkodę
                    feedback_color = (255, 0, 0)  # Czerwony
                    feedback_position = (target_cell[0] * cell_size + cell_size // 2,
                                         target_cell[1] * cell_size + cell_size // 2)  # Środek kwadratu
                    feedback_time = pygame.time.get_ticks()  # Ustaw czas wyświetlania
                elif movement_map[target_cell[1]][target_cell[0]] == 0:
                    # Kliknięcie na dozwolony obszar
                    feedback_color = (0, 255, 0)  # Zielony
                    feedback_position = (target_cell[0] * cell_size + cell_size // 2,
                                         target_cell[1] * cell_size + cell_size // 2)  # Środek kwadratu
                    feedback_time = pygame.time.get_ticks()  # Ustaw czas wyświetlania

            # Znalezienie ścieżki do celu
            if target_cell:
                player_cell = (player_rect.x // cell_size, player_rect.y // cell_size)
                path = a_star(player_cell, target_cell)

    # Rysowanie tła
    screen.blit(background, (0, 0))

    # Poruszanie postaci wzdłuż znalezionej ścieżki
    if path:
        next_cell = path[0]
        next_pos = (next_cell[0] * cell_size, next_cell[1] * cell_size)
        if player_rect.topleft != next_pos:
            dx = next_pos[0] - player_rect.x
            dy = next_pos[1] - player_rect.y
            distance = math.hypot(dx, dy)
            if distance > player_speed:
                direction_x = dx / distance
                direction_y = dy / distance
                player_rect.x += direction_x * player_speed
                player_rect.y += direction_y * player_speed
            else:
                player_rect.topleft = next_pos  # Ustaw na dokładną pozycję

            # Usunięcie osiągniętej komórki z ścieżki
            if player_rect.topleft == next_pos:
                path.pop(0)
        else:
            path.pop(0)  # Jeśli dotarł do następnej komórki, usuń ją z listy

        # Sprawdź kierunek ruchu
        moving = True
        if path and player_rect.x < next_pos[0]:
            moving_direction = 1  # Prawo
        elif path and player_rect.x > next_pos[0]:
            moving_direction = -1  # Lewo
    else:
        moving = False

    # Animacja postaci
    if moving:
        animation_count += animation_speed
        if animation_count >= len(player_images):
            animation_count = 0
    else:
        animation_count = 0  # Reset animacji, gdy postać stoi

    # Rysowanie postaci
    if moving_direction == 1:
        screen.blit(player_images[int(animation_count)], player_rect.topleft)
    else:
        screen.blit(player_images_flipped[int(animation_count)], player_rect.topleft)

    # Rysowanie informacji zwrotnej (X lub kółko)
    if feedback_position and feedback_time:
        current_time = pygame.time.get_ticks()
        if current_time - feedback_time < 1000:  # Jeśli minęła mniej niż 1 sekunda
            if feedback_color == (255, 0, 0):  # Czerwony "X"
                pygame.draw.line(screen, feedback_color,
                                 (feedback_position[0] - 10, feedback_position[1] - 10),
                                 (feedback_position[0] + 10, feedback_position[1] + 10), 5)
                pygame.draw.line(screen, feedback_color,
                                 (feedback_position[0] + 10, feedback_position[1] - 10),
                                 (feedback_position[0] - 10, feedback_position[1] + 10), 5)
            elif feedback_color == (0, 255, 0):  # Zielone kółko
                pygame.draw.circle(screen, feedback_color, feedback_position, 10)  # Promień kółka

        else:
            # Resetuj zmienne po upływie czasu
            feedback_position = None
            feedback_color = None
            feedback_time = 0

    # Aktualizacja ekranu
    pygame.display.flip()

    # Ustawienie liczby klatek na sekundę
    clock.tick(60)

# Zamknięcie gry
pygame.quit()
sys.exit()
