import pygame
import sys
import os
import random
import json

# Stałe
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Kolory
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

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
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.name = ''
        self.active_input = False

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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.active_input = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    else:
                        if len(self.name) < 20:
                            self.name += event.unicode
            self.window.fill(BLACK)
            self.draw_text("Enter your name:", WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40)
            self.draw_text(self.name, WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
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
            for i, option in enumerate(options):
                color = WHITE if i != selected else (255, 0, 0)
                self.draw_text(option, color, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + i * 40)
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        showing = False
            self.window.fill(BLACK)
            self.draw_text("High Scores", WHITE, WINDOW_WIDTH // 2, 50)
            for i, score in enumerate(self.high_score_manager.high_scores):
                text = f"{i + 1}. {score['name']}: {score['score']}"
                self.draw_text(text, WHITE, WINDOW_WIDTH // 2, 100 + i * 40)
            pygame.display.flip()
            self.clock.tick(FPS)


class TetrisGame:
    def __init__(self, window, skin_manager, player_name):
        self.window = window
        self.skin_manager = skin_manager
        self.player_name = player_name
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.level = 1
        self.speed = 1000
        self.last_fall = pygame.time.get_ticks()
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.bag = []
        self.init_bag()

    def init_bag(self):
        self.bag = list(SHAPES.keys())
        random.shuffle(self.bag)
        self.next_piece = self.bag.pop()
        self.current_piece = self.new_piece()

    def new_piece(self):
        if not self.bag:
            self.bag = list(SHAPES.keys())
            random.shuffle(self.bag)
        next_p = self.next_piece
        self.next_piece = self.bag.pop()
        return {
            'shape': next_p,
            'rotation': 0,
            'x': GRID_WIDTH // 2 - len(SHAPES[next_p][0][0]) // 2,
            'y': 0
        }

    def check_collision(self, piece, dx=0, dy=0):
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
        if self.game_over:
            return
        original_rotation = self.current_piece['rotation']
        self.current_piece['rotation'] = (self.current_piece['rotation'] + 1) % len(SHAPES[self.current_piece['shape']])
        if self.check_collision(self.current_piece):
            self.current_piece['rotation'] = original_rotation

    def place_piece(self):
        shape = SHAPES[self.current_piece['shape']][self.current_piece['rotation']]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
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
        points = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
        self.score += points.get(lines, 0) * self.level
        self.level = 1 + (self.score // 1000)
        self.speed = max(50, 1000 - (self.level - 1) * 100)

    def draw(self):
        self.window.fill(BLACK)
        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    block = self.grid[y][x]
                    skin = self.skin_manager.get_skin(block)
                    rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                    if isinstance(skin, pygame.Surface):
                        self.window.blit(skin, rect)
                    else:
                        pygame.draw.rect(self.window, skin, rect)
        # Draw current piece
        if self.current_piece and not self.game_over:
            shape = SHAPES[self.current_piece['shape']][self.current_piece['rotation']]
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        block = self.current_piece['shape']
                        skin = self.skin_manager.get_skin(block)
                        pos_x = (self.current_piece['x'] + x) * BLOCK_SIZE
                        pos_y = (self.current_piece['y'] + y) * BLOCK_SIZE
                        rect = pygame.Rect(pos_x, pos_y, BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                        if isinstance(skin, pygame.Surface):
                            self.window.blit(skin, rect)
                        else:
                            pygame.draw.rect(self.window, skin, rect)
        # Draw next piece
        next_x = GRID_WIDTH * BLOCK_SIZE + 50
        next_y = 50
        if self.next_piece:
            shape = SHAPES[self.next_piece][0]
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        block = self.next_piece
                        skin = self.skin_manager.get_skin(block)
                        pos_x = next_x + x * BLOCK_SIZE
                        pos_y = next_y + y * BLOCK_SIZE
                        rect = pygame.Rect(pos_x, pos_y, BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                        if isinstance(skin, pygame.Surface):
                            self.window.blit(skin, rect)
                        else:
                            pygame.draw.rect(self.window, skin, rect)
        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        self.window.blit(score_text, (next_x, next_y + 200))
        self.window.blit(level_text, (next_x, next_y + 240))
        if self.game_over:
            font = pygame.font.Font(None, 72)
            text = font.render("Game Over", True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.window.blit(text, text_rect)
        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
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
                    while self.move(0, 1):
                        pass
                    self.place_piece()
                elif event.key == pygame.K_ESCAPE:
                    self.game_over = True

    def run(self):
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
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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