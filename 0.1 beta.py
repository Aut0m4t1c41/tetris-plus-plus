# TETRIS PLUS PLUS — Arcade 3.3.3
# Меню: игроки / сложность / режим

import arcade
import random

# ================== КОНСТАНТЫ ==================
CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

FIELD_WIDTH = GRID_WIDTH * CELL_SIZE
BIG_FIELD_WIDTH = GRID_WIDTH * 2 * CELL_SIZE

SCREEN_WIDTH = FIELD_WIDTH * 2 + 80
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

# ================== ФИГУРЫ ==================
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

COLORS = [
    arcade.color.CYAN,
    arcade.color.PURPLE,
    arcade.color.ORANGE,
    arcade.color.BLUE,
    arcade.color.YELLOW,
    arcade.color.GREEN,
    arcade.color.RED,
    arcade.color.PINK,
    arcade.color.BROWN,
]

# ================== ИГРОВОЕ ПОЛЕ ==================
class PlayerField:
    def __init__(self, offset_x, speed, shapes, width=GRID_WIDTH):
        self.offset_x = offset_x
        self.width = width
        self.speed = speed
        self.shapes = shapes

        self.grid = [[0 for _ in range(width)] for _ in range(GRID_HEIGHT)]
        self.timer = 0
        self.score = 0
        self.game_over = False

        self.new_piece()

    def new_piece(self):
        idx = random.randint(0, len(self.shapes) - 1)
        self.piece = self.shapes[idx]
        self.color = COLORS[idx]
        self.x = self.width // 2 - len(self.piece[0]) // 2
        self.y = GRID_HEIGHT - 1
        if not self.valid():
            self.game_over = True

    def rotate(self):
        rotated = [[self.piece[y][x] for y in range(len(self.piece) - 1, -1, -1)]
                   for x in range(len(self.piece[0]))]
        old = self.piece
        self.piece = rotated
        if not self.valid():
            self.piece = old

    def valid(self, dx=0, dy=0):
        for y, row in enumerate(self.piece):
            for x, cell in enumerate(row):
                if cell:
                    gx = self.x + x + dx
                    gy = self.y - y + dy
                    if gx < 0 or gx >= self.width or gy < 0:
                        return False
                    if gy < GRID_HEIGHT and self.grid[gy][gx]:
                        return False
        return True

    def place(self):
        for y, row in enumerate(self.piece):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.y - y][self.x + x] = self.color
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        new_grid = [row for row in self.grid if not all(row)]
        cleared = GRID_HEIGHT - len(new_grid)
        for _ in range(cleared):
            new_grid.append([0] * self.width)
        self.grid = new_grid
        self.score += cleared * 100

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

    def draw(self):
        for y in range(GRID_HEIGHT):
            for x in range(self.width):
                if self.grid[y][x]:
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(
                            self.offset_x + x * CELL_SIZE + CELL_SIZE // 2,
                            y * CELL_SIZE + CELL_SIZE // 2,
                            CELL_SIZE - 1,
                            CELL_SIZE - 1,
                        ),
                        self.grid[y][x],
                    )
        for y, row in enumerate(self.piece):
            for x, cell in enumerate(row):
                if cell:
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(
                            self.offset_x + (self.x + x) * CELL_SIZE + CELL_SIZE // 2,
                            (self.y - y) * CELL_SIZE + CELL_SIZE // 2,
                            CELL_SIZE - 1,
                            CELL_SIZE - 1,
                        ),
                        self.color,
                    )

# ================== ИГРА ==================
class TetrisPlusPlus(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Tetris++")
        arcade.set_background_color(arcade.color.BLACK)

        self.state = "menu"
        self.menu_index = 0

        self.players = 1
        self.difficulty = 0
        self.mode = 0

        self.menu_items = [
            "Игроки: ",
            "Сложность: ",
            "Режим: ",
            "СТАРТ",
        ]

    # ---------- НАСТРОЙКА ИГРЫ ----------
    def setup_game(self):
        if self.difficulty == 0:
            speed, shapes = 0.7, BASIC_SHAPES
        elif self.difficulty == 1:
            speed, shapes = 0.4, BASIC_SHAPES
        else:
            speed, shapes = 0.25, HARD_SHAPES

        if self.mode == 0:  # дуэль
            self.p1 = PlayerField(0, speed, shapes)
            self.p2 = PlayerField(FIELD_WIDTH + 40, speed, shapes) if self.players == 2 else None
        else:  # совместный режим
            self.p1 = PlayerField(40, speed, shapes, width=GRID_WIDTH * 2)
            self.p2 = None

        self.state = "game"

    # ---------- ОТРИСОВКА ----------
    def on_draw(self):
        self.clear()
        if self.state == "menu":
            self.draw_menu()
        else:
            self.draw_game()

    def draw_menu(self):
        options = [
            f"Игроки: {'Один' if self.players == 1 else 'Два'}",
            f"Сложность: {['Легко', 'Нормально', 'Хард'][self.difficulty]}",
            f"Режим: {'Дуэль' if self.mode == 0 else 'Совместный'}",
            "СТАРТ",
        ]

        for i, text in enumerate(options):
            color = arcade.color.YELLOW if i == self.menu_index else arcade.color.WHITE
            arcade.draw_text(
                text,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 60 - i * 40,
                color,
                20,
                anchor_x="center",
            )

    def draw_game(self):
        self.p1.draw()
        if self.p2:
            self.p2.draw()
        arcade.draw_text(f"Score: {self.p1.score}", 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 14)

    # ---------- ЛОГИКА ----------
    def on_update(self, dt):
        if self.state == "game":
            self.p1.update(dt)
            if self.p2:
                self.p2.update(dt)

    def on_key_press(self, key, modifiers):
        if self.state == "menu":
            if key == arcade.key.UP:
                self.menu_index = (self.menu_index - 1) % 4
            elif key == arcade.key.DOWN:
                self.menu_index = (self.menu_index + 1) % 4
            elif key == arcade.key.LEFT:
                self.change_option(-1)
            elif key == arcade.key.RIGHT:
                self.change_option(1)
            elif key == arcade.key.ENTER:
                if self.menu_index == 3:
                    self.setup_game()
            return

        # управление игроком 1
        if key == arcade.key.A and self.p1.valid(dx=-1): self.p1.x -= 1
        elif key == arcade.key.D and self.p1.valid(dx=1): self.p1.x += 1
        elif key == arcade.key.S and self.p1.valid(dy=-1): self.p1.y -= 1
        elif key == arcade.key.W: self.p1.rotate()

        # игрок 2 (если есть)
        if self.p2:
            if key == arcade.key.LEFT and self.p2.valid(dx=-1): self.p2.x -= 1
            elif key == arcade.key.RIGHT and self.p2.valid(dx=1): self.p2.x += 1
            elif key == arcade.key.DOWN and self.p2.valid(dy=-1): self.p2.y -= 1
            elif key == arcade.key.UP: self.p2.rotate()

    def change_option(self, direction):
        if self.menu_index == 0:
            self.players = 1 if self.players == 2 else 2
        elif self.menu_index == 1:
            self.difficulty = (self.difficulty + direction) % 3
        elif self.menu_index == 2:
            self.mode = 1 - self.mode


def main():
    TetrisPlusPlus()
    arcade.run()


if __name__ == '__main__':
    main()