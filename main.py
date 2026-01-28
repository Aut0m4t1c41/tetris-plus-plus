# TETRIS PLUS PLUS — Arcade 3.3.3
# Меню + Game Over + дуэль/соло
# Добавлено: подписи игроков, счётчик, рестарт, улучшенный выход

import arcade
import random

CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

FIELD_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_WIDTH = FIELD_WIDTH * 2 + 80
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

# ---------- ФИГУРЫ ----------
BASIC_SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
]

HARD_SHAPES = BASIC_SHAPES + [
    [[1, 1, 1, 1, 1]],
    [[1, 0, 1], [1, 1, 1]],
]

COLORS = [arcade.color.CYAN, arcade.color.PURPLE, arcade.color.ORANGE,
          arcade.color.BLUE, arcade.color.YELLOW, arcade.color.GREEN,
          arcade.color.RED, arcade.color.PINK, arcade.color.BROWN]

# ---------- ПОЛЕ ----------
class PlayerField:
    def __init__(self, offset_x, speed, shapes):
        self.offset_x = offset_x
        self.speed = speed
        self.shapes = shapes
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.timer = 0
        self.score = 0
        self.game_over = False
        self.new_piece()

    def new_piece(self):
        idx = random.randint(0, len(self.shapes) - 1)
        self.piece = self.shapes[idx]
        self.color = COLORS[idx]
        self.x = GRID_WIDTH // 2 - len(self.piece[0]) // 2
        self.y = GRID_HEIGHT - 1
        if not self.valid():
            self.game_over = True

    def rotate(self):
        r = [[self.piece[y][x] for y in range(len(self.piece) - 1, -1, -1)]
             for x in range(len(self.piece[0]))]
        old = self.piece
        self.piece = r
        if not self.valid():
            self.piece = old

    def valid(self, dx=0, dy=0):
        for y, row in enumerate(self.piece):
            for x, c in enumerate(row):
                if c:
                    gx = self.x + x + dx
                    gy = self.y - y + dy
                    if gx < 0 or gx >= GRID_WIDTH or gy < 0:
                        return False
                    if gy < GRID_HEIGHT and self.grid[gy][gx]:
                        return False
        return True

    def place(self):
        for y, row in enumerate(self.piece):
            for x, c in enumerate(row):
                if c:
                    self.grid[self.y - y][self.x + x] = self.color
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        self.grid = [r for r in self.grid if not all(r)]
        while len(self.grid) < GRID_HEIGHT:
            self.grid.append([0] * GRID_WIDTH)
        self.score += 100

    def update(self, dt):
        if self.game_over:
            return
        self.timer += dt
        if self.timer >= self.speed:
            self.timer = 0
            if self.valid(dy=-1):
                self.y -= 1
            else:
                self.place()

    def draw(self, dead=False):
        arcade.draw_rect_filled(
            arcade.rect.XYWH(self.offset_x + FIELD_WIDTH // 2,
                             SCREEN_HEIGHT // 2,
                             FIELD_WIDTH,
                             SCREEN_HEIGHT),
            arcade.color.DARK_RED if dead else arcade.color.DARK_BLUE_GRAY
        )

        if dead:
            arcade.draw_text("ИГРА ОКОНЧЕНА",
                             self.offset_x + FIELD_WIDTH // 2,
                             SCREEN_HEIGHT // 2 + 20,
                             arcade.color.WHITE, 20,
                             anchor_x="center")
            return

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(self.offset_x + x * CELL_SIZE + CELL_SIZE // 2,
                                         y * CELL_SIZE + CELL_SIZE // 2,
                                         CELL_SIZE - 1, CELL_SIZE - 1),
                        self.grid[y][x])

        for y, row in enumerate(self.piece):
            for x, c in enumerate(row):
                if c:
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(self.offset_x + (self.x + x) * CELL_SIZE + CELL_SIZE // 2,
                                         (self.y - y) * CELL_SIZE + CELL_SIZE // 2,
                                         CELL_SIZE - 1, CELL_SIZE - 1),
                        self.color)

# ---------- ИГРА ----------
class TetrisPP(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Tetris++")
        arcade.set_background_color(arcade.color.BLACK)
        self.state = "menu"
        self.menu_index = 0
        self.players = 1
        self.difficulty = 0
        self.mode = 0

    def setup_game(self):
        speed = [0.7, 0.4, 0.25][self.difficulty]
        shapes = BASIC_SHAPES if self.difficulty < 2 else HARD_SHAPES

        if self.players == 1:
            center = SCREEN_WIDTH // 2 - FIELD_WIDTH // 2
            self.p1 = PlayerField(center, speed, shapes)
            self.p2 = None
        else:
            self.p1 = PlayerField(0, speed, shapes)
            self.p2 = PlayerField(FIELD_WIDTH + 40, speed, shapes)
        self.state = "game"

    def on_draw(self):
        self.clear()
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "game":
            self.draw_game()
        elif self.state == "game_over":
            self.draw_game_over()

    def draw_menu(self):
        items = [
            f"Игроки: {'Один' if self.players == 1 else 'Два'}",
            f"Сложность: {['Легко', 'Нормально', 'Хард'][self.difficulty]}",
            "СТАРТ"
        ]
        for i, text in enumerate(items):
            arcade.draw_text(text, SCREEN_WIDTH // 2,
                             SCREEN_HEIGHT // 2 + 60 - i * 40,
                             arcade.color.YELLOW if i == self.menu_index else arcade.color.WHITE,
                             20, anchor_x="center")

    def draw_game(self):
        self.p1.draw(dead=self.p1.game_over)

        arcade.draw_text("Игрок 1",
                         self.p1.offset_x + FIELD_WIDTH // 2,
                         SCREEN_HEIGHT - 25,
                         arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text(f"Счёт: {self.p1.score}",
                         self.p1.offset_x + 10,
                         SCREEN_HEIGHT - 50,
                         arcade.color.WHITE, 14)

        if self.p2:
            self.p2.draw(dead=self.p2.game_over)
            arcade.draw_text("Игрок 2",
                             self.p2.offset_x + FIELD_WIDTH // 2,
                             SCREEN_HEIGHT - 25,
                             arcade.color.WHITE, 16, anchor_x="center")
            arcade.draw_text(f"Счёт: {self.p2.score}",
                             self.p2.offset_x + 10,
                             SCREEN_HEIGHT - 50,
                             arcade.color.WHITE, 14)

            if self.p1.game_over and self.p2.game_over:
                self.state = "game_over"
        elif self.p1.game_over:
            self.state = "game_over"

    def draw_game_over(self):
        arcade.draw_text("GAME OVER",
                         SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT // 2 + 40,
                         arcade.color.RED, 30, anchor_x="center")
        arcade.draw_text("ENTER — Начать заново",
                         SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT // 2,
                         arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("ESC — Выход из игры",
                         SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT // 2 - 30,
                         arcade.color.LIGHT_GRAY, 14, anchor_x="center")

    def on_update(self, dt):
        if self.state == "game":
            self.p1.update(dt)
            if self.p2:
                self.p2.update(dt)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.state == "game":
                self.state = "menu"
            else:
                arcade.close_window()
            return

        if self.state == "menu":
            if key == arcade.key.UP:
                self.menu_index = max(0, self.menu_index - 1)
            elif key == arcade.key.DOWN:
                self.menu_index += 1
            elif key == arcade.key.LEFT and self.menu_index == 0:
                self.players = 1 if self.players == 2 else 2
            elif key == arcade.key.RIGHT and self.menu_index == 0:
                self.players = 1 if self.players == 2 else 2
            elif key == arcade.key.LEFT and self.menu_index == 1:
                self.difficulty = (self.difficulty - 1) % 3
            elif key == arcade.key.RIGHT and self.menu_index == 1:
                self.difficulty = (self.difficulty + 1) % 3
            elif key == arcade.key.ENTER:
                self.setup_game()

            return

        if self.state == "game_over":
            if key == arcade.key.ENTER:
                self.setup_game()
            return

        if self.state != "game":
            return

        if key == arcade.key.A and self.p1.valid(dx=-1): self.p1.x -= 1
        elif key == arcade.key.D and self.p1.valid(dx=1): self.p1.x += 1
        elif key == arcade.key.S and self.p1.valid(dy=-1): self.p1.y -= 1
        elif key == arcade.key.W: self.p1.rotate()

        if self.p2:
            if key == arcade.key.LEFT and self.p2.valid(dx=-1): self.p2.x -= 1
            elif key == arcade.key.RIGHT and self.p2.valid(dx=1): self.p2.x += 1
            elif key == arcade.key.DOWN and self.p2.valid(dy=-1): self.p2.y -= 1
            elif key == arcade.key.UP: self.p2.rotate()


def main():
    TetrisPP()
    arcade.run()


if __name__ == '__main__':
    main()