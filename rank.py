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


beaten_by = {}


def get_beaten_by_regular(rank):
    return {x for x in Rank if x.value < rank.value}


for rank in Rank:
    if rank == Rank.PRIVATE:
        beaten_by[rank] = {Rank.SPY, Rank.FLAG}
    elif rank == Rank.FLAG:
        beaten_by[rank] = {Rank.FLAG}
    elif rank == Rank.SPY:
        beaten_by[rank] = get_beaten_by_regular(rank) ^ {Rank.PRIVATE}
    else:
        beaten_by[rank] = get_beaten_by_regular(rank)


def get_beats_regular(rank):
    return {x for x in Rank if x.value > rank.value}


beats = {}

for rank in Rank:
    if rank == Rank.PRIVATE:
        beats[rank] = get_beats_regular(rank) ^ {Rank.SPY}
    elif rank == Rank.FLAG:
        beats[rank] = get_beats_regular(rank) | {Rank.FLAG}
    elif rank == Rank.SPY:
        beats[rank] = {Rank.PRIVATE}
    else:
        beats[rank] = get_beats_regular(rank)
