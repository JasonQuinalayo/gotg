import pygame
import sys
from rank import Rank
from ai import generate_random_init_form
pygame.init()

SQUARE_DIM = 90
PIECE_WIDTH = 80
PIECE_HEIGHT = 48
PADDING = 3

RANK_IMG = {
    Rank.FLAG: 'flag.png',
    Rank.SPY: 'spy.png',
    Rank.PRIVATE: 'private.png',
    Rank.SERGEANT: 'sergeant.png',
    Rank.FIRST_LIEUTENANT: 'lieutenant1.png',
    Rank.SECOND_LIEUTENANT: 'lieutenant2.png',
    Rank.MAJOR: 'major.png',
    Rank.CAPTAIN: 'captain.png',
    Rank.LIEUTENANT_COLONEL: 'colonel2.png',
    Rank.COLONEL: 'colonel3.png',
    Rank.GENERAL_ONE: 'general1.png',
    Rank.GENERAL_TWO: 'general2.png',
    Rank.GENERAL_THREE: 'general3.png',
    Rank.GENERAL_FOUR: 'general4.png',
    Rank.GENERAL_FIVE: 'general5.jpg',
}

ENEMY_PIECE_IMG = pygame.transform.smoothscale(pygame.image.load('./assets/image0.jpeg'), (PIECE_WIDTH, PIECE_HEIGHT))

for rank, file in RANK_IMG.items():
    RANK_IMG[rank] = pygame.transform.smoothscale(pygame.image.load(f'./assets/{file}'), (PIECE_WIDTH, PIECE_HEIGHT))


class Square:
    def __init__(self, screen, left, top, row, col):
        self._screen = screen
        self._rect = pygame.Rect(left, top, SQUARE_DIM, SQUARE_DIM)
        self._outline_rect = pygame.Rect(left + (SQUARE_DIM - PIECE_WIDTH) / 2 - 3,
                                         top + (SQUARE_DIM - PIECE_HEIGHT) / 2 - 3,
                                         PIECE_WIDTH + 6,
                                         PIECE_HEIGHT + 6)
        self.row = row
        self.col = col

    def draw_square(self):
        pygame.draw.rect(self._screen, (108, 0, 0), self._rect)

    def draw_piece(self, surface):
        rect = surface.get_rect(center=(self._rect.left + SQUARE_DIM / 2, self._rect.top + SQUARE_DIM / 2))
        self._screen.blit(surface, rect)

    def touches(self, x, y):
        return self._rect.left <= x <= self._rect.left + SQUARE_DIM and \
               self._rect.top <= y <= self._rect.top + SQUARE_DIM

    def color(self, rgb):
        pygame.draw.rect(self._screen, rgb, self._rect)

    def outline_piece(self, rgb):
        pygame.draw.rect(self._screen, rgb, self._outline_rect)


def _run(tick, cond):
    clock = pygame.time.Clock()
    while cond():
        clock.tick(60)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()
        tick(events)


def print_board(board):
    print()
    b = [[str(i) for i in range(-1,9)]] + \
        [[str(idx)] + [str(x.player) + "_" + str(x.rank.value) if x is not None else '#' for x in row] for
         idx, row in enumerate(board)]
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in b]))


class Game:
    def __init__(self, gog):
        self._gog = gog
        self._screen = pygame.display.set_mode((PADDING * 10 + SQUARE_DIM * 9, PADDING * 9 + SQUARE_DIM * 8))
        self._init_form = generate_random_init_form()
        self._squares = []
        self._started = False
        self._selected_square = None
        self._highlight_green = []
        self._ready_button = pygame.Rect(0, 0, 300, 80)
        self._ready_button.center = (PADDING * 10 + SQUARE_DIM * 9) / 2, 300
        self._pov = None
        for i in range(8):
            row = []
            for j in range(9):
                row.append(Square(
                    self._screen,
                    (j + 1) * PADDING + j * SQUARE_DIM,
                    (i + 1) * PADDING + i * SQUARE_DIM,
                    i,
                    j,
                ))
            self._squares.append(row)

    def _draw_board(self):
        self._screen.fill((18, 0, 0))
        for row in self._squares:
            for square in row:
                square.draw_square()
        if self._selected_square:
            self._selected_square.outline_piece((12, 255, 0))
        if self._highlight_green:
            for square in self._highlight_green:
                square.color((12, 255, 0))
        if not self._started:
            pygame.draw.rect(self._screen, (100, 100, 100), self._ready_button)
            for i, row in enumerate(self._init_form):
                for j, square in enumerate(row):
                    if square is not None:
                        self._squares[5 + i][j].draw_piece(RANK_IMG[square])
        else:
            assert self._pov
            for i, row in enumerate(self._pov):
                for j, square in enumerate(row):
                    if square is not None:
                        if square.player == 2:
                            self._squares[i][j].draw_piece(ENEMY_PIECE_IMG)
                        else:
                            self._squares[i][j].draw_piece(RANK_IMG[square.rank])
        pygame.display.flip()

    def run(self):
        def init_pos_tick(events):
            self._draw_board()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self._selected_square:
                        for i, row in enumerate(self._squares[5:8]):
                            for j, square in enumerate(row):
                                if self._init_form[i][j]:
                                    continue
                                if square.touches(event.pos[0], event.pos[1]):
                                    self._init_form[i][j] = \
                                        self._init_form[self._selected_square.row - 5][self._selected_square.col]
                                    self._init_form[self._selected_square.row - 5][self._selected_square.col] = None
                        self._selected_square = None
                        self._highlight_green = []
                    else:
                        highlight = []
                        for i, row in enumerate(self._squares[5:8]):
                            for j, square in enumerate(row):
                                if not self._init_form[i][j]:
                                    highlight.append(square)
                                    continue
                                if square.touches(event.pos[0], event.pos[1]):
                                    self._selected_square = square
                                    self._highlight_green = highlight
                    if self._touches_ready_button(event.pos[0], event.pos[1]):
                        self._pov = self._gog.set_player_pieces(self._init_form, 1)
                        self._started = True
        _run(init_pos_tick, lambda: not self._started)

        def main_game(events):
            self._draw_board()

        _run(main_game, lambda: True)

    def _touches_ready_button(self, x, y):
        return self._ready_button.left <= x <= self._ready_button.right and \
               self._ready_button.top <= y <= self._ready_button.bottom

