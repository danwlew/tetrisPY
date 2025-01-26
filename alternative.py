import pygame
import sys
import os
import random
import json

# Stałe dla planszy (zostawiamy je, bo nie zmieniają się)
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Domyślny rozmiar okna
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

FPS = 60

# Kolory
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Kształty tetromino z wszystkimi rotacjami
SHAPES = {
    'I': [
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]],
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]]
    ],
    'O': [
        [[1, 1], [1, 1]]
    ],
    'T': [
        [[0, 1, 0], [1, 1, 1]],
        [[1, 0], [1, 1], [1, 0]],
        [[1, 1, 1], [0, 1, 0]],
        [[0, 1], [1, 1], [0, 1]]
    ],
    'L': [
        [[1, 0], [1, 0], [1, 1]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1], [0, 1], [0, 1]],
        [[0, 0, 1], [1, 1, 1]]
    ],
    'J': [
        [[0, 1], [0, 1], [1, 1]],
        [[1, 0, 0], [1, 1, 1]],
        [[1, 1], [1, 0], [1, 0]],
        [[1, 1, 1], [0, 0, 1]]
    ],
    'S': [
        [[0, 1, 1], [1, 1, 0]],
        [[1, 0], [1, 1], [0, 1]]
    ],
    'Z': [
        [[1, 1, 0], [0, 1, 1]],
        [[0, 1], [1, 1], [1, 0]]
    ]
}

SHAPE_COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'L': (255, 165, 0),
    'J': (0, 0, 255),
    'S': (0, 255, 0),
    'Z': (255, 0, 0)
}


class SkinManager:
    def __init__(self):
        self.skins = {}
        self.load_skins()

    def load_skins(self):
        skin_dir = 'skins'
        if not os.path.exists(skin_dir):
            return
        for shape in SHAPES.keys():
            path = os.path.join(skin_dir, f"{shape}.png")
            if os.path.exists(path):
                self.skins[shape] = pygame.image.load(path).convert_alpha()

    def get_skin(self, shape):
        return self.skins.get(shape, SHAPE_COLORS.get(shape, WHITE))


class HighScoreManager:
    def __init__(self, filename='highscores.json'):
        self.filename = filename
        self.high_scores = []
        self.load_high_scores()

    def load_high_scores(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.high_scores = json.load(f)
        else:
            self.high_scores = []

    def save_high_scores(self):
        with open(self.filename, 'w') as f:
            json.dump(self.high_scores, f)

    def add_score(self, name, score):
        self.high_scores.append({'name': name, 'score': score})
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        self.high_scores = self.high_scores[:10]
        self.save_high_scores()


class Menu:
    def __init__(self, window, high_score_manager):
        self.window = window
        self.high_score_manager = high_score_manager
        self.clock = pygame.time.Clock()

        # Na początek wyliczamy rozmiar czcionki w oparciu o wysokość okna,
        # tak aby tekst skalował się wraz z oknem
        self.font_size = max(20, self.window.get_height() // 15)
        self.font = pygame.font.Font(None, self.font_size)

        self.name = ''
        self.active_input = False

    def update_font(self):
        """Wywoływane przy zmianie rozmiaru okna, aby dopasować czcionkę."""
        self.font_size = max(20, self.window.get_height() // 15)
        self.font = pygame.font.Font(None, self.font_size)

    def draw_text(self, text, color, x, y):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.window.blit(text_surface, text_rect)

    def enter_name(self):
        self.active_input = True
        self.name = ''
        while self.active_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Reagujemy na zmianę rozmiaru okna w trakcie wprowadzania
                if event.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.update_font()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.active_input = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    else:
                        if len(self.name) < 20:
                            self.name += event.unicode

            self.window.fill(BLACK)
            cx = self.window.get_width() // 2
            cy = self.window.get_height() // 2
            self.draw_text("Enter your name:", WHITE, cx, cy - self.font_size * 1.5)
            self.draw_text(self.name, WHITE, cx, cy)
            pygame.display.flip()
            self.clock.tick(FPS)
        return self.name

    def display_menu(self):
        menu_running = True
        selected = 0
        options = ['Start Game', 'High Scores', 'Quit']
        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Obsługa zmiany rozmiaru okna
                if event.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.update_font()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if options[selected] == 'Start Game':
                            name = self.enter_name()
                            return 'start', name
                        elif options[selected] == 'High Scores':
                            self.show_high_scores()
                        elif options[selected] == 'Quit':
                            pygame.quit()
                            sys.exit()

            self.window.fill(BLACK)
            cx = self.window.get_width() // 2
            cy = self.window.get_height() // 2

            for i, option in enumerate(options):
                color = WHITE if i != selected else (255, 0, 0)
                # Pozycjonujemy tekst zależnie od i
                self.draw_text(option, color, cx, cy + i * (self.font_size + 10))

            pygame.display.flip()
            self.clock.tick(FPS)
        return 'quit', None

    def show_high_scores(self):
        showing = True
        while showing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.update_font()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        showing = False

            self.window.fill(BLACK)
            cx = self.window.get_width() // 2
            self.draw_text("High Scores", WHITE, cx, self.font_size * 1.5)

            for i, score in enumerate(self.high_score_manager.high_scores):
                text = f"{i + 1}. {score['name']}: {score['score']}"
                self.draw_text(text, WHITE, cx, (self.font_size * 3) + i * (self.font_size + 5))

            pygame.display.flip()
            self.clock.tick(FPS)


class TetrisGame:
    def __init__(self, window, skin_manager, player_name):
        self.window = window
        self.skin_manager = skin_manager
        self.player_name = player_name

        # Pobieramy wymiary aktualnego okna
        self.window_width = self.window.get_width()
        self.window_height = self.window.get_height()

        # Ustalamy wielkość klocka tak, aby cały grid (10x20)
        # i dodatkowy obszar na bok (na "next piece") zmieściły się na ekranie.
        # Przyjmujemy przykładowo, że w szerokości mamy min. 14 klocków
        # (10 na planszę + parę w zapasie na 'next piece'),
        # a w wysokości – 20 klocków (wysokość planszy).
        self.block_size = min(self.window_width // 14, self.window_height // 20)

        # Przygotowujemy siatkę
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = None

        self.score = 0
        self.level = 1

        # Prędkość spadania (ms)
        self.speed = 1000
        self.last_fall = pygame.time.get_ticks()
        self.game_over = False
        self.clock = pygame.time.Clock()

        # "Bag" do losowania klocków
        self.bag = []
        self.init_bag()

    def init_bag(self):
        """Inicjuje losowy worek kształtów i ustawia current_piece oraz next_piece."""
        self.bag = list(SHAPES.keys())
        random.shuffle(self.bag)
        self.next_piece = self.bag.pop()
        self.current_piece = self.new_piece()

    def new_piece(self):
        """Pobiera kolejny kształt z worka, uzupełnia worek, jeśli pusty."""
        if not self.bag:
            self.bag = list(SHAPES.keys())
            random.shuffle(self.bag)
        next_p = self.next_piece
        self.next_piece = self.bag.pop()
        return {
            'shape': next_p,
            'rotation': 0,
            # Ustawienie x tak, aby klocek startował pośrodku
            'x': GRID_WIDTH // 2 - len(SHAPES[next_p][0][0]) // 2,
            'y': 0
        }

    def check_collision(self, piece, dx=0, dy=0):
        """Sprawdza kolizję klocka z krawędziami lub już osadzonymi klockami."""
        shape = SHAPES[piece['shape']][piece['rotation']]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece['x'] + x + dx
                    new_y = piece['y'] + y + dy
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return True
        return False

    def move(self, dx, dy):
        """Przesuwa klocek o dx, dy jeśli nie ma kolizji.
           Jeśli kolizja przy dy=1, osadzamy klocek."""
        if not self.game_over:
            if not self.check_collision(self.current_piece, dx, dy):
                self.current_piece['x'] += dx
                self.current_piece['y'] += dy
                return True
            elif dy == 1:
                self.place_piece()
                return False
        return False

    def rotate(self):
        """Rotacja klocka (z uwzględnieniem kolizji)."""
        if self.game_over:
            return
        original_rotation = self.current_piece['rotation']
        self.current_piece['rotation'] = (original_rotation + 1) % len(SHAPES[self.current_piece['shape']])
        if self.check_collision(self.current_piece):
            self.current_piece['rotation'] = original_rotation

    def place_piece(self):
        """Osadza klocek na siatce i czyści linie."""
        shape = SHAPES[self.current_piece['shape']][self.current_piece['rotation']]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    # Jeśli klocek wychodzi ponad planszę => Game Over
                    if self.current_piece['y'] + y < 0:
                        self.game_over = True
                        return
                    self.grid[self.current_piece['y'] + y][self.current_piece['x'] + x] = self.current_piece['shape']

        lines_cleared = self.clear_lines()
        self.update_score(lines_cleared)
        self.current_piece = self.new_piece()
        if self.check_collision(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        """Usuwa zapełnione linie i zlicza ile usunięto."""
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(self.grid[y]):
                lines_cleared += 1
                del self.grid[y]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            else:
                y -= 1
        return lines_cleared

    def update_score(self, lines):
        """Aktualizuje wynik w zależności od liczby wyczyszczonych linii."""
        points = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
        self.score += points.get(lines, 0) * self.level
        self.level = 1 + (self.score // 1000)
        # Im wyższy poziom, tym szybsze spadanie, ale do pewnego minimum (50 ms)
        self.speed = max(50, 1000 - (self.level - 1) * 100)

    def draw(self):
        """Rysowanie całej sceny."""
        self.window.fill(BLACK)

        # Rysujemy zakotwiczone klocki z grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    block = self.grid[y][x]
                    skin = self.skin_manager.get_skin(block)
                    rect = pygame.Rect(
                        x * self.block_size,
                        y * self.block_size,
                        self.block_size - 1,
                        self.block_size - 1
                    )
                    if isinstance(skin, pygame.Surface):
                        # Skalujemy ewentualnie grafikę do block_size x block_size
                        scaled_skin = pygame.transform.scale(skin, (self.block_size, self.block_size))
                        self.window.blit(scaled_skin, rect)
                    else:
                        pygame.draw.rect(self.window, skin, rect)

        # Rysujemy aktualnie spadający klocek
        if self.current_piece and not self.game_over:
            shape = SHAPES[self.current_piece['shape']][self.current_piece['rotation']]
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        block = self.current_piece['shape']
                        skin = self.skin_manager.get_skin(block)
                        pos_x = (self.current_piece['x'] + x) * self.block_size
                        pos_y = (self.current_piece['y'] + y) * self.block_size
                        rect = pygame.Rect(pos_x, pos_y, self.block_size - 1, self.block_size - 1)
                        if isinstance(skin, pygame.Surface):
                            scaled_skin = pygame.transform.scale(skin, (self.block_size, self.block_size))
                            self.window.blit(scaled_skin, rect)
                        else:
                            pygame.draw.rect(self.window, skin, rect)

        # Rysujemy podgląd następnego klocka (po prawej stronie)
        next_x = self.block_size * (GRID_WIDTH + 2)
        next_y = self.block_size * 2
        if self.next_piece:
            shape = SHAPES[self.next_piece][0]
            for row_i, row in enumerate(shape):
                for col_i, cell in enumerate(row):
                    if cell:
                        block = self.next_piece
                        skin = self.skin_manager.get_skin(block)
                        pos_x = next_x + col_i * self.block_size
                        pos_y = next_y + row_i * self.block_size
                        rect = pygame.Rect(pos_x, pos_y, self.block_size - 1, self.block_size - 1)
                        if isinstance(skin, pygame.Surface):
                            scaled_skin = pygame.transform.scale(skin, (self.block_size, self.block_size))
                            self.window.blit(scaled_skin, rect)
                        else:
                            pygame.draw.rect(self.window, skin, rect)

        # Rysowanie UI z punktacją
        font_size = max(20, self.block_size)  # dopasowujemy wielkość czcionki do rozmiaru klocka
        font = pygame.font.Font(None, font_size)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)

        self.window.blit(score_text, (next_x, next_y + 5 * self.block_size))
        self.window.blit(level_text, (next_x, next_y + 5 * self.block_size + font_size + 10))

        # Komunikat Game Over
        if self.game_over:
            font_go = pygame.font.Font(None, font_size * 2)
            text = font_go.render("Game Over", True, WHITE)
            text_rect = text.get_rect(center=(self.window_width // 2, self.window_height // 2))
            self.window.blit(text, text_rect)

        pygame.display.flip()

    def handle_input(self):
        """Obsługa inputu gracza oraz zdarzeń systemowych (w tym zmiany rozmiaru)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Obsługa zmiany rozmiaru okna
            if event.type == pygame.VIDEORESIZE:
                # Aktualizujemy okno i obliczamy nowy block_size
                self.window_width, self.window_height = event.w, event.h
                self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.block_size = min(self.window_width // 14, self.window_height // 20)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move(1, 0)
                elif event.key == pygame.K_DOWN:
                    self.move(0, 1)
                elif event.key == pygame.K_UP:
                    self.rotate()
                elif event.key == pygame.K_SPACE:
                    # tzw. "hard drop"
                    while self.move(0, 1):
                        pass
                    self.place_piece()
                elif event.key == pygame.K_ESCAPE:
                    self.game_over = True

    def run(self):
        """Główna pętla gry."""
        while not self.game_over:
            self.handle_input()
            now = pygame.time.get_ticks()
            if now - self.last_fall > self.speed:
                if not self.move(0, 1):
                    self.place_piece()
                self.last_fall = now
            self.draw()
            self.clock.tick(FPS)


def main():
    pygame.init()

    # Ustawiamy okno jako RESIZABLE
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Tetris")

    high_score_manager = HighScoreManager()
    skin_manager = SkinManager()
    menu = Menu(window, high_score_manager)

    while True:
        action, player_name = menu.display_menu()

        if action == 'start':
            game = TetrisGame(window, skin_manager, player_name)
            game.run()
            if game.score > 0:
                high_score_manager.add_score(player_name, game.score)
        elif action == 'quit':
            break

    pygame.quit()


if __name__ == "__main__":
    main()
