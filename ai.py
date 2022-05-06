from collections import defaultdict

from rank import Rank, beats, beaten_by
from random import shuffle, randint
from gog import player_pieces, Piece, BoardManager
import math


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


move_dirs = ((0, 1), (1, 0), (-1, 0), (0, -1))


def _generate_valid_moves(pov, player):
    def is_valid_destination(row_num, col_num):
        return 0 <= row_num < 8 and 0 <= col_num < 9 and (pov[row_num][col_num] is None
                                                          or pov[row_num][col_num].player != player)

    valid_moves = []
    for i, row in enumerate(pov):
        for j, square in enumerate(row):
            if square is not None and square.player == player:
                for move_dir in move_dirs:
                    if is_valid_destination(i + move_dir[0], j + move_dir[1]):
                        valid_moves.append(((i, j), (i + move_dir[0], j + move_dir[1])))
    return valid_moves


def _get_random_move(pov, player):
    valid_moves = _generate_valid_moves(pov, player)
    if len(valid_moves) == 0:
        return None
    m = valid_moves[randint(0, len(valid_moves) - 1)]
    return (m[0][0], m[0][1]), (m[1][0], m[1][1])


class AI:
    def __init__(self, player):
        self._player = player
        self._pov = None

    def set_pov(self, pov):
        self._pov = pov

    def get_init_form(self):
        raise NotImplementedError()

    def get_move(self):
        raise NotImplementedError()

    def board_event(self, event):
        raise NotImplementedError()

    def enemy_set_pieces(self):
        raise NotImplementedError()


class AIRandom(AI):
    def get_init_form(self):
        return generate_random_init_form()

    def board_event(self, event):
        return

    def enemy_set_pieces(self):
        return

    def get_move(self):
        assert self._pov
        return _get_random_move(self._pov, self._player)


def _duel_dict_copy(duel_dict):
    copy = {}
    for key, value in duel_dict.items():
        copy[key] = value.copy()
    return copy


def _update_possibilities(self, event):
    eliminated_pieces = event[1]
    if not eliminated_pieces:
        return
    move = event[0]
    if len(eliminated_pieces) == 2:
        own_piece = eliminated_pieces[0] if eliminated_pieces[0].player == self._player else eliminated_pieces[1]
        enemy_piece = eliminated_pieces[0] if eliminated_pieces[0].player != self._player else eliminated_pieces[1]
        for rank in self._possible_ranks_per_piece[enemy_piece]:
            if rank == own_piece.rank: continue
            self._possible_pieces_per_rank[rank].remove(enemy_piece)
        self._possible_ranks_per_piece[enemy_piece] = {own_piece.rank}
    else:
        enemy_piece = eliminated_pieces[0] if eliminated_pieces[0].player != self._player else \
            self._pov[move[1][0]][move[1][1]]
        own_piece = eliminated_pieces[0] if eliminated_pieces[0].player == self._player else \
            self._pov[move[1][0]][move[1][1]]
        duel_dict = beats if enemy_piece is eliminated_pieces[0] else beaten_by
        enemy_piece_cannot_be = duel_dict[own_piece.rank] | {own_piece.rank}
        for rank in enemy_piece_cannot_be:
            if rank in self._possible_ranks_per_piece[enemy_piece]:
                self._possible_pieces_per_rank[rank].remove(enemy_piece)
        self._possible_ranks_per_piece[enemy_piece] -= enemy_piece_cannot_be
        self._possible_ranks_per_piece[enemy_piece].discard(Rank.FLAG)

    _clean_possibilities(self)


def _clean_possibilities(self):
    modified = True
    while modified:
        modified = False
        for piece, ranks in self._possible_ranks_per_piece.items():
            if len(ranks) == 1:
                for rank in ranks:
                    modified = _update_pieces_from_clean(self, rank)
                if modified: break
        for rank, pieces in self._possible_pieces_per_rank.items():
            if (rank != Rank.PRIVATE and rank != Rank.SPY and len(pieces) == 1) or (rank == Rank.PRIVATE and
                                                                                    len(pieces) == 6) \
                    or (rank == Rank.SPY and len(pieces) == 2):
                modified = modified or _update_ranks_from_clean(self, rank, pieces)
                if modified: break


def _update_ranks_from_clean(self, rank, pieces):
    modified = False
    for piece in pieces:
        if len(self._possible_ranks_per_piece[piece]) != 1:
            for piece_probable_rank in self._possible_ranks_per_piece[piece]:
                if piece_probable_rank == rank: continue
                self._possible_pieces_per_rank[piece_probable_rank].discard(piece)
            self._possible_ranks_per_piece[piece] = {rank}
            modified = True
    return modified


def _update_pieces_from_clean(self, rank):
    sure_pieces = set()
    modified = False
    for piece in self._possible_pieces_per_rank[rank]:
        if len(self._possible_ranks_per_piece[piece]) == 1:
            sure_pieces.add(piece)
    if len(sure_pieces) == player_pieces[rank]:
        if len(self._possible_pieces_per_rank[rank]) != player_pieces[rank]:
            for piece in self._possible_pieces_per_rank[rank]:
                if piece in sure_pieces: continue
                self._possible_ranks_per_piece[piece].discard(rank)
            self._possible_pieces_per_rank[rank] = sure_pieces
            modified = True
    return modified


class AISmart(AI):
    def __init__(self, player):
        super().__init__(player)
        self._possible_ranks_per_piece = {}
        self._possible_pieces_per_rank = {}
        for rank in Rank:
            self._possible_pieces_per_rank[rank] = set()

    def get_init_form(self):
        return generate_random_init_form()

    def board_event(self, event):
        assert self._pov
        if not event: return
        _update_possibilities(self, event)

    def enemy_set_pieces(self):
        assert self._pov
        for row in self._pov[5:8]:
            for square in row:
                if square:
                    self._possible_ranks_per_piece[square] = set()
                    for rank in Rank:
                        self._possible_pieces_per_rank[rank].add(square)
                        self._possible_ranks_per_piece[square].add(rank)

    def get_move(self):
        assert self._pov
        monte_carlo = AISmart.MonteCarlo(self._pov, self._player, self._possible_ranks_per_piece)
        return monte_carlo.get_move()
        # pov_c = [[x for x in row] for row in self._pov]
        # ranks_per_piece_c = _duel_dict_copy(self._possible_ranks_per_piece)
        # pieces_per_rank_c = _duel_dict_copy(self._possible_pieces_per_rank)
        # initial_time = time.time_ns()
        # timeout_time = initial_time + 5 * 1_000_000_000
        # mini_max = AISmart.MiniMax(self._player, pov_c, ranks_per_piece_c, pieces_per_rank_c, initial_time,
        #                              timeout_time)
        # return mini_max.get_move()

    class MonteCarlo:
        def __init__(self, pov, player, possible_ranks_per_piece):
            self._pov = pov
            self._player = player
            self._possible_ranks_per_piece = possible_ranks_per_piece
            moves = _generate_valid_moves(pov, player)
            winning_moves = defaultdict(int)
            for _ in range(100):
                beginning_move = moves[randint(0, len(moves) - 1)]
                board = self._generate_valid_board_configuration()
                board_manager = BoardManager(board)
                board_manager.move(beginning_move)
                current_turn = 1 if player == 2 else 2
                while not board_manager.get_victor():
                    move = _get_random_move(board, current_turn)
                    board_manager.move(move)
                    current_turn = 2 if current_turn == 1 else 1
                if board_manager.get_victor() == player:
                    winning_moves[beginning_move] += 1
            if len(winning_moves) == 0:
                self._best_move = _get_random_move(pov, player)
            else:
                self._best_move = max(winning_moves.items(), key=lambda x: x[1])[0]

        def _generate_valid_board_configuration(self):
            board_configuration = [[None] * 9 for _ in range(8)]
            enemy_pieces = []
            for i, row in enumerate(self._pov):
                for j, square in enumerate(row):
                    if square:
                        if square.player == self._player:
                            board_configuration[i][j] = square
                        else:
                            enemy_pieces.append(((i,j), self._possible_ranks_per_piece[square].copy()))
            enemy_pieces.sort(key=lambda x : len(x[1]))
            enemy_pieces_count = defaultdict(int)
            for i in range(len(enemy_pieces)):
                if i == len(enemy_pieces) - 1 and enemy_pieces_count[Rank.FLAG] == 0:
                    rank = Rank.FLAG
                else:
                    rank = list(enemy_pieces[i][1])[randint(0, len(enemy_pieces[i][1]) - 1)]
                enemy_pieces_count[rank] += 1
                board_configuration[enemy_pieces[i][0][0]][enemy_pieces[i][0][1]] = Piece(rank, 1 if self._player == 2 else 2)
                if enemy_pieces_count[rank] == player_pieces[rank]:
                    for j in range(i + 1, len(enemy_pieces)):
                        enemy_pieces[j][1].discard(rank)
                        if j > i + 1 and len(enemy_pieces[j-1][1]) > len(enemy_pieces[j][1]):
                            enemy_pieces[j-1], enemy_pieces[j] = enemy_pieces[j], enemy_pieces[j-1]

            return board_configuration

        def get_move(self):
            return self._best_move

    class MiniMax:
        # non functional (buggy) xD
        def __init__(self, player, pov, can_be, pieces_for_each_rank, init_time, timeout_time):
            assert player == 2
            self._player = player
            self._pov = pov
            self._possible_ranks_per_piece = can_be
            self._possible_pieces_per_rank = pieces_for_each_rank
            self._init_time = init_time
            self._timeout_time = timeout_time
            self._best_move = None
            self._initial_depth = 3
            self._search(self._initial_depth, -math.inf, math.inf, player)

        # -1 if mover dies, 0 if draw, 1 if mover lives
        def _get_possible_outcomes(self, move):
            if not self._pov[move[1][0]][move[1][1]]:
                return (1, 1),
            own_piece = self._pov[move[0][0]][move[0][1]] if self._pov[move[0][0]][move[0][1]].player == self._player \
                else self._pov[move[1][0]][move[1][1]]
            enemy_piece = self._pov[move[1][0]][move[1][1]] if self._pov[move[1][0]][move[1][1]].player != self._player \
                else self._pov[move[0][0]][move[0][1]]
            own_piece_is_mover = own_piece is self._pov[move[0][0]][move[0][1]]
            prob_denom = sum([player_pieces[x] for x in self._possible_ranks_per_piece[enemy_piece]])
            if own_piece.rank == Rank.FLAG:
                win_prob_num = 0 if not own_piece_is_mover or Rank.FLAG not in self._possible_ranks_per_piece[
                    enemy_piece] else 1
                draw_prob_num = 0
                lose_prob_num = prob_denom if not own_piece_is_mover or \
                                              Rank.FLAG not in self._possible_ranks_per_piece[
                                                  enemy_piece] else prob_denom - 1
            else:
                win_prob_num = sum([player_pieces[x] for x in beats[own_piece.rank] if
                                    x in self._possible_ranks_per_piece[enemy_piece]])
                draw_prob_num = player_pieces[own_piece.rank] if own_piece.rank in self._possible_ranks_per_piece[
                    enemy_piece] else 0
                lose_prob_num = sum(
                    [player_pieces[x] for x in beaten_by[own_piece.rank] if
                     x in self._possible_ranks_per_piece[enemy_piece]])
            assert prob_denom == win_prob_num + draw_prob_num + lose_prob_num
            if own_piece_is_mover:
                return (
                    (-1, lose_prob_num / prob_denom),
                    (0, draw_prob_num / prob_denom),
                    (1, win_prob_num / prob_denom),
                )
            return (
                (-1, win_prob_num / prob_denom),
                (0, draw_prob_num / prob_denom),
                (1, lose_prob_num / prob_denom),
            )

        def _try_outcome(self, move, outcome):
            if not self._pov[move[1][0]][move[1][1]]:
                self._pov[move[1][0]][move[1][1]] = self._pov[move[0][0]][move[0][1]]
                self._pov[move[0][0]][move[0][1]] = None
                return
            if outcome == -1:
                eliminated_pieces = self._pov[move[0][0]][move[0][1]],
                self._pov[move[0][0]][move[0][1]] = None
            elif outcome == 0:
                eliminated_pieces = self._pov[move[0][0]][move[0][1]], self._pov[move[1][0]][move[1][1]]
                self._pov[move[0][0]][move[0][1]] = None
                self._pov[move[1][0]][move[1][1]] = None
            else:
                eliminated_pieces = self._pov[move[1][0]][move[1][1]],
                self._pov[move[1][0]][move[1][1]] = self._pov[move[0][0]][move[0][1]]
                self._pov[move[0][0]][move[0][1]] = None
            _update_possibilities(self, (move, eliminated_pieces))

        def _evaluate(self):
            res = 0
            own_flag_coord = None
            enemy_flag = False
            for i, row in enumerate(self._pov):
                for j, square in enumerate(row):
                    if square:
                        if square.player == self._player:
                            if square.rank == Rank.FLAG:
                                own_flag_coord = (i,j)
                            else:
                                res += square.rank.value
                        else:
                            if Rank.FLAG in self._possible_ranks_per_piece[square]:
                                enemy_flag = True
                            else:
                                res -= 6
            if own_flag_coord is None:
                return -math.inf
            if not enemy_flag:
                return math.inf
            res += 10 * own_flag_coord[1]
            return res

        def _get_current_state_copy(self):
            cb_copy = _duel_dict_copy(self._possible_ranks_per_piece)
            pfer_copy = _duel_dict_copy(self._possible_pieces_per_rank)
            pov_copy = [[x for x in row] for row in self._pov]
            return [cb_copy, pfer_copy, pov_copy]

        def _revert_state(self, state):
            self._possible_ranks_per_piece = state[0]
            self._possible_pieces_per_rank = state[1]
            self._pov = state[2]

        def _search(self, depth, alpha, beta, player_to_move):
            if depth == 0:
                return self._evaluate()
            valid_moves = _generate_valid_moves(self._pov, player_to_move)
            for move in valid_moves:
                for outcome, probability in self._get_possible_outcomes(move):
                    if not probability: continue
                    current_state = self._get_current_state_copy()
                    self._try_outcome(move, outcome)
                    valid = True
                    for piece, ranks in self._possible_ranks_per_piece.items():
                        # invalid state since a piece has no probable rank
                        if len(ranks) == 0:
                            valid = False
                            break
                    if not valid:
                        self._revert_state(current_state)
                        continue
                    evaluation = -(probability * self._search(depth - 1, -beta/probability, -alpha/probability, 1 if player_to_move == 2 else 2))
                    self._revert_state(current_state)
                    if evaluation >= beta:
                        return beta
                    if evaluation > alpha:
                        alpha = evaluation
                        if depth == self._initial_depth:
                            self._best_move = move
            return alpha

        def get_move(self):
            return self._best_move
