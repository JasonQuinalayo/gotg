from functools import reduce
from collections import namedtuple

from rank import player_pieces, duel, DuelResult, Rank


class GOG:
    Piece = namedtuple('Piece', ['rank', 'player'])

    def __init__(self):
        self.board = [[None] * 9 for _ in range(8)]
        self.inverse_board = [[None] * 9 for _ in range(8)]
        self.victor = 0
        self._winning = [None, False, False]
        self._initialized = [None, False, False]
        self._started = False
        self._current_turn = 1

    def set_player_pieces(self, pieces, player):
        def is_valid_initial_position():
            player_pieces_copy = player_pieces.copy()
            valid_len = len(pieces) == 3 and reduce(lambda acc, cur: acc and len(cur) == 9, pieces, True)
            if not valid_len: return False
            for row in pieces:
                for piece in row:
                    if piece is not None:
                        if piece not in player_pieces_copy:
                            return False
                        player_pieces_copy[piece] -= 1
            return reduce(lambda acc, cur: acc and cur[1] == 0, player_pieces_copy.items(), True)

        assert not self._started
        assert player == 1 or player == 2
        assert not self._initialized[player]
        assert is_valid_initial_position()
        game_pieces = [[GOG.Piece(rank, player) if rank is not None else None for rank in row] for row in pieces]
        game_pieces_inverse = [x[::-1] for x in game_pieces[::-1]]
        if player == 1:
            self.board[0:3] = game_pieces
            self.inverse_board[5:8] = game_pieces_inverse
        else:
            self.inverse_board[0:3] = game_pieces
            self.board[5:8] = game_pieces_inverse
        self._initialized[player] = True
        if self._initialized[1] and self._initialized[2]:
            self._started = True
        return self.board if player == 1 else self.inverse_board

    MoveTuple = namedtuple('MoveTuple', ['pos1', 'pos2'])
    Tile = namedtuple('Move', ['row', 'col'])

    def move(self, pos1, pos2, player):
        assert self._started
        original = GOG.MoveTuple(GOG.Tile(pos1[0], pos1[1]), GOG.Tile(pos2[0], pos2[1])) if player == 1 \
            else GOG.MoveTuple(GOG.Tile(7 - pos1[0], 8 - pos1[1]), GOG.Tile(7 - pos2[0], 8 - pos2[1]))
        inverted = GOG.MoveTuple(GOG.Tile(pos1[0], pos1[1]), GOG.Tile(pos2[0], pos2[1])) if player == 2 \
            else GOG.MoveTuple(GOG.Tile(7 - pos1[0], 8 - pos1[1]), GOG.Tile(7 - pos2[0], 8 - pos2[1]))
        if self.victor or not self._is_valid_move(original.pos1, original.pos2):
            return False
        # if destination square has an enemy piece
        if self.board[original.pos2.row][original.pos2.col]:
            duel_result = duel(self.board[original.pos1.row][original.pos1.col],
                               self.board[original.pos2.row][original.pos2.col])
            if duel_result == DuelResult.ATTACKER_WINS:
                if self.board[original.pos2.row][original.pos2.col].rank == Rank.FLAG:
                    self.victor = player
                self.board[original.pos2.row][original.pos2.col] = self.board[original.pos1.row][original.pos1.col]
                self.board[original.pos1.row][original.pos1.col] = None
                self.inverse_board[inverted.pos2.row][inverted.pos2.col] = self.inverse_board[inverted.pos1.row][
                    inverted.pos1.col]
                self.inverse_board[inverted.pos1.row][inverted.pos1.col] = None
            elif duel_result == DuelResult.DRAW:
                self.board[original.pos2.row][original.pos2.col] = None
                self.board[original.pos1.row][original.pos1.col] = None
                self.inverse_board[inverted.pos2.row][inverted.pos2.col] = None
                self.inverse_board[inverted.pos1.row][inverted.pos1.col] = None
            else:
                if self.board[original.pos1.row][original.pos1.col].rank == Rank.FLAG:
                    self.victor = 1 if player == 2 else 2
                self.board[original.pos1.row][original.pos1.col] = None
                self.inverse_board[inverted.pos1.row][inverted.pos1.col] = None
        # else destination square is empty
        else:
            self.board[original.pos2.row][original.pos2.col] = self.board[original.pos1.row][original.pos1.col]
            self.board[original.pos1.row][original.pos1.col] = None
            self.inverse_board[inverted.pos2.row][inverted.pos2.col] = \
                self.inverse_board[inverted.pos1.row][inverted.pos1.col]
            self.inverse_board[inverted.pos1.row][inverted.pos1.col] = None
            if (original.pos2.row == 0 and self.board[original.pos2.row][original.pos2.col] == (Rank.FLAG, 2)) \
                    or (original.pos2.row == 7 and self.board[original.pos2.row][original.pos2.col] == (Rank.FLAG, 1)):
                if original.pos2.col - 1 > 0 \
                        and (self.board[original.pos2.row][original.pos2.col - 1] is None
                             or self.board[original.pos2.row][original.pos2.col - 1].player == player) \
                        and original.pos2.col + 1 < 9 \
                        and (self.board[original.pos2.row][original.pos2.col + 1] is None
                             or self.board[original.pos2.row][original.pos2.col + 1].player == player):
                    self.victor = player
                else:
                    self._winning[player] = True
        if self._winning[2 if player == 1 else 1] and not self.victor:
            self.victor = 2 if player == 1 else 1
        self._current_turn = 2 if player == 1 else 1
        return True

    def _is_valid_move(self, pos1, pos2):
        def is_within_board(row, col):
            return 0 <= row < 8 and 0 <= col < 9

        return is_within_board(pos1.row, pos1.col) and is_within_board(pos2.row, pos2.col) \
               and self.board[pos1.row][pos1.col] is not None \
               and self.board[pos1.row][pos1.col].player == self._current_turn \
               and abs(pos2.row - pos1.row) + abs(pos2.col - pos1.col) == 1 \
               and (self.board[pos2.row][pos2.col] is None
                    or self.board[pos2.row][pos2.col].player != self.board[pos1.row][pos1.col].player)
