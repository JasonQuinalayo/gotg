from gog import GOG
from game import Game
from ai import generate_random_init_form


def ai_test(ai1, ai2):
    results = [None, 0, 0]
    for _ in range(1000):
        game = GOG()
        ai1.set_init_form()
        ai2.set_init_form()
        while not game.victor:
            ai1.move()
            ai2.move()
        results[game.victor] += 1
    print(results)


def main():
    gog = GOG()
    game = Game(gog)
    gog.set_player_pieces(generate_random_init_form(), 2)
    game.run()


if __name__ == '__main__':
    main()
