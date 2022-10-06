from django.test import TestCase
from django.urls.base import reverse
from proofchecker.models import Instructor, Student, User

class StudentSignUpViewTests(TestCase):

    def test_get_context_data(self):
        """
        Verify the get_context_data method is working
        """
        response = self.client.get(reverse('student_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup_form.html')
        self.assertEqual(response.context['user_type'], 'student')

    def test_redirects_with_valid_input(self):
        response = self.client.post(reverse('student_signup'), {
            'username': 'abc',
            'email':'abc@123.com',
            'password1': '1X<ISRUkw+tuK',
            'password2': '1X<ISRUkw+tuK'
        })
        self.assertRedirects(response, reverse('login'))

class InstructorSignUpViewTests(TestCase):

    def test_get_context_data(self):
        """
        Verify the get_context_data method is working
        """
        response = self.client.get(reverse('instructor_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup_form.html')
        self.assertEqual(response.context['user_type'], 'instructor')

    def test_redirects_with_valid_input(self):
        response = self.client.post(reverse('instructor_signup'), {
            'username': 'abc',
            'email':'abc@123.com',
            'password1': '1X<ISRUkw+tuK',
            'password2': '1X<ISRUkw+tuK'
        })
        self.assertRedirects(response, reverse('login'))


class StudentProfileViewTests(TestCase):

    def test_get_context_data(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True', is_student='True')
        test_student1 = Student.objects.create(user=test_user1, bio="Hello World", mobile='555-123-4567')
        test_student1.save()
        test_user1.save()
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')

        response = self.client.get(reverse('student_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/student_profile.html')


class InstructorProfileViewTests(TestCase):

    def test_get_context_data(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True', is_student='True')
        test_student1 = Instructor.objects.create(user=test_user1, bio="Hello World", mobile='555-123-4567')
        test_student1.save()
        test_user1.save()
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')

        response = self.client.get(reverse('instructor_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/instructor_profile.html')    


class StudentProfileUpdateViewTests(TestCase):

    def test_get_context_data(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True', is_student='True')
        test_student1 = Student.objects.create(user=test_user1, bio="Hello World", mobile='555-123-4567')
        test_student1.save()
        test_user1.save()
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')

        response = self.client.get(reverse('student_profile_update'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/student_profile_update.html')

class InstructorProfileUpdateViewTests(TestCase):

    def test_get_context_data(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', is_active='True', is_student='True')
        test_student1 = Instructor.objects.create(user=test_user1, bio="Hello World", mobile='555-123-4567')
        test_student1.save()
        test_user1.save()
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_active='True')

        response = self.client.get(reverse('instructor_profile_update'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/instructor_profile_update.html')
