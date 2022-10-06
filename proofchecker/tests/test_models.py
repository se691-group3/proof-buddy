from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from ..models import Assignment, Course, Instructor, Proof, User, validate_formula, validate_line_no

class ValidationMethodsTest(TestCase):
    def test_validate_line_no(self):
        self.assertRaises(ValidationError, validate_line_no, '1.a')
        self.assertRaisesMessage(ValidationError, "1.a is not a valid line number", validate_line_no, value='1.a')

    def test_validate_formula(self):
        self.assertRaises(ValidationError, validate_formula, 'A∧')
        self.assertRaisesMessage(ValidationError, "A∧ is not a valid expression", validate_formula, value='A∧')


class ProofModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        user = User()
        user.save()

        Proof.objects.create(
            premises = 'A∧B',
            conclusion = 'A',
            created_by = user
        )

    def test_get_absolute_url(self):
        proof = Proof.objects.get(id=1)
        self.assertEqual(proof.get_absolute_url(), "/proofs")

class AssignmentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        user = User()
        user.save()
        instructor = Instructor(user_id = 1)
        instructor.save()

        course = Course(
            title = "Test Course",
            term = "Fall 2021",
            section = "001",
            instructor = instructor
        )
        course.save()

        Assignment.objects.create(
            title = "First Assignment",
            created_by = instructor,
            created_on = timezone.now(),
            due_by = timezone.now() + timedelta(days=7),
            course = course
        )

    def test_assignment_to_string(self):
        assignment = Assignment.objects.get(pk=1)
        self.assertEqual(str(assignment), "First Assignment")


    def test_get_absolute_url(self):
        assignment = Assignment.objects.get(id=1)
        self.assertEqual(assignment.get_absolute_url(), "/assignments")