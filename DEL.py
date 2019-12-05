import numpy as np
import random as rd
import copy as cp

class World:
    """
    a world is a set of statements/facts about the current situation

    attributes:
    on_table: played cards on the on the table
    player1_hand: list of cards that player 1 has currently on his hand
    player2_hand: list of cards that player 2 has currently on his hand
    """

    def __init__(self):
        self.on_table = []
        self.player1_hand = []
        self.player2_hand = []
        self.blitz = 0

    def __str__(self):
        """
        converts the world into a string, needed for printing conveniently
        """
        return f'w = on table: {self.on_table} p1: {self.player1_hand} p2: {self.player2_hand}, blitz: {self.blitz}'

    #  hash & eq needed for comparing worlds, equal worlds have the same hash
    def __hash__(self):
        """
        does a unique hashing for all worlds that are equal to each other regarding their attributes,
        needed for elimation of doubles in the set of possible worlds
        """
        return hash((str(self.on_table), str(self.player1_hand), str(self.player2_hand)))

    def __eq__(self, other):
        """
        compares two world objects in regards to their attributes,
        two worlds are equal if the same cards are in player1's hand, player2's hand and
        on the on_table in both worlds
        """
        if not isinstance(other, type(self)): return NotImplemented
        return self.on_table == other.on_table and self.player1_hand == other.player1_hand and self.player2_hand == other.player2_hand

class Player:
    """
    a representation of a player in the game

    attriutes:
    - name: player 1 or player 2
    - possible_worlds: a set of unique worlds that the player considers possible from his point of view
    """

    def __init__(self, name):
        self.name = name
        self.possible_worlds = set()

    def create_possible_worlds(self):
        copy_real_world = cp.deepcopy(real_world)
        self.possible_worlds.add(copy_real_world)
        copy_pile = original_pile
        if self.name is "player1":
            copy_pile.remove(real_world.player2_hand[0])
        if self.name is "player2":
            copy_pile.remove(real_world.player1_hand[0])

        for i, card in enumerate(copy_pile):
            world = World()
            if self.name is "player1":
                world.player2_hand.append(real_world.player2_hand[0])
                world.player1_hand.append(card)
            if self.name is "player2":
                world.player1_hand.append(real_world.player1_hand[0])
                world.player2_hand.append(card)

            self.possible_worlds.add(world)

def start_game():
    """
    a game of Hanabi is started by having all player draw 1 card
    """
    draw_card(player1)
    draw_card(player2)

def draw_card(player):
    """
    a random card is drawn from the pile, either to player 1
    or player 2
    """
    random_index = rd.randint(0,len(pile) - 1)

    if player.name is "player1":
        real_world.player1_hand.append(pile.pop(random_index))

    if player.name is "player2":
        real_world.player2_hand.append(pile.pop(random_index))

def play_card(player):

    if player.name is "player1":
        played_card = real_world.player1_hand.pop()
    if player.name is "player2":
        played_card = real_world.player2_hand.pop()

    if played_card == 1:
        real_world.on_table.append(played_card)
    else:
        real_world.blitz += 1

    for w in player1.possible_worlds:
        w.on_table = real_world.on_table
        if player.name is "player1":
            w.player1_hand.pop()
        if player.name is "player2":
            w.player2_hand.pop()
        w.blitz = real_world.blitz

    for w in player2.possible_worlds:
        w.on_table = real_world.on_table
        if player.name is "player2":
            w.player2_hand.pop()
        if player.name is "player1":
            w.player1_hand.pop()
        w.blitz = real_world.blitz

def print_game_status():

    print("------------------")
    print("[real world]", real_world)
    print("------------------")

    print("[possible worlds for player 1]")
    for w in player1.possible_worlds:
        print(w)

    print("\n[possible worlds for player 2]")
    for w in player2.possible_worlds:
        print(w)

""""
One simulated / scripted game
"""

# setting up the game, 1 colour, 1-3, 1 are double
pile = [1,1,2,3]
original_pile = [1,1,2,3]
real_world = World()
player1 = Player("player1")
player2 = Player("player2")

start_game()
player1.create_possible_worlds()
player2.create_possible_worlds()

print("\n------------------")
print("START OF THE GAME")
print("2 players, 4 cards, 1x2, 1x3, 1x1")
print("------------------")
print("ROUND 0: after drawing cards")

print_game_status()

play_card(player1)

print("\n------------------")
print("ROUND 1: player 1 plays his card")
print_game_status()
