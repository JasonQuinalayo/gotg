from functools import reduce

from rank import Rank, beaten_by

player_pieces = {
    Rank.FLAG: 1,
    Rank.SPY: 2,
    Rank.PRIVATE: 6,
    Rank.SERGEANT: 1,
    Rank.SECOND_LIEUTENANT: 1,
    Rank.FIRST_LIEUTENANT: 1,
    Rank.CAPTAIN: 1,
    Rank.MAJOR: 1,
    Rank.LIEUTENANT_COLONEL: 1,
    Rank.COLONEL: 1,
    Rank.GENERAL_ONE: 1,
    Rank.GENERAL_TWO: 1,
    Rank.GENERAL_THREE: 1,
    Rank.GENERAL_FOUR: 1,
    Rank.GENERAL_FIVE: 1,
}


class Piece:
    def __init__(self, rank, player):
        self.rank = rank
        self.player = player


class BoardManager:
    def __init__(self, board):
        def is_valid_board():
            if len(board) != 8 and len(board[0]) != 9:
                return False
            player_pieces_count = {1: {k: 0 for k in player_pieces.keys()}, 2: {k: 0 for k in player_pieces.keys()}}
            for row in board:
                for square in row:
                    if square:
                        assert square.player == 1 or square.player == 2
                        assert isinstance(square.rank, Rank)
                        player_pieces_count[square.player][square.rank] += 1
            for i in [1,2]:
                for k, v in player_pieces_count[i].items():
                    if (k == Rank.FLAG and v == 0) or (v > player_pieces[k]):
                        return False
            return True
        assert is_valid_board()
        self.board = board
        self._winning = {1: False, 2: False}
        self.victor = 0

    def get_victor(self):
        return self.victor

    def move(self, move):
        pos1, pos2 = move
        assert self.board[pos1[0]][pos1[1]]
        player = self.board[pos1[0]][pos1[1]].player
        other_player = 1 if player == 2 else 2
        eliminated_pieces = None
        # if destination square has an enemy piece
        if self.board[pos2[0]][pos2[1]]:
            if self.board[pos2[0]][pos2[1]].rank in beaten_by[self.board[pos1[0]][pos1[1]].rank]:
                if self.board[pos2[0]][pos2[1]].rank == Rank.FLAG:
                    self.victor = player
                eliminated_pieces = self.board[pos2[0]][pos2[1]],
                self.board[pos2[0]][pos2[1]] = self.board[pos1[0]][pos1[1]]
                self.board[pos1[0]][pos1[1]] = None
            elif self.board[pos1[0]][pos1[1]].rank == self.board[pos2[0]][pos2[1]].rank:
                eliminated_pieces = self.board[pos1[0]][pos1[1]], self.board[pos2[0]][pos2[1]]
                self.board[pos2[0]][pos2[1]] = None
                self.board[pos1[0]][pos1[1]] = None
            else:
                if self.board[pos1[0]][pos1[1]].rank == Rank.FLAG:
                    self.victor = other_player
                eliminated_pieces = self.board[pos1[0]][pos1[1]],
                self.board[pos1[0]][pos1[1]] = None
        # else destination square is empty
        else:
            self.board[pos2[0]][pos2[1]] = self.board[pos1[0]][pos1[1]]
            self.board[pos1[0]][pos1[1]] = None
            flag_reaches_opponent_back_row = \
                (pos2[0] == 0 and self.board[pos2[0]][pos2[1]].rank == Rank.FLAG
                 and self.board[pos2[0]][pos2[1]].player == 2) \
                or (pos2[0] == 7 and self.board[pos2[0]][pos2[1]].rank == Rank.FLAG
                    and self.board[pos2[0]][pos2[1]].player == 1)
            if flag_reaches_opponent_back_row:
                no_enemy_piece_is_currently_beside_flag = \
                    (pos2[1] - 1 < 0 or self.board[pos2[0]][pos2[1] - 1] is None
                     or self.board[pos2[0]][pos2[1] - 1].player == player) \
                    and (pos2[1] + 1 >= 9 or self.board[pos2[0]][pos2[1] + 1] is None
                         or self.board[pos2[0]][pos2[1] + 1].player == player)
                if no_enemy_piece_is_currently_beside_flag:
                    self.victor = player
                else:
                    self._winning[player] = True
        if self._winning[other_player] and not self.victor:
            self.victor = other_player
        return eliminated_pieces


class GOG:
    def __init__(self):
        self.board = [[None] * 9 for _ in range(8)]
        self._board_manager = None
        self.inv_board = [[None] * 9 for _ in range(8)]
        self._inv_board_manager = None
        self.victor = 0
        self._initialized = {1: False, 2: False}
        self._started = False
        self.current_turn = 1

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
        game_pieces = [[Piece(rank, player) if rank is not None else None for rank in row] for row in pieces]
        game_pieces_inverse = [x[::-1] for x in game_pieces[::-1]]
        if player == 1:
            self.board[0:3] = game_pieces
            self.inv_board[5:8] = game_pieces_inverse
        else:
            self.inv_board[0:3] = game_pieces
            self.board[5:8] = game_pieces_inverse
        self._initialized[player] = True
        if self._initialized[1] and self._initialized[2]:
            self._started = True
            self._board_manager = BoardManager(self.board)
            self._inv_board_manager = BoardManager(self.inv_board)
        return self.board if player == 1 else self.inv_board

    def move(self, pos1, pos2, player):
        assert self._started

        def is_valid_move(p1, p2):
            def is_within_board(row, col):
                return 0 <= row < 8 and 0 <= col < 9

            return is_within_board(p1[0], p1[1]) and is_within_board(p2[0], p2[1]) \
                   and self.board[p1[0]][p1[1]] is not None \
                   and self.board[p1[0]][p1[1]].player == self.current_turn \
                   and abs(p2[0] - p1[0]) + abs(p2[1] - p1[1]) == 1 \
                   and (self.board[p2[0]][p2[1]] is None
                        or self.board[p2[0]][p2[1]].player != self.board[p1[0]][p1[1]].player)

        original_move = ((pos1[0], pos1[1]), (pos2[0], pos2[1])) if player == 1 else \
            ((7 - pos1[0], 8 - pos1[1]), (7 - pos2[0], 8 - pos2[1]))
        inverted_move = ((pos1[0], pos1[1]), (pos2[0], pos2[1])) if player == 2 \
            else ((7 - pos1[0], 8 - pos1[1]), (7 - pos2[0], 8 - pos2[1]))

        if self.victor or not is_valid_move(original_move[0], original_move[1]):
            return None

        eliminated_pieces = self._board_manager.move(original_move)
        self._inv_board_manager.move(inverted_move)

        self.victor = self._board_manager.get_victor()

        self.current_turn = 2 if player == 1 else 1

        return ((
            None,
            ((original_move[0][0], original_move[0][1]), (original_move[1][0], original_move[1][1])),
            ((inverted_move[0][0], inverted_move[0][1]), (inverted_move[1][0], inverted_move[1][1])),
        ), eliminated_pieces)