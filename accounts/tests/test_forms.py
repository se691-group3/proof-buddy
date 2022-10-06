from django.test import TestCase

from accounts.forms import InstructorSignUpForm, StudentSignUpForm

class StudentFormTest(TestCase):
    def test_submit(self):
        form = StudentSignUpForm(data={
            'username': 'abc',
            'email':'abc@123.com',
            'password1': '1X<ISRUkw+tuK',
            'password2': '1X<ISRUkw+tuK'
            })
        form.save()
        self.assertTrue(form.is_valid())

class InstructorFormTest(TestCase):
    def test_submit(self):
        form = InstructorSignUpForm(data={
            'username': 'abc',
            'email':'abc@123.com',
            'password1': '1X<ISRUkw+tuK',
            'password2': '1X<ISRUkw+tuK'
            })
        form.save()
        self.assertTrue(form.is_valid())
