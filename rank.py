from enum import Enum, unique


@unique
class Rank(Enum):
    FLAG = 0
    PRIVATE = 1
    SERGEANT = 2
    SECOND_LIEUTENANT = 3
    FIRST_LIEUTENANT = 4
    CAPTAIN = 5
    MAJOR = 6
    LIEUTENANT_COLONEL = 7
    COLONEL = 8
    GENERAL_ONE = 9
    GENERAL_TWO = 10
    GENERAL_THREE = 11
    GENERAL_FOUR = 12
    GENERAL_FIVE = 13
    SPY = 14


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


class DuelResult(Enum):
    ATTACKER_WINS = 1
    DRAW = 0
    ATTACKER_LOSES = -1


def duel(attacker, defender):
    if defender.rank == Rank.FLAG or (attacker.rank == Rank.PRIVATE and defender.rank == Rank.SPY):
        return DuelResult.ATTACKER_WINS
    if attacker.rank == Rank.SPY and defender.rank == Rank.PRIVATE:
        return DuelResult.ATTACKER_LOSES
    if attacker.rank == defender.rank:
        return DuelResult.DRAW
    if attacker.rank.value > defender.rank.value:
        return DuelResult.ATTACKER_WINS
    return DuelResult.ATTACKER_LOSES
