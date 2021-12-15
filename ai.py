from rank import player_pieces
from random import shuffle, randint


def generate_random_init_form():
    form = []
    for rank, n in player_pieces.items():
        for _ in range(n):
            form.append(rank)
    for _ in range(6):
        form.append(None)
    shuffle(form)
    form = [form[9 * i: 9 * (i + 1)] for i in range(3)]
    return form


moves = ((0,1), (1,0), (-1,0), (0,-1))


class AI:
    def __init__(self, game, player):
        self._game = game
        self._player = player
        self._pov = None

    def set_init_form(self):
        raise NotImplementedError()

    def move(self):
        raise NotImplementedError()


class AIRandom(AI):
    def set_init_form(self):
        self._pov = self._game.set_player_pieces(generate_random_init_form(), self._player)

    def move(self):
        def is_valid_destination(row_num, col_num):
            return 0 <= row_num < 8 and 0 <= col_num < 9 and (self._pov[row_num][col_num] is None
                                                              or self._pov[row_num][col_num].player != self._player)
        valid_moves = []
        for i, row in enumerate(self._pov):
            for j, square in enumerate(row):
                if square is not None and square.player == self._player:
                    for move in moves:
                        if is_valid_destination(i + move[0], j + move[1]):
                            valid_moves.append(((i, j), (i+move[0], j+move[1])))
        if len(valid_moves) == 0:
            return
        m = valid_moves[randint(0, len(valid_moves) - 1)]
        self._game.move((m[0][0], m[0][1]), (m[1][0], m[1][1]), self._player)


class AIMinMax(AI):
    def set_init_form(self):
        pass

    def move(self):
        pass
