def print_board(board):
    print()
    b = [[str(i) for i in range(-1,9)]] + \
        [[str(idx)] + [str(x.player) + "_" + str(x.rank.value) if x is not None else '#' for x in row] for
         idx, row in enumerate(board)]
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in b]))
