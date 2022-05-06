from gog import GOG
from ai import AISmart
from game import Game


def main():
    restart = True
    while restart:
        gog = GOG()
        ai = AISmart(2)
        game = Game(gog, ai)
        restart = game.start()


if __name__ == '__main__':
    main()
