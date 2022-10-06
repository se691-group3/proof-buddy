from django.test import Client, TestCase
from django.urls.base import reverse
from pytz import timezone
import pytz
from proofchecker.models import Assignment, Course, Instructor, Problem, Student, User, Proof, ProofLine
from datetime import datetime

class AllAssignmentsViewTest(TestCase):

    def setUp(self):
        # Create two users (one instructor, one student)
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True', is_instructor="True")
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_active='True', is_student="True")
        test_instructor = Instructor.objects.create(user=test_user1)
        test_student = Student.objects.create(user=test_user2)

        test_instructor.save()
        test_student.save()
        test_user1.save()
        test_user2.save()

    def test_logged_in_instructor_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('all_assignments'))
        self.assertTemplateUsed(response, 'assignments/instructor_assignments.html')
        self.assertEqual(response.status_code, 200)

    def test_logged_in_student_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD', is_active='True')
        response = self.client.get(reverse('all_assignments'))
        self.assertTemplateUsed(response, 'assignments/student_assignments.html')
        self.assertEqual(response.status_code, 200)

class CreateAssignmentViewTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True', is_instructor="True")
        test_instructor = Instructor.objects.create(user=test_user1)
        test_instructor.save()
        test_user1.save()

    def test_logged_in_instructor_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('add_assignment'))
        self.assertTemplateUsed(response, 'assignments/add_assignment.html')
        self.assertEqual(response.status_code, 200)


class AssignmentDetailsViewTest(TestCase):

    def setUp(self):
        # Create two users (one instructor, one student)
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True', is_instructor="True")
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_active='True', is_student="True")
        test_instructor = Instructor.objects.create(user=test_user1)
        test_student = Student.objects.create(user=test_user2)

        test_instructor.save()
        test_student.save()
        test_user1.save()
        test_user2.save()

        # Create a proof
        test_proof = Proof.objects.create(
            premises = 'A∧B',
            conclusion = 'A',
            created_by = test_user1
        )
        test_proof.save()

        # Create two lines for the proof
        test_line_1 = ProofLine.objects.create(
            line_no = 1,
            formula = 'A∧B',
            rule = 'Premise',
            proof = test_proof
        )
        test_line_2 = ProofLine.objects.create(
            line_no = 2,
            formula = 'A',
            rule = '∧E 1',
            proof = test_proof
        )
        test_line_1.save()
        test_line_2.save()

        # Create a problem
        test_problem1 = Problem.objects.create(
            question = 'Test Question',
            point = 10,
            target_steps = 10,
            proof = test_proof,
        )

        # Create a course
        test_course = Course.objects.create(
            title = "Test Course",
            term = "Fall 2022",
            section = "101",
            instructor = test_instructor,
        )
        test_course.save()

        # Create an assignment
        d = datetime(2025, 1, 1, tzinfo=pytz.UTC)

        test_assignment = Assignment.objects.create(
            title="Test Assignment",
            due_by=d,
            course=test_course,
        )
        test_assignment.problems.set([test_problem1])
        test_assignment.save()

    def test_logged_in_instructor_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('assignment_details', args=[1]))
        self.assertTemplateUsed(response, 'assignments/assignment_details.html')
        self.assertEqual(response.status_code, 200)

    def test_logged_in_student_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD', is_active='True')
        response = self.client.get(reverse('assignment_details', args=[1]))
        self.assertTemplateUsed(response, 'assignments/assignment_details.html')
        self.assertEqual(response.status_code, 200)


class ProblemSolutionViewTest(TestCase):

    def setUp(self):
        # Create two users (one instructor, one student)
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True', is_instructor="True")
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_active='True', is_student="True")
        test_instructor = Instructor.objects.create(user=test_user1)
        test_student = Student.objects.create(user=test_user2)

        test_instructor.save()
        test_student.save()
        test_user1.save()
        test_user2.save()

        # Create a proof
        test_proof = Proof.objects.create(
            premises = 'A∧B',
            conclusion = 'A',
            created_by = test_user1
        )
        test_proof.save()

        # Create two lines for the proof
        test_line_1 = ProofLine.objects.create(
            line_no = 1,
            formula = 'A∧B',
            rule = 'Premise',
            proof = test_proof
        )
        test_line_2 = ProofLine.objects.create(
            line_no = 2,
            formula = 'A',
            rule = '∧E 1',
            proof = test_proof
        )
        test_line_1.save()
        test_line_2.save()

        # Create a problem
        test_problem = Problem.objects.create(
            question = 'Test Question',
            point = 10,
            target_steps = 10,
            proof = test_proof,
        )
        test_problem.save()

        # Create a course
        test_course = Course.objects.create(
            title = "Test Course",
            term = "Fall 2022",
            section = "101",
            instructor = test_instructor,
        )
        test_course.save()

        # Create an assignment
        d = datetime(2025, 1, 1, tzinfo=pytz.UTC)

        test_assignment = Assignment.objects.create(
            title="Test Assignment",
            due_by=d,
            course=test_course,
        )
        test_assignment.problems.set([test_problem])
        test_assignment.save()