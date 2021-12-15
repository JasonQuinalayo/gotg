import unittest
from gog import GOG
from rank import Rank

FLG, PRVT, SRGNT, SND_LT, FST_LT, CPTN, MJR, LT_CLNL, CLNL, G_ONE, G_TWO, G_THREE, G_FOUR, G_FIVE, SPY = Rank

initial_pos_one = [
    [PRVT, PRVT, CPTN, G_ONE, G_TWO, MJR, G_FOUR, None, None],
    [PRVT, SPY, SND_LT, CLNL, PRVT, LT_CLNL, FST_LT, None, None],
    [PRVT, FLG, G_FIVE, SPY, G_THREE, SRGNT, PRVT, None, None],
]

initial_pos_two = [
    [PRVT, FLG, G_FIVE, SPY, G_THREE, SRGNT, PRVT, None, None],
    [PRVT, PRVT, CPTN, G_ONE, G_TWO, MJR, G_FOUR, None, None],
    [PRVT, SPY, SND_LT, CLNL, PRVT, LT_CLNL, FST_LT, None, None],
]


def print_board(board):
    print()
    b = [[str(i) for i in range(-1,9)]] + \
        [[str(idx)] + [str(x.player) + "_" + str(x.rank.value) if x is not None else '#' for x in row] for
         idx, row in enumerate(board)]
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in b]))


class InitialPosTest(unittest.TestCase):
    def setUp(self) -> None:
        self.game = GOG()

    def test_valid_initial_pos(self):
        self.assertIsNotNone(self.game.set_player_pieces(initial_pos_one, 1))
        self.assertIsNotNone(self.game.set_player_pieces(initial_pos_two, 2))

    def tearDown(self) -> None:
        self.game = None


def inv(pos):
    return 7 - pos[0], 8 - pos[1]


def inv_m(pos1, pos2):
    return inv(pos1), inv(pos2)


def get_move_povs(pos1, pos2, player):
    return [
        (pos1, pos2) if player == 1 else inv_m(pos1, pos2),
        inv_m(pos1, pos2) if player == 1 else (pos1, pos2)
    ]


class GameTest(unittest.TestCase):
    def setUp(self) -> None:
        self.game = GOG()
        self.pov = [
            None,
            self.game.set_player_pieces(initial_pos_one, 1),
            self.game.set_player_pieces([row[::-1] for row in initial_pos_two[::-1]], 2),
        ]

    def _assert_mover_lives(self, pos1, pos2, player):
        player_move, _ = get_move_povs(pos1, pos2, player)
        piece = self.pov[player][player_move[0][0]][player_move[0][1]]
        self._assert_movement(pos1, pos2, player, piece)

    def _assert_mover_dies(self, pos1, pos2, player):
        player_move, _ = get_move_povs(pos1, pos2, player)
        piece = self.pov[player][player_move[1][0]][player_move[1][1]]
        self._assert_movement(pos1, pos2, player, piece)

    def _assert_draw(self, pos1, pos2, player):
        self._assert_movement(pos1, pos2, player, None)

    def _assert_movement(self, pos1, pos2, player, surviving_piece):
        player_move, other_move = get_move_povs(pos1, pos2, player)
        other_player = 1 if player == 2 else 2
        old_boards = [
            None,
            [row[:] for row in self.pov[1]],
            [row[:] for row in self.pov[2]]
        ]
        self.assertTrue(self.game.move(player_move[0], player_move[1], player))
        for i in range(8):
            if i != player_move[0][0] and i != player_move[1][0]:
                self.assertListEqual(old_boards[player][i], self.pov[player][i])
            if i != other_move[0][0] and i != other_move[1][0]:
                self.assertListEqual(old_boards[other_player][i], self.pov[other_player][i])
        if player_move[0][0] != player_move[1][0]:
            for i in range(9):
                if i != player_move[0][1]:
                    self.assertEqual(old_boards[player][player_move[0][0]][i], self.pov[player][player_move[0][0]][i])
                if i != player_move[1][1]:
                    self.assertEqual(old_boards[player][player_move[1][0]][i], self.pov[player][player_move[1][0]][i])
                if i != other_move[0][1]:
                    self.assertEqual(old_boards[other_player][other_move[0][0]][i],
                                     self.pov[other_player][other_move[0][0]][i])
                if i != other_move[1][1]:
                    self.assertEqual(old_boards[other_player][other_move[1][0]][i],
                                     self.pov[other_player][other_move[1][0]][i])
        else:
            for i in range(9):
                if i != player_move[0][1] and i != player_move[1][1]:
                    self.assertEqual(old_boards[player][player_move[0][0]][i], self.pov[player][player_move[0][0]][i])
                    self.assertEqual(old_boards[player][player_move[1][0]][i], self.pov[player][player_move[1][0]][i])
                if i != other_move[0][1] and i != other_move[1][1]:
                    self.assertEqual(old_boards[other_player][other_move[0][0]][i],
                                     self.pov[other_player][other_move[0][0]][i])
                    self.assertEqual(old_boards[other_player][other_move[1][0]][i],
                                     self.pov[other_player][other_move[1][0]][i])
        self.assertIsNone(self.pov[player][player_move[0][0]][player_move[0][1]])
        self.assertEqual(surviving_piece, self.pov[player][player_move[1][0]][player_move[1][1]])
        self.assertIsNone(self.pov[other_player][other_move[0][0]][other_move[0][1]])
        self.assertEqual(surviving_piece, self.pov[other_player][other_move[1][0]][other_move[1][1]])

    def _assert_no_movement(self, pos1, pos2, player, msg):
        player_move, _ = get_move_povs(pos1, pos2, player)
        old_boards = [
            None,
            [row[:] for row in self.pov[1]],
            [row[:] for row in self.pov[2]]
        ]
        self.assertFalse(self.game.move(player_move[0], player_move[1], 1), msg)
        for i in range(8):
            self.assertListEqual(old_boards[1][i], self.pov[1][i])
            self.assertListEqual(old_boards[2][i], self.pov[2][i])

    def test_valid_moves(self):
        self._assert_mover_lives((2, 6), (3, 6), 1)
        self._assert_mover_lives((5, 6), (4, 6), 2)
        self._assert_mover_lives((3, 6), (3, 5), 1)
        self._assert_mover_lives((4, 6), (4, 5), 2)
        self._assert_mover_lives((3, 5), (3, 6), 1)
        self._assert_mover_lives((4, 5), (4, 6), 2)
        self._assert_mover_lives((3, 6), (2, 6), 1)
        self._assert_mover_lives((4, 6), (3, 6), 2)
        self._assert_mover_lives((2, 6), (2, 7), 1)
        self._assert_mover_lives((3, 6), (4, 6), 2)
        self._assert_mover_lives((1, 6), (2, 6), 1)
        self._assert_mover_lives((5, 5), (4, 5), 2)
        self._assert_mover_lives((2, 6), (3, 6), 1)
        self._assert_mover_dies((4, 6), (3, 6), 2)
        self._assert_mover_lives((2, 5), (3, 5), 1)
        self._assert_draw((4, 5), (3, 5), 2)
        self._assert_mover_lives((2, 0), (3, 0), 1)

    def test_invalid_moves(self):
        self._assert_no_movement((2, 1), (3, 2), 1, 'Diagonal')
        self._assert_no_movement((2, 1), (1, 1), 1, 'Occupied')
        self._assert_no_movement((2, 1), (2, 1), 1, 'Same Spot')
        self._assert_no_movement((3, 1), (2, 1), 1, 'No piece tile')
        self._assert_no_movement((5, 1), (4, 1), 1, 'Enemy piece')
        self._assert_no_movement((2, 0), (2, -1), 1, 'Out of bounds')
        self._assert_no_movement((2, 0), (4, 0), 1, 'Many steps')
        self._assert_no_movement((2, 0), (9, 10), 1, 'Out of bounds')
        self._assert_no_movement((5, 0), (4, 0), 2, 'Not turn')
        self._assert_mover_lives((2, 0), (3, 0), 1)
        self._assert_no_movement((3, 0), (4, 0), 1, 'Not turn')

    # 1_flag  kills 2_flag
    def test_game1(self):
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((2, 1), (3, 1), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 1), (4, 1), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((3, 1), (4, 1), 1)
        self.assertEqual(self.game.victor, 1)

    # 2_flag kills 1_flag
    def test_game2(self):
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((2, 1), (3, 1), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 1), (4, 1), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((2, 0), (3, 0), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 1), (3, 1), 2)
        self.assertEqual(self.game.victor, 2)

    # 2_general_5 kills 1_flag
    def test_game3(self):
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((2, 1), (3, 1), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 2), (4, 2), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((3, 1), (3, 2), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 2), (3, 2), 2)
        self.assertEqual(self.game.victor, 2)

    # 2_flag reaches row 1 but doesn't win immediately due to neighboring enemy pieces
    # wins after player 1 does not capture 2_flag
    def test_game4(self):
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((2, 1), (3, 1), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 1), (4, 1), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((3, 1), (3, 0), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 1), (3, 1), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((2, 2), (3, 2), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((3, 1), (2, 1), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((1, 2), (2, 2), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 2), (4, 2), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((1, 1), (1, 2), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((2, 1), (1, 1), 2)
        self.assertFalse(self.game.victor)
        self._assert_draw((3, 2), (4, 2), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((7, 6), (7, 7), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((2, 2), (3, 2), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((7, 7), (7, 6), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((1, 2), (2, 2), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((7, 6), (7, 7), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((0, 2), (1, 2), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 5), (4, 5), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((0, 1), (0, 2), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 5), (3, 5), 2)
        self.assertFalse(self.game.victor)
        self._assert_draw((2, 5), (3, 5), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((1, 1), (0, 1), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((0, 6), (0, 7), 1)
        self.assertEqual(self.game.victor, 2)

    # 1_flag reaches row 8 and wins immediately
    def test_game5(self):
        self._assert_mover_lives((2, 1), (3, 1), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 1), (4, 1), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((2, 3), (3, 3), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 1), (4, 0), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((3, 3), (4, 3), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 2), (4, 2), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 3), (4, 4), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 2), (4, 3), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 4), (4, 5), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 3), (4, 4), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 5), (5, 5), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 3), (4, 3), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 5), (6, 5), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 3), (3, 3), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((2, 2), (2, 3), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((3, 3), (2, 3), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_dies((2, 4), (2, 3), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((6, 2), (5, 2), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((6, 5), (6, 4), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 2), (4, 2), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((6, 4), (5, 4), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 2), (3, 2), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 4), (6, 4), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 4), (5, 4), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((3, 1), (4, 1), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((7, 2), (6, 2), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((4, 1), (5, 1), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_dies((5, 4), (6, 4), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_dies((6, 4), (7, 4), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((6, 2), (5, 2), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_dies((1, 3), (2, 3), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 2), (4, 2), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 1), (5, 2), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((6, 1), (5, 1), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((5, 2), (6, 2), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((7, 1), (6, 1), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((1, 4), (1, 3), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((6, 3), (5, 3), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((1, 3), (2, 3), 1)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((7, 3), (6, 3), 2)
        self.assertFalse(self.game.victor)
        self._assert_mover_lives((6, 2), (7, 2), 1)
        self.assertEqual(self.game.victor, 1)

    def tearDown(self) -> None:
        self.game = None
        self.pov = None


if __name__ == 'main':
    unittest.main()
