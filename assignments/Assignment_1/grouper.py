"""CSC148 Assignment 1

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Misha Schwartz, Mario Badr, Christine Murad, Diane Horton, Sophia Huynh
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) 2020 Misha Schwartz, Mario Badr, Christine Murad, Diane Horton,
Sophia Huynh and Jaisie Sin

=== Module Description ===

This file contains classes that define different algorithms for grouping
students according to chosen criteria and the group members' answers to survey
questions. This file also contain a classe that describes a group of students as
well as a grouping (a group of groups).
"""
from __future__ import annotations
import random
from typing import TYPE_CHECKING, List, Any
from course import sort_students
if TYPE_CHECKING:
    from survey import Survey
    from course import Course, Student


def slice_list(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Return a list containing slices of <lst> in order. Each slice is a
    list of size <n> containing the next <n> elements in <lst>.

    The last slice may contain fewer than <n> elements in order to make sure
    that the returned list contains all elements in <lst>.

    === Precondition ===
    n <= len(lst)

    >>> slice_list([3, 4, 6, 2, 3], 2) == [[3, 4], [6, 2], [3]]
    True
    >>> slice_list(['a', 1, 6.0, False], 3) == [['a', 1, 6.0], [False]]
    True
    """
    s = []
    i = 0
    if n % len(lst) == 0:
        while i <= (len(lst) - 1):
            s += [lst[i: i + n]]
            i += n
        return s
    else:
        while i <= (len(lst) - 1 - n % len(lst)):
            s += [lst[i: i + n]]
            i += n
            while (len(lst) - 1 - n % len(lst)) < i <= (len(lst) - 1):
                s += [lst[i:]]
                i += n
        return s


def windows(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Return a list containing windows of <lst> in order. Each window is a list
    of size <n> containing the elements with index i through index i+<n> in the
    original list where i is the index of window in the returned list.

    === Precondition ===
    n <= len(lst)

    >>> windows([3, 4, 6, 2, 3], 2) == [[3, 4], [4, 6], [6, 2], [2, 3]]
    True
    >>> windows(['a', 1, 6.0, False], 3) == [['a', 1, 6.0], [1, 6.0, False]]
    True
    """
    out = []
    current = []
    
    pos = 0
    while pos < len(lst):
        if len(current) < n:
            current.append(lst[pos])
            pos += 1
        else:
            out.append(current)
            current = []
            pos -= n - 1
    out.append(current)
    current = []
    return out


class Grouper:
    """
    An abstract class representing a grouper used to create a grouping of
    students according to their answers to a survey.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def __init__(self, group_size: int) -> None:
        """
        Initialize a grouper that creates groups of size <group_size>

        === Precondition ===
        group_size > 1
        """
        self.group_size = group_size

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """ Return a grouping for all students in <course> using the questions
        in <survey> to create the grouping.
        """
        raise NotImplementedError


class AlphaGrouper(Grouper):
    """
    A grouper that groups students in a given course according to the
    alphabetical order of their names.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        The first group should contain the students in <course> whose names come
        first when sorted alphabetically, the second group should contain the
        next students in that order, etc.

        All groups in this grouping should have exactly self.group_size members
        except for the last group which may have fewer than self.group_size
        members if that is required to make sure all students in <course> are
        members of a group.

        Hint: the sort_students function might be useful
        """
        result = Grouping()
        students = list(course.get_students())
        students = sort_students(students, "name")
        groups_list = slice_list(students, self.group_size)

        for group_list in groups_list:
            result.add_group(Group(group_list))
        return result


class RandomGrouper(Grouper):
    """
    A grouper used to create a grouping of students by randomly assigning them
    to groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int


    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Students should be assigned to groups randomly.

        All groups in this grouping should have exactly self.group_size members
        except for one group which may have fewer than self.group_size
        members if that is required to make sure all students in <course> are
        members of a group.
        """
        students = list(course.get_students())
        groups = Grouping()
        current_group = []
        while len(students) > 0:
            if len(current_group) < self.group_size:
                selected = students[random.randint(0, len(students)) - 1]
                current_group.append(selected)
                students.remove(selected)
            else:
                groups.add_group(Group(current_group))
                current_group = []
        groups.add_group(Group(current_group))
        current_group = []
        return groups

class GreedyGrouper(Grouper):
    """
    A grouper used to create a grouping of students according to their
    answers to a survey. This grouper uses a greedy algorithm to create
    groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Starting with a tuple of all students in <course> obtained by calling
        the <course>.get_students() method, create groups of students using the
        following algorithm:

        1. select the first student in the tuple that hasn't already been put
           into a group and put this student in a new group.
        2. select the student in the tuple that hasn't already been put into a
           group that, if added to the new group, would increase the group's
           score the most (or reduce it the least), add that student to the new
           group.
        3. repeat step 2 until there are N students in the new group where N is
           equal to self.group_size.
        4. repeat steps 1-3 until all students have been placed in a group.

        In step 2 above, use the <survey>.score_students method to determine
        the score of each group of students.

        The final group created may have fewer than N members if that is
        required to make sure all students in <course> are members of a group.
        """
        students = list(course.get_students())
        groups = Grouping()
        group_list = []

        while len(students) > 0:
            if group_list == []:
                group_list.append(students[0])
                students.remove(students[0])
                self._move_best_results_for_group(group_list, students, survey)
            else:
                groups.add_group(Group(group_list))
                group_list = []
        groups.add_group(Group(group_list))
        group_list = []
        return groups

    def _move_best_results_for_group(self, group: List(Student), 
                                     students: List(Student),
                                     survey: Survey) -> None:
        """
        Moves the best student from the list of <students> to the <group> of
        students.

        The best student for the group is the one that raises the groups
        score the most calculated by <survey>.score_students().

        This method moves the student from <students> to <group>. 
        """
        if len(group) < self.group_size:
            highest_score = 0
            best_student = None
            for student in students:
                group.append(student)
                score = survey.score_students(group)
                if score > highest_score:
                    highest_score = score
                    best_student = student
                group.remove(student)

            group.append(best_student)
            students.remove(best_student)
class WindowGrouper(Grouper):
    """
    A grouper used to create a grouping of students according to their
    answers to a survey. This grouper uses a window search algorithm to create
    groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Starting with a tuple of all students in <course> obtained by calling
        the <course>.get_students() method, create groups of students using the
        following algorithm:

        1. Get the windows of the list of students who have not already been
           put in a group.
        2. For each window in order, calculate the current window's score as
           well as the score of the next window in the list. If the current
           window's score is greater than or equal to the next window's score,
           make a group out of the students in current window and start again at
           step 1. If the current window is the last window, compare it to the
           first window instead.

        In step 2 above, use the <survey>.score_students to determine the score
        of each window (list of students).

        In step 1 and 2 above, use the windows function to get the windows of
        the list of students.

        If there are any remaining students who have not been put in a group
        after repeating steps 1 and 2 above, put the remaining students into a
        new group.
        """
        students = list(course.get_students())
        grouping = Grouping()

        while len(students) > 0:
            window_groups = windows(students, self.group_size)
            highscore = 0
            best_win_group = None
            for window in window_groups:
                score = survey.score_students(window)
                if score > highscore:
                    best_win_group = window
                    highscore = score
            grouping.add_group(Group(best_win_group))
            for student in best_win_group:
                students.remove(student)
        return grouping


class Group:
    """
    A group of one or more students

    === Private Attributes ===
    _members: a list of unique students in this group

    === Representation Invariants ===
    No two students in _members have the same id
    """

    _members: List[Student]

    def __init__(self, members: List[Student]) -> None:
        """ Initialize a group with members <members> """
        self._members = members

    def __len__(self) -> int:
        """ Return the number of members in this group """
        return len(self._members)

    def __contains__(self, member: Student) -> bool:
        """
        Return True iff this group contains a member with the same id
        as <member>.
        """
        return member in self._members

    def __str__(self) -> str:
        """
        Return a string containing the names of all members in this group
        on a single line.

        You can choose the precise format of this string.
        """
        res = "Members:"
        for m in self._members:
            res += " " + str(m)
        return res

    def get_members(self) -> List[Student]:
        """ Return a list of members in this group. This list should be a
        shallow copy of the self._members attribute.
        """
        return self._members.copy()


class Grouping:
    """
    A collection of groups

    === Private Attributes ===
    _groups: a list of Groups
    _students_ids: a list of student ids that are members of this grouping.

    === Representation Invariants ===
    No group in _groups contains zero members
    No student appears in more than one group in _groups
    """

    _groups: List[Group]
    _students_ids: List[int]
    def __init__(self) -> None:
        """ Initialize a Grouping that contains zero groups """
        self._groups = []
        self._students_ids = []

    def __len__(self) -> int:
        """ Return the number of groups in this grouping """
        return len(self._groups)

    def __str__(self) -> str:
        """
        Return a multi-line string that includes the names of all of the members
        of all of the groups in <self>. Each line should contain the names
        of members for a single group.

        You can choose the precise format of this string.
        """
        final = ""
        for group in self._groups:
            final += str(group) + "\n"
        final = final.strip()
        return final

    def add_group(self, group: Group) -> bool:
        """
        Add <group> to this grouping and return True.

        Iff adding <group> to this grouping would violate a representation
        invariant don't add it and return False instead.
        """
        if len(group) == 0:
            return False
        
        students = group.get_members()
        for student in students:
            if student.id in self._students_ids:
                return False
            self._students_ids.append(student.id)
        self._groups.append(group)
        return True

    def get_groups(self) -> List[Group]:
        """ Return a list of all groups in this grouping. 
        This list should be a shallow copy of the self._groups 
        attribute.
        """
        return self._groups.copy()


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={'extra-imports': ['typing',
                                                  'random',
                                                  'survey',
                                                  'course']})
