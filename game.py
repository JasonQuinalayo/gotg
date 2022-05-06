import pygame
import sys
from threading import Thread
from rank import Rank
from ai import generate_random_init_form
pygame.init()

SQUARE_DIM = 90
PIECE_WIDTH = 80
PIECE_HEIGHT = 48
PADDING = 3
SCREEN = pygame.display.set_mode((PADDING * 10 + SQUARE_DIM * 9, PADDING * 9 + SQUARE_DIM * 8))

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
    def __init__(self, left, top, row, col):
        self._rect = pygame.Rect(left, top, SQUARE_DIM, SQUARE_DIM)
        self._outline_rect = pygame.Rect(left + (SQUARE_DIM - PIECE_WIDTH) / 2 - 3,
                                         top + (SQUARE_DIM - PIECE_HEIGHT) / 2 - 3,
                                         PIECE_WIDTH + 6,
                                         PIECE_HEIGHT + 6)
        self.row = row
        self.col = col

    def draw_square(self):
        pygame.draw.rect(SCREEN, (108, 0, 0), self._rect)

    def draw_piece(self, surface):
        rect = surface.get_rect(center=(self._rect.left + SQUARE_DIM / 2, self._rect.top + SQUARE_DIM / 2))
        SCREEN.blit(surface, rect)

    def touches(self, x, y):
        return self._rect.collidepoint(x, y)

    def color(self, rgb):
        pygame.draw.rect(SCREEN, rgb, self._rect)

    def outline_piece(self, rgb):
        pygame.draw.rect(SCREEN, rgb, self._outline_rect)


class Game:
    def __init__(self, gog, ai):
        self._gog = gog
        self._init_form = generate_random_init_form()
        self._squares = []
        self._started = False
        self._selected_square = None
        self._highlight_green = []
        self._highlight_orange = []
        self._glow_ready = False
        self._ready_text_surface = pygame.font.SysFont('comicsansms', 50).render('READY', True, (255, 255, 255))
        self._ready_text_glow_surface = pygame.font.SysFont('comicsansms', 50).render('READY', True, (102, 255, 107))
        self._ready_text_rect = self._ready_text_surface.get_rect(center=((PADDING * 10 + SQUARE_DIM * 9) / 2, 300))
        self._ready_button_rect = self._ready_text_rect.copy()
        self._ready_button_rect.width = self._ready_text_rect.width + 20
        self._ready_button_rect.height = self._ready_text_rect.height + 20
        self._ready_button_rect.center = self._ready_text_rect.center
        self._outcome_text_surface = {
            1: pygame.font.SysFont('comicsansms', 50).render('VICTORY!', True, (41, 155, 255)),
            2: pygame.font.SysFont('comicsansms', 50).render('DEFEAT!', True, (238, 255, 0))
        }
        self._outcome_rect = {
            1: self._outcome_text_surface[1].get_rect(
                center=(((10 * PADDING + 9 * SQUARE_DIM) / 2), (9 * PADDING + 8 * SQUARE_DIM) / 2)),
            2: self._outcome_text_surface[2].get_rect(
                center=(((10 * PADDING + 9 * SQUARE_DIM) / 2), (9 * PADDING + 8 * SQUARE_DIM) / 2)),
        }
        self._glow_restart = False
        self._restart_text_surface = pygame.font.SysFont('comicsansms', 30).render('RESTART', True, (255, 255, 255))
        self._restart_text_glow_surface = pygame.font.SysFont('comicsansms', 30).render('RESTART', True, (102, 255, 99))
        self._restart_text_rect = self._restart_text_surface.get_rect(center=((PADDING * 10 + SQUARE_DIM * 9) / 2, 450))
        self._restart_button_rect = self._restart_text_rect.copy()
        self._restart_button_rect.width = self._restart_text_rect.width + 20
        self._restart_button_rect.height = self._restart_text_rect.height + 20
        self._restart_button_rect.center = self._restart_text_rect.center
        self._calculating_text_surface = pygame.font.SysFont('comicsansms', 30).render('enemy thinking xd', True, (255, 255, 255))
        self._calculating_text_rect = self._calculating_text_surface.get_rect(center=(((10 * PADDING + 9 * SQUARE_DIM) / 2), (9 * PADDING + 8 * SQUARE_DIM) / 2)),
        self._pov = None
        self._ai = ai
        self._restart = False
        self._exit = False
        self._get_ai_move = False
        self._ai_move = None
        for i in range(8):
            row = []
            for j in range(9):
                row.append(Square(
                    (j + 1) * PADDING + j * SQUARE_DIM,
                    (i + 1) * PADDING + i * SQUARE_DIM,
                    i,
                    j,
                ))
            self._squares.append(row)

    def _draw_board(self):
        SCREEN.fill((18, 0, 0))
        for row in self._squares:
            for square in row:
                square.draw_square()
        if self._highlight_orange:
            for square in self._highlight_orange:
                square.color((255, 77, 0))
        if self._highlight_green:
            for square in self._highlight_green:
                square.color((12, 255, 0))
        if self._selected_square:
            self._selected_square.outline_piece((12, 255, 0))
        if not self._started:
            pygame.draw.rect(SCREEN, (100, 100, 100), self._ready_button_rect)
            if self._glow_ready:
                SCREEN.blit(self._ready_text_glow_surface, self._ready_text_rect)
            else:
                SCREEN.blit(self._ready_text_surface, self._ready_text_rect)
            for i, row in enumerate(self._init_form):
                for j, square in enumerate(row):
                    if square is not None:
                        self._squares[7-i][8-j].draw_piece(RANK_IMG[square])
        else:
            assert self._pov
            for i, row in enumerate(self._pov):
                for j, square in enumerate(row):
                    if square is not None:
                        if square.player == 2:
                            if self._gog.victor:
                                self._squares[7-i][8-j].outline_piece((255, 55, 54))
                                self._squares[7-i][8-j].draw_piece(RANK_IMG[square.rank])
                            else:
                                self._squares[7-i][8-j].draw_piece(ENEMY_PIECE_IMG)
                        else:
                            self._squares[7-i][8-j].draw_piece(RANK_IMG[square.rank])
            if self._get_ai_move:
                SCREEN.blit(self._calculating_text_surface, self._calculating_text_rect)
        if self._gog.victor:
            SCREEN.blit(self._outcome_text_surface[self._gog.victor], self._outcome_rect[self._gog.victor])
            pygame.draw.rect(SCREEN, (100, 100, 100), self._restart_button_rect)
            if self._glow_restart:
                SCREEN.blit(self._restart_text_glow_surface, self._restart_text_rect)
            else:
                SCREEN.blit(self._restart_text_surface, self._restart_text_rect)

        pygame.display.flip()

    def start(self):
        ai_thread = Thread(target=self._compute_ai_move)
        ai_thread.start()
        self._run()
        ai_thread.join(0)
        return self._restart

    def _compute_ai_move(self):
        while not self._restart and not self._exit:
            if not self._get_ai_move:
                continue
            move = self._ai.get_move()
            self._ai_move = move
            self._get_ai_move = False

    def _run(self):
        self._ai.set_pov(self._gog.set_player_pieces(self._ai.get_init_form(), 2))

        def init_pos_tick(event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._selected_square:
                    for i, row in enumerate(self._squares[5:8]):
                        for j, square in enumerate(row):
                            if self._init_form[2-i][8-j]:
                                continue
                            if square.touches(event.pos[0], event.pos[1]):
                                self._init_form[2-i][8-j] = \
                                    self._init_form[2 - self._selected_square.row + 5][8 - self._selected_square.col]
                                self._init_form[2 - self._selected_square.row + 5][8 - self._selected_square.col] = None
                    self._selected_square = None
                    self._highlight_green = []
                else:
                    highlight = []
                    for i, row in enumerate(self._squares[5:8]):
                        for j, square in enumerate(row):
                            if not self._init_form[2-i][8-j]:
                                highlight.append(square)
                                continue
                            if square.touches(event.pos[0], event.pos[1]):
                                self._selected_square = square
                                self._highlight_green = highlight
                if self._ready_button_rect.collidepoint(event.pos[0], event.pos[1]):
                    self._selected_square = None
                    self._highlight_green = []
                    self._pov = self._gog.set_player_pieces(self._init_form, 1)
                    self._started = True
            elif event.type == pygame.MOUSEMOTION:
                if self._ready_button_rect.collidepoint(event.pos[0], event.pos[1]):
                    self._glow_ready = True
                else:
                    self._glow_ready = False

        self._run_ticks(init_pos_tick, lambda: not self._started)

        self._ai.enemy_set_pieces()

        def main_tick(event):
            assert self._pov
            assert self._started
            if self._ai_move:
                next_event = self._gog.move(self._ai_move[0], self._ai_move[1], 2)
                self._ai.board_event((next_event[0][2], next_event[1]))
                self._highlight_orange = [self._squares[x][y] for x, y in self._ai_move]
                self._ai_move = None
            if self._gog.current_turn != 1 or self._get_ai_move:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self._selected_square:
                    game_event = None
                    for i, row in enumerate(self._squares):
                        for j, square in enumerate(row):
                            if self._pov[7-i][8-j] and self._pov[7-i][8-j].player == 1:
                                continue
                            if square.touches(event.pos[0], event.pos[1]):
                                game_event = self._gog.move((7 - self._selected_square.row, 8 - self._selected_square.col),
                                                           (7 - i, 8 - j), 1)
                    if game_event:
                        self._ai.board_event((game_event[0][2], game_event[1]))
                        self._get_ai_move = True
                        self._highlight_orange = []
                    self._selected_square = None
                    self._highlight_green = []
                else:
                    for i, row in enumerate(self._squares):
                        for j, square in enumerate(row):
                            if not self._pov[7-i][8-j] or self._pov[7-i][8-j].player != 1:
                                continue
                            if square.touches(event.pos[0], event.pos[1]):
                                self._selected_square = square
                    if self._selected_square:
                        highlight = []
                        for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                            if self._is_valid_destination(7 - self._selected_square.row - dr, 8 - self._selected_square.col - dc):
                                highlight.append(self._squares[self._selected_square.row + dr][self._selected_square.col + dc])
                        self._highlight_green = highlight
        self._run_ticks(main_tick, lambda: not self._gog.victor)

        def end_tick(event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._restart_button_rect.collidepoint(event.pos[0], event.pos[1]):
                    self._restart = True
            elif event.type == pygame.MOUSEMOTION:
                if self._restart_button_rect.collidepoint(event.pos[0], event.pos[1]):
                    self._glow_restart = True
                else:
                    self._glow_restart = False

        self._run_ticks(end_tick, lambda: not self._restart)

    def _run_ticks(self, tick, cond):
        clock = pygame.time.Clock()
        while cond():
            self._draw_board()
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._exit = True
                    sys.exit()
                tick(event)

    def _is_valid_destination(self, row, col):
        return 0 <= row < 8 and 0 <= col < 9 and (not self._pov[row][col] or self._pov[row][col].player == 2)

