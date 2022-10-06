from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from proofchecker.models import Course, Instructor, Problem, Proof, ProofLine, Student, User

class HomeViewTest(TestCase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proofchecker/home.html')

class ProofCheckerViewTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_active='True')

        test_user1.save()
        test_user2.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/proofs/checker/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('proof_checker'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('proof_checker'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proofchecker/proof_checker.html')

    def test_check_proof_submission(self):
        self.client = Client(enforce_csrf_checks=False)
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.post(reverse('proof_checker'), {
            'name': ['Proof'], 'rules': ['tfl_basic'], 'premises': ['A∧B'], 'conclusion': ['A'], 'form-TOTAL_FORMS': ['1'], 'form-INITIAL_FORMS': ['0'], 
            'form-MIN_NUM_FORMS': ['0'], 'form-MAX_NUM_FORMS': ['1000'], 'form-0-line_no': ['1'], 
            'form-0-formula': ['A∧B'], 'form-0-rule': ['Premise'], 'form-__prefix__-line_no': [''], 'form-__prefix__-formula': [''], 
            'form-__prefix__-rule': ['']})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proofchecker/proof_checker.html')

class ProofCreateViewTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_active='True')

        test_user1.save()
        test_user2.save()

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get('/proofs/new/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('add_proof'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('add_proof'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proofchecker/proof_add_edit.html')

    def test_check_proof_submission(self):
        self.client = Client(enforce_csrf_checks=False)
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.post(reverse('add_proof'), {
            'name': ['Proof'], 'rules': ['tfl_basic'], 'premises': ['A∧B'], 'conclusion': ['A'], 'proofline_set-TOTAL_FORMS': ['1'], 
            'proofline_set-INITIAL_FORMS': ['0'], 'proofline_set-MIN_NUM_FORMS': ['0'], 
            'proofline_set-MAX_NUM_FORMS': ['1000'], 'proofline_set-__prefix__-id': [''], 
            'proofline_set-__prefix__-ORDER': [''], 'proofline_set-__prefix__-line_no': [''], 
            'proofline_set-__prefix__-formula': [''], 'proofline_set-__prefix__-rule': [''], 
            'proofline_set-0-id': [''], 'proofline_set-0-ORDER': ['0'], 'proofline_set-0-line_no': ['1'], 
            'proofline_set-0-formula': ['A∧B'], 'proofline_set-0-rule': ['Premise'], 'check_proof': ['']})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proofchecker/proof_add_edit.html')

    def test_submit_proof_redirect(self):
        self.client = Client(enforce_csrf_checks=False)
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.post(reverse('add_proof'), {
            'name': ['Proof'], 'rules': ['tfl_basic'],  'premises': ['A∧B'], 'conclusion': ['A'], 'proofline_set-TOTAL_FORMS': ['1'], 
            'proofline_set-INITIAL_FORMS': ['0'], 'proofline_set-MIN_NUM_FORMS': ['0'], 
            'proofline_set-MAX_NUM_FORMS': ['1000'], 'proofline_set-__prefix__-id': [''], 
            'proofline_set-__prefix__-ORDER': [''], 'proofline_set-__prefix__-line_no': [''], 
            'proofline_set-__prefix__-formula': [''], 'proofline_set-__prefix__-rule': [''], 
            'proofline_set-0-id': [''], 'proofline_set-0-ORDER': ['0'], 'proofline_set-0-line_no': ['1'], 
            'proofline_set-0-formula': ['A∧B'], 'proofline_set-0-rule': ['Premise'], 'submit': ['']})
        self.assertEqual(response.status_code, 302)


class ProofViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create 5 proofs
        number_of_proofs = 13

        # Create test user
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_active='True')

        test_user1.save()
        test_user2.save()

        for _ in range(number_of_proofs):
            Proof.objects.create(
                premises = 'AvB',
                conclusion = '∧',
                created_by = test_user1
            )

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get('/proofs/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('all_proofs'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('all_proofs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proofchecker/allproofs.html')

    def test_lists_all_proofs(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('all_proofs'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['proof_list']), 6) # Paginated


class ProofUpdateViewTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_active='True')

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

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('update_proof', args=[1]))
        self.assertTemplateUsed(response, 'proofchecker/proof_add_edit.html')
        self.assertEqual(response.status_code, 200)
    
    def test_post_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.post(reverse('update_proof', args=[1]))
        self.assertTemplateUsed(response, 'proofchecker/proof_add_edit.html')
        self.assertEqual(response.status_code, 200)

    def test_check_proof_submission(self):
        self.client = Client(enforce_csrf_checks=False)
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.post(reverse('update_proof', args=[1]), {
            'name': ['Proof'], 'rules': ['tfl_basic'], 'premises': ['A∧B'], 'conclusion': ['A'], 'proofline_set-TOTAL_FORMS': ['2'], 'proofline_set-INITIAL_FORMS': ['2'], 
            'proofline_set-MIN_NUM_FORMS': ['0'], 'proofline_set-MAX_NUM_FORMS': ['1000'], 'proofline_set-0-id': ['1'], 'proofline_set-0-ORDER': ['0'], 
            'proofline_set-0-line_no': ['1'], 'proofline_set-0-formula': ['A∧B'], 'proofline_set-0-rule': ['Premise'], 'proofline_set-1-id': ['2'], 
            'proofline_set-1-ORDER': ['1'], 'proofline_set-1-line_no': ['2'], 'proofline_set-1-formula': ['A'], 'proofline_set-1-rule': ['∧E 1'], 
            'proofline_set-__prefix__-id': [''], 'proofline_set-__prefix__-ORDER': [''], 'proofline_set-__prefix__-line_no': [''], 
            'proofline_set-__prefix__-formula': [''], 'proofline_set-__prefix__-rule': [''], 'check_proof': ['']
            })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proofchecker/proof_add_edit.html')

    def test_submit_proof_redirect(self):
        self.client = Client(enforce_csrf_checks=False)
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.post(reverse('update_proof', args=[1]), {
            'name': ['Proof'], 'rules': ['tfl_basic'], 'premises': ['A∧B'], 'conclusion': ['A'], 'proofline_set-TOTAL_FORMS': ['2'], 'proofline_set-INITIAL_FORMS': ['2'], 
            'proofline_set-MIN_NUM_FORMS': ['0'], 'proofline_set-MAX_NUM_FORMS': ['1000'], 'proofline_set-0-id': ['1'], 'proofline_set-0-ORDER': ['0'], 
            'proofline_set-0-line_no': ['1'], 'proofline_set-0-formula': ['A∧B'], 'proofline_set-0-rule': ['Premise'], 'proofline_set-1-id': ['2'], 
            'proofline_set-1-ORDER': ['1'], 'proofline_set-1-line_no': ['2'], 'proofline_set-1-formula': ['A'], 'proofline_set-1-rule': ['∧E 1'], 
            'proofline_set-__prefix__-id': [''], 'proofline_set-__prefix__-ORDER': [''], 'proofline_set-__prefix__-line_no': [''], 
            'proofline_set-__prefix__-formula': [''], 'proofline_set-__prefix__-rule': [''], 'submit': ['']
            })
        self.assertEqual(response.status_code, 302)

class FeedbackFormTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        test_user1.save()

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('feedback'))
        self.assertTemplateUsed(response, 'proofchecker/feedback_form.html')
        self.assertEqual(response.status_code, 200)

    # def test_submit_feedback_redirect(self):
    #     self.client = Client(enforce_csrf_checks=False)
    #     login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
    #     response = self.client.post(reverse('feedback'), {
    #         'name': 'Test User',
    #         'email': 'test@gmail.com',
    #         'subject': 'Test Subject',
    #         'details': 'Hello World'
    #     })
    #     self.assertEqual(response.status_code, 302)

class StudentProofsViewTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True', is_instructor='True')
        test_instructor = Instructor.objects.create(user=test_user1)
        test_instructor.save()
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuK', is_active='True', is_student='True')
        test_student = Student.objects.create(user=test_user2)
        test_student.save()
        test_user2.save()

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('student_proofs'))
        self.assertTemplateUsed(response, 'proofchecker/student_proofs.html')
        self.assertEqual(response.status_code, 200)

    def test_specific_student(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('student_proofs'), args=[2])
        self.assertTemplateUsed(response, 'proofchecker/student_proofs.html')
        self.assertEqual(response.status_code, 200)

class CourseStudentProofsViewTest(TestCase):

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

        # Create a course
        test_course = Course.objects.create(
            title = "Test Course",
            term = "Fall 2022",
            section = "101",
            instructor = test_instructor,
        )

        test_course.save()

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')
        response = self.client.get(reverse('course_student_proofs', args=[1, 2]))
        self.assertTemplateUsed(response, 'proofchecker/course_student_proofs.html')
        self.assertEqual(response.status_code, 200)
