"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    goals = generate_goals(num_human + num_random + len(smart_players))
    res = []
    current_id = 0
    for player in range(num_human):
        res.append(HumanPlayer(current_id, goals[current_id]))
        current_id += 1
    for player in range(num_random):
        res.append(RandomPlayer(current_id, goals[current_id]))
        current_id += 1
    for player in smart_players:
        res.append(SmartPlayer(current_id, goals[current_id],
                               player))
        current_id += 1
    
    return res
    

def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    pos = block.position
    if  location[0] in range(pos[0], pos[0] + block.size) and\
        location[1] in range(pos[1], pos[1] + block.size):
        if block.level > level:
            return None
        
        if block.children == []:
            return block

        for child in block.children:
            selected = _get_block(child, location, level)
            if selected is not None:
                return selected
        return block
    return None



class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError

    def _check_move(self, block: Optional[Block], 
                    action: tuple[str, int]) -> bool:
        """Return true iff the given <action> is valid on the given <block>.
        Does not mutate <block>.

        Precondition: 
        <action> is given with possible movement string and integer.
        """
        if block is None:
            return False

        test_block = block.create_copy()
        valid = False
        if action in [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE]:
            valid = test_block.rotate(action[1])
        elif action in [SWAP_HORIZONTAL, SWAP_VERTICAL]:
            valid = test_block.swap(action[1])
        elif action == SMASH:
            valid = test_block.smash()
        elif action == PAINT:
            valid = test_block.paint(self.goal.colour)
        elif action == COMBINE:
            valid = test_block.combine()
        return valid
    
    def _generate_random_valid_move(self, board: Block)\
        -> Tuple[Tuple[str, Optional[int]], Tuple[int, int], int]:
        """Return a tuple containing the valid action, a tuple containing the 
        coordinates of the selected, and a tuple containing the level of the
        selection of the block.
        """
        valid = False
        action = None
        location = None
        level = 0
        while not valid:
            level = random.randint(board.level, board.max_depth)
            action = random.choice([ROTATE_CLOCKWISE,
                                    ROTATE_COUNTER_CLOCKWISE, 
                                    SWAP_HORIZONTAL, 
                                    SWAP_VERTICAL, 
                                    SMASH, 
                                    PAINT, 
                                    COMBINE])

            location = (random.randint(0, board.size),
                        random.randint(0, board.size))
            selected = _get_block(board, location, level)
            valid = self._check_move(selected, action)
        return (action, location, level)

def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    """Return a tuple containing the action string, the optional associated 
    integer parameter, and the block that the action is to be performed on.

    Uses the <action> for the first two items in the tuple, and <block> for the
    third. 
    """
    return action[0], action[1], block



class HumanPlayer(Player):
    """A human player.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0

    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """A player that chooses moves completely randomly.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    # === Private Attributes ===
    # _proceed:
    #     True when the player should make a move, False when the player should
    #     wait.
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initializes the random player with a <player_id> and a <goal>
        the former being used to identify and the latter 
        being used as this player's objective.
        """
        super().__init__(player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block currently selected by the player.
        If this does not apply for this player, return None.
        """
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player in accordance to the given events.
        The random player should only run it's course when the user
        clicks.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove
        generated = self._generate_random_valid_move(board)
        action = generated[0]
        selected = _get_block(board, generated[1], generated[2])
        self._proceed = False  # Must set to False before returning!
        return _create_move(action, selected)


class SmartPlayer(Player):
    """A player that looks at a variety of moves and chooses the best one.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    # === Private Attributes ===
    # _proceed:
    #    True when the player should make a move, False when the player should
    #    wait.
    # _difficulty:
    #    The number of valid moves this player checks.
    # == Representation Invariants concerning the private attributes ==
    #   _difficulty > 0
    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        """Initializes the smart player with a <player_id> and a <goal>
        the former being used to identify and the latter being used as this 
        player's objective. The <difficulty> sets how many moves it will check
        before choosing the one that yields the greatest score. It does not 
        take into account the penalty that may apply to an action.
        """
        super().__init__(player_id, goal)
        self._proceed = False
        self._difficulty = difficulty

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the selected block by the user. In this case,
        the smart player does not query the user for a selection,
        and therefore, returns None.
        """
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Update the this player in accordance to changes in game events.
        This smart player should play it's move after the player clicks.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        potential_moves = []

        while len(potential_moves) < self._difficulty:
            test_board = board.create_copy()
            generated = self._generate_random_valid_move(test_board)
            test_board_block = _get_block(test_board, generated[1], 
                                          generated[2])
            current_action = generated[0]
            if current_action in [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE]:
                test_board_block.rotate(current_action[1])
            elif current_action in [SWAP_HORIZONTAL, SWAP_VERTICAL]:
                test_board_block.swap(current_action[1])
            elif current_action == SMASH:
                test_board_block.smash()
            elif current_action == PAINT:
                test_board_block.paint(self.goal.colour)
            elif current_action == COMBINE:
                test_board_block.combine()
            
            score = self.goal.score(test_board)
            move = _create_move(current_action,
                                _get_block(board, generated[1], generated[2]))
            potential_moves.append((move, score))
        
        greatest = self.goal.score(board)
        greatest_move = _create_move(PASS, board)
        for move_and_score in potential_moves:
            if move_and_score[1] > greatest:
                greatest = move_and_score[1]
                greatest_move = move_and_score[0]

        self._proceed = False  # Must set to False before returning!
        return greatest_move

if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
