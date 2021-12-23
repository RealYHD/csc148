import course
import criterion
import grouper
import survey
import pytest
from typing import List

@pytest.fixture
def basic_course() -> course.Course:
    return course.Course("Basic")

@pytest.fixture
def generic_student() -> course.Student:
    return course.Student(0, "John")

@pytest.fixture
def students() -> List[course.Student]:
    return [course.Student(1, 'Jason'),
            course.Student(2, 'Barry'),
            course.Student(3, 'John'),
            course.Student(4, 'Henry'),
            course.Student(5, 'Alice'),
            course.Student(6, 'Zack'),
            course.Student(7, 'Alfred')]

@pytest.fixture
def alphabetical_students_grouping(basic_survey,
                                   basic_course,
                                   students_with_answers_to_generic_questions
                                   ) -> grouper.Grouping:
    basic_course.enroll_students(students_with_answers_to_generic_questions)
    grpr = grouper.AlphaGrouper(2)
    return grpr.make_grouping(basic_course, survey)

@pytest.fixture
def less_students() -> List[course.Student]:
    return [course.Student(1, 'Jason'),
            course.Student(2, 'Bob'),
            course.Student(3, 'Thomas'),
            course.Student(4, 'Barry')]

@pytest.fixture
def generic_questions() -> List[survey.Question]:
    return [survey.YesNoQuestion(1, "Yes or No"),
            survey.CheckboxQuestion(2, "A, B, or C", ["A", "B", "C"]),
            survey.MultipleChoiceQuestion(3, "A, B, or C", ["A", "B", "C"]),
            survey.NumericQuestion(4, "Number between 1 and 10", 1, 10)]

@pytest.fixture
def course_with_less_students(basic_course, less_students) -> course.Course:
    basic_course.enroll_students(less_students)
    return basic_course

@pytest.fixture
def students_with_answers_to_generic_questions(generic_questions, less_students) -> List[course.Student]:
    less_students[0].set_answer(generic_questions[0], survey.Answer(False))
    less_students[0].set_answer(generic_questions[1], survey.Answer(["A", "B"]))
    less_students[0].set_answer(generic_questions[2], survey.Answer("A"))
    less_students[0].set_answer(generic_questions[3], survey.Answer(1))
    less_students[1].set_answer(generic_questions[0], survey.Answer(True))
    less_students[1].set_answer(generic_questions[1], survey.Answer(["A", "B", "C"]))
    less_students[1].set_answer(generic_questions[2], survey.Answer("C"))
    less_students[1].set_answer(generic_questions[3], survey.Answer(10))
    less_students[2].set_answer(generic_questions[0], survey.Answer(True))
    less_students[2].set_answer(generic_questions[1], survey.Answer(["A", "B", "C"]))
    less_students[2].set_answer(generic_questions[2], survey.Answer("C"))
    less_students[2].set_answer(generic_questions[3], survey.Answer(10))
    less_students[3].set_answer(generic_questions[0], survey.Answer(True))
    less_students[3].set_answer(generic_questions[1], survey.Answer(["A", "B", "C"]))
    less_students[3].set_answer(generic_questions[2], survey.Answer("C"))
    less_students[3].set_answer(generic_questions[3], survey.Answer(10))
    return less_students

@pytest.fixture
def generic_criteria() -> List[criterion.Criterion]:
    return [criterion.HomogeneousCriterion(),
            criterion.HeterogeneousCriterion(),
            criterion.LonelyMemberCriterion()]

@pytest.fixture
def generic_weights() -> List[int]:
    return [1, 3, 5]

@pytest.fixture
def basic_survey(generic_questions) -> survey.Survey:
    s = survey.Survey(generic_questions)
    return s

class TestCourses:

    def test_enroll_same_id(self, basic_course, generic_student) -> None:
        c = basic_course
        student = generic_student
        student1 = course.Student(0, "Jacy")
        c.enroll_students([student, student1])
        assert len(c.get_students()) == 0

    def test_enroll_empty_name(self, basic_course) -> None:
        basic_course.enroll_students([course.Student(1, None)])
        assert len(basic_course.get_students()) == 0

    def test_enroll_many(self, basic_course, students) -> None:
        basic_course.enroll_students(students)
        assert basic_course.get_students() == tuple(students)

    def test_enroll_separate_same_id(self, 
                                     basic_course,
                                     generic_student) -> None:
        basic_course.enroll_students([generic_student])
        student1 = course.Student(0, "Jacy")
        basic_course.enroll_students([student1])
        assert basic_course.get_students() == tuple([generic_student])

    def test_all_answered(self,
                          students_with_answers_to_generic_questions,
                          basic_course,
                          basic_survey) -> None:
        basic_course.enroll_students(students_with_answers_to_generic_questions)
        assert basic_course.all_answered(basic_survey)
    
    def test_get_all_students_sorted(self,
                                     basic_course,
                                     less_students,
                                     generic_student) -> None:
        less_students.append(generic_student)
        basic_course.enroll_students(less_students)
        correct = [generic_student]
        correct.extend(less_students)
        del correct[len(correct) - 1]
        assert basic_course.get_students() == tuple(correct)

class TestStudent:
    def test_has_answer(self, students_with_answers_to_generic_questions,
                        generic_questions) -> None:
        assert students_with_answers_to_generic_questions[0].has_answer\
            (generic_questions[0])
    
    def test_has_answer(self, generic_student, generic_questions) -> None:
        generic_student.set_answer(generic_questions[0], survey.Answer("Apple"))
        assert generic_student.has_answer(generic_questions[0]) == False

    def test_set_answer_and_get_answer(self, generic_student, generic_questions) -> None:
        ans = [survey.Answer(True),
               survey.Answer(["B"]),
               survey.Answer("A"),
               survey.Answer("4")]
        generic_student.set_answer(generic_questions[0], ans[0])
        generic_student.set_answer(generic_questions[1], ans[1])
        generic_student.set_answer(generic_questions[2], ans[2])
        generic_student.set_answer(generic_questions[3], ans[3])
        
        assert generic_student.get_answer(generic_questions[0]) == ans[0]
        assert generic_student.get_answer(generic_questions[1]) == ans[1]
        assert generic_student.get_answer(generic_questions[2]) == ans[2]
        assert generic_student.get_answer(generic_questions[3]) == ans[3]

    def test_set_answer(self, generic_student, generic_questions) -> None:
        ans = [survey.Answer(True),
               survey.Answer(["B"]),
               survey.Answer(["C"])]
        generic_student.set_answer(generic_questions[0], ans[0])
        generic_student.set_answer(generic_questions[1], ans[1])
        assert generic_student.get_answer(generic_questions[0]) == ans[0]
        generic_student.set_answer(generic_questions[1], ans[2])
        assert generic_student.get_answer(generic_questions[1]) == ans[2]

    def test__exists_answer(self, generic_student, generic_questions) -> None:
        generic_student.set_answer(generic_questions[0], survey.Answer(True))
        assert generic_student._exists_answer(generic_questions[0])

    def test__exists_answer_invalid(self, generic_student, generic_questions) -> None:
        generic_student.set_answer(generic_questions[0], survey.Answer("A"))
        assert generic_student._exists_answer(generic_questions[0])

class TestMultipleChoiceQuestion:
    def test_validate_answer_valid(self) -> None:
        mc_question = survey.MultipleChoiceQuestion(1, "Pick one.", ["A", "B", "C"])
        assert mc_question.validate_answer(survey.Answer("A"))

    def test_validate_answer_invalid(self) -> None:
        mc_question = survey.MultipleChoiceQuestion(1, "Pick one.", ["A", "B", "C"])
        assert mc_question.validate_answer(survey.Answer("E")) == False

    def test_get_similarity_full(self) -> None:
        mc_question = survey.MultipleChoiceQuestion(1, "Same option?", ["A", "B", "C"])
        assert mc_question.get_similarity(survey.Answer("A"), survey.Answer("A")) == 1.0
    
    def test_get_similarity_none(self) -> None:
        mc_question = survey.MultipleChoiceQuestion(1, "Same option?", ["A", "B", "C"])
        assert mc_question.get_similarity(survey.Answer("C"), survey.Answer("A")) == 0


class TestNumericQuestion:
    def test_validate_answer_valid(self) -> None:
        mc_question = survey.NumericQuestion(1, "Pick val.", 1, 30)
        assert mc_question.validate_answer(survey.Answer(3))

    def test_validate_answer_invalid(self) -> None:
        mc_question = survey.NumericQuestion(1, "Pick val.", 1, 30)
        assert mc_question.validate_answer(survey.Answer("E")) == False

    def test_get_similarity_full(self) -> None:
        mc_question = survey.NumericQuestion(1, "Pick val.", 1, 30)
        assert mc_question.get_similarity(survey.Answer(3), survey.Answer(3)) == 1.0
    
    def test_get_similarity_in_between(self) -> None:
        mc_question = survey.NumericQuestion(1, "Pick val.", 1, 30)
        assert round(mc_question.get_similarity\
            (survey.Answer(1), survey.Answer(15)), 1) == 1/2 

    def test_get_similarity_none(self) -> None:
        mc_question = survey.NumericQuestion(1, "Pick val.", 1, 30)
        assert mc_question.get_similarity(survey.Answer(1), survey.Answer(30)) == 0.0

class TestYesNoQuestion:
    def test_validate_answer_valid(self) -> None:
        mc_question = survey.YesNoQuestion(1, "Yes or No?")
        assert mc_question.validate_answer(survey.Answer(True))

    def test_validate_answer_invalid(self) -> None:
        mc_question = survey.YesNoQuestion(1, "Yes or No?")
        assert mc_question.validate_answer(survey.Answer("E")) == False

    def test_get_similarity_full(self) -> None:
        mc_question = survey.YesNoQuestion(1, "Yes or No?")
        assert mc_question.get_similarity(survey.Answer(True), survey.Answer(True)) == 1.0
    
    def test_get_similarity_none(self) -> None:
        mc_question = survey.YesNoQuestion(1, "Yes or No?")
        assert mc_question.get_similarity(survey.Answer(False), survey.Answer(True)) == 0.0

class TestCheckboxQuestion:
    def test_validate_answer_valid(self) -> None:
        mc_question = survey.CheckboxQuestion(1, "Pick some", ["A", "B", "C"])
        assert mc_question.validate_answer(survey.Answer(["A", "C"]))

    def test_validate_answer_valid(self) -> None:
        mc_question = survey.CheckboxQuestion(1, "Pick some", ["A", "B", "C"])
        assert mc_question.validate_answer(survey.Answer("Pears")) == False

    def test_validate_answer_invalid_not_contained(self) -> None:
        mc_question = survey.CheckboxQuestion(1, "Pick some", ["A", "B", "C"])
        assert mc_question.validate_answer(survey.Answer("E")) == False

    def test_validate_answer_invalid_empty(self) -> None:
        mc_question = survey.CheckboxQuestion(1, "Pick some", ["A", "B", "C"])
        assert mc_question.validate_answer(survey.Answer([])) == False

    def test_get_similarity_full(self) -> None:
        mc_question = survey.CheckboxQuestion(1, "Pick some", ["A", "B", "C"])
        assert mc_question.get_similarity(survey.Answer(["A"]), survey.Answer(["A"])) == 1.0

    def test_get_similarity_full(self) -> None:
        mc_question = survey.CheckboxQuestion(1, "Pick some", ["A", "B", "C", "D"])
        assert mc_question.get_similarity(survey.Answer(["A", "B", "C"]), survey.Answer(["B", "C", "D"])) == 0.5
        
    def test_get_similarity_none(self) -> None:
        mc_question = survey.CheckboxQuestion(1, "Pick some", ["A", "B", "C"])
        assert mc_question.get_similarity(survey.Answer(["A"]), survey.Answer(["C"])) == 0.0

class TestAnswer:
    def test_is_valid(self) -> None:
        mc_question = survey.CheckboxQuestion(1, "Pick some", ["A", "B", "C"])
        answer = survey.Answer(["C"])
        assert answer.is_valid(mc_question)

class TestSurvey:
    def test_get_questions(self, basic_survey, generic_questions) -> None:
        assert basic_survey.get_questions() == generic_questions
    
    def test_set_criterion(self, basic_survey,
                                         generic_questions,
                                         generic_criteria) -> None:
        basic_survey.set_criterion(generic_criteria[0], generic_questions[1])
        assert basic_survey._criteria[generic_questions[1].id] == generic_criteria[0]

    def test_get_criterion(self, basic_survey,
                                         generic_questions,
                                         generic_criteria) -> None:
        basic_survey._criteria = {generic_questions[0].id: generic_criteria[0] }
        assert basic_survey._get_criterion(generic_questions[0]) == generic_criteria[0]

    def test_set_weight(self, basic_survey,
                                         generic_questions,
                                         generic_weights) -> None:
        basic_survey.set_weight(generic_weights[0], generic_questions[1])
        assert basic_survey._weights[generic_questions[1].id] == generic_weights[0]

    def test_get_weight(self, basic_survey,
                                         generic_questions,
                                         generic_weights) -> None:
        basic_survey._weights = {generic_questions[0].id: generic_weights[0] }
        assert basic_survey._get_weight(generic_questions[0]) == generic_weights[0]
    
    def test_score_students(self, basic_survey,
                            students_with_answers_to_generic_questions) -> None:
        assert round(basic_survey.score_students\
        (students_with_answers_to_generic_questions), 1) == 0.6

    def test_score_grouping(self, basic_survey,
                            students_with_answers_to_generic_questions,
                            basic_course) -> None:
        basic_course.enroll_students(students_with_answers_to_generic_questions)
        grper = grouper.AlphaGrouper(2)
        grping = grper.make_grouping(basic_course, survey)
        assert basic_survey.score_students(grping.get_groups()[0].get_members()) == 1.0
        assert round(basic_survey.score_grouping(grping), 1) == 0.6


class TestGroup:
    def test_group___len__(self, less_students) -> None:
        """Test group class private methods"""
        grp = grouper.Group(less_students)
        assert len(grp) == 4

    def test_group___contains__(self, less_students) -> None:
        grp = grouper.Group(less_students)
        assert less_students[0] in grp

    def test_group___str__(self, less_students) -> None:
        grp = grouper.Group(less_students)

        contains = True
        str_ = str(grp)
        members = grp.get_members()
        for student in members:
            if not str(student) in str_:
                contains = False
                break
        assert contains
    def test_get_members(self, less_students) -> None:
        """Test get_numbers"""
        grp = grouper.Group(less_students)
        assert grp.get_members() == less_students

class TestGrouping:
    def test___len__(self, alphabetical_students_grouping) -> None:
        """Test group class private methods"""
        assert len(alphabetical_students_grouping) == 2

    def test_get_group(self, less_students) -> None:
        group1 = grouper.Group(less_students[0:2])
        group2 = grouper.Group(less_students[2:4])
        grpng = grouper.Grouping()
        grpng.add_group(group1)
        grpng.add_group(group2)
        assert grpng.get_groups() == [group1, group2] 

    def test___str__(self, alphabetical_students_grouping) -> None:
        agrp = alphabetical_students_grouping
        groups = agrp.get_groups()
        msg_correct = True
        lines = str(agrp).splitlines()
        for gid in range(len(groups)):
            students = groups[gid].get_members()
            for student in students:
                if not str(student) in lines[gid]:
                    contains = False
                    break
        assert msg_correct

class TestAlphaGrouper:
    def test_make_grouping(self, 
                           basic_survey, 
                           course_with_less_students, 
                           less_students) -> None:
        """Test AlphaGrouper.make_grouping"""
        agrouper = grouper.AlphaGrouper(2)
        groups = agrouper.make_grouping(course_with_less_students, basic_survey).get_groups()

        assert groups[0].get_members() == [less_students[3],
                                           less_students[1]]
        assert groups[1].get_members() == [less_students[0], 
                                           less_students[2]]

class TestRandomGrouper:
    def test_make_grouping(self, 
                           basic_survey, 
                           course_with_less_students, 
                           less_students) -> None:
        rgrouper = grouper.RandomGrouper(2)
        groups = rgrouper.make_grouping(course_with_less_students, basic_survey).get_groups()
        assert len(groups) == 2
        for group in groups:
            assert len(group) == 2
        
        exists = []
        for group in groups:
            students = group.get_members()
            for student in students:
                exists.append(student)
        for student in less_students:
            assert student in exists
        


#TODO Grouper test greedygrouper make_grouping
#TODO Grouper test windowgrouper make_grouping


class TestHomogeneousCriterion:
    def test_score_answers_homogeneous_criterion(self) -> None:
        """Test HomogeneousCriterion.score_answers"""
        q1 = survey.MultipleChoiceQuestion(1, "Favorite Colors", ['Red', 'Blue', 'Yellow'])
        a1 = survey.Answer(['Green'])
        a2 = survey.Answer(['Orange'])
        a3 = survey.Answer(['Grey'])
        a4 = survey.Answer(['Black'])
        answers = [a1, a2, a3, a4]
        hc = criterion.HomogeneousCriterion()
        with pytest.raises(criterion.InvalidAnswerError):
            hc.score_answers(q1, answers) 
    
  
class TestLonelyMemberCriterion:
    def test_score_answers_lonely_member_criterion(self) -> None:
        """Test LonelyMemberCriterion.score_answers"""
        q1 = survey.MultipleChoiceQuestion(1, "Favorite Colors", ['Red', 'Blue', 'Yellow'])
        a1 = survey.Answer(['Green'])
        a2 = survey.Answer(['Orange'])
        a3 = survey.Answer(['Grey'])
        a4 = survey.Answer(['Black'])
        answers = [a1, a2, a3, a4]
        hc = criterion.LonelyMemberCriterion()
        with pytest.raises(criterion.InvalidAnswerError):
            hc.score_answers(q1, answers) 
    
    
class TestHeterogeneousCriterion:
    def test_score_answers_heterogeneous_criterion(self) -> None:
        """Test HeterogeneousCriterion.score_answers"""
        q1 = survey.MultipleChoiceQuestion(1, "Favorite Colors", ['Red', 'Blue','Yellow'])
        a1 = survey.Answer('Green')
        a2 = survey.Answer('Orange')
        a3 = survey.Answer('Grey')
        a4 = survey.Answer('Black')
        answers = [a1, a2, a3, a4]
        hc = criterion.HeterogeneousCriterion()
        with pytest.raises(criterion.InvalidAnswerError):
            hc.score_answers(q1, answers)
  
    
    
def test_slice_lists() -> None:
    """Test slice_lists"""
    assert grouper.slice_list([3,4,5,6,7,8,9], 4) == [[3,4,5,6], [7, 8, 9]]

def test_windows() -> None:
    """Test windows"""
    assert grouper.windows([3,4,5,6,7,8,9], 4) == \
    [[3,4,5,6], [4,5,6,7], [5,6,7,8], [6,7,8,9]]
    
    
    

if __name__ == '__main__':
    pytest.main(['tests.py'])