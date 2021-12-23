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
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    
    num = random.randint(0, 1)

    res = []
    useable_colours = COLOUR_LIST.copy()
    for _ in range(num_goals):
        color = random.choice(useable_colours)
        if num == 0:
            res.append(BlobGoal(color))
        else:
            res.append(PerimeterGoal(color))
        useable_colours.remove(color)

    return res


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    
    res = []
    if block.children == []:
        potential_units = 2 ** (block.max_depth - block.level)
        for i in range(potential_units):
            res.append([])
            for _ in range(potential_units):
                res[i].append(block.colour)
    else:
        res.extend(_flatten(block.children[1]))
        res.extend(_flatten(block.children[0]))
        
        bottom_left = _flatten(block.children[2])
        for col in range(len(bottom_left)):
            res[col].extend(bottom_left[col])
        
        bottom_right = _flatten(block.children[3])
        for col in range(len(bottom_right)):
            res[len(bottom_left) + col].extend(bottom_right[col])
    return res

class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """

    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A goal based on the amount of units of color on perimeter.

    === Attributes ===
    colour:
        This goal's color to be placed on perimeter units.
    """

    def score(self, board: Block) -> int:
        """Return an integer score calculated from the amount of units touching
        the edge of the <board>. The amount of units is the score. Each corner
        unit is worth two points instead of one normally.
        """
        flattened = _flatten(board)
        score = 0
        edge_index = len(flattened) - 1

        for unit in range(edge_index + 1):
            if flattened[unit][0] == self.colour:
                score += 1
            if flattened[unit][edge_index] == self.colour:
                score += 1
            if flattened[0][unit] == self.colour:
                score += 1
            if flattened[edge_index][unit] == self.colour:
                score += 1
                
        return score

    def description(self) -> str:
        """Return a string describing this perimeter goal. 
        Shows up at the bottom right of the screen.
        """
        return 'Make as much {} units touch the edge as possible.'\
            .format(colour_name(self.colour))


class BlobGoal(Goal):
    """Goal based on the amount of a colour is adjacent to 
    each other to form a blob.

    === Attributes ===
    colour:
        The colour that is supposed to be clustered together.
    """
    def score(self, board: Block) -> int:
        """Return an integer score based on the largest amount of units in the 
        given <board> that are the same colour as this goal's colour and are 
        adjacent to each other forming the group. The amount of units in this
        group is the score. 
        """
        flattened = _flatten(board)
        board_size = len(flattened)
        visited = []
        for col in range(board_size):
            visited.append([])
            for _ in range(board_size):
                visited[col].append(-1)

        greatest_blob = 0
        for x in range(board_size):
            for y in range(board_size):
                blob_size = \
                    self._undiscovered_blob_size((x, y), flattened, visited)
                if blob_size > greatest_blob:
                    greatest_blob = blob_size
        return greatest_blob

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        current_color = None
        current_visit = None
        if not pos[0] in range(len(board)) or not pos[1] in range(len(board)):
            return 0

        current_color = board[pos[0]][pos[1]]
        current_visit = visited[pos[0]][pos[1]]
        
        if current_visit != -1:
            return 0

        
        if current_color != self.colour:
            visited[pos[0]][pos[1]] = 0
            return 0
        else:
            visited[pos[0]][pos[1]] = 1
            blob_size = 1 + self._undiscovered_blob_size((pos[0] + 1, pos[1]),
                                                         board, visited) + \
                            self._undiscovered_blob_size((pos[0] - 1, pos[1]),
                                                         board, visited) + \
                            self._undiscovered_blob_size((pos[0], pos[1] + 1),
                                                         board, visited) + \
                            self._undiscovered_blob_size((pos[0], pos[1] - 1),
                                                         board, visited)
            return blob_size


    def description(self) -> str:
        """Return a string describing the blob goal. 
        Shows up at the bottom right of the screen.
        """
        return "Create the biggest blob of {} units."\
            .format(colour_name(self.colour))


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
