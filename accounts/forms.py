from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction

from proofchecker.models import Student, Instructor, User


class DateInput(forms.DateInput):
    input_type = 'date'


class StudentSignUpForm(UserCreationForm):
    email = forms.EmailField()

    def clean_email(self):
        # if User.objects.filter(email=self.cleaned_data['email']).exists():
        #     raise forms.ValidationError(
        #         "The given e-mail address is already registered")
        return self.cleaned_data['email']

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.is_active = False
        user.save()

        student = Student.objects.create(user=user)
        student.save()
        return user


class InstructorSignUpForm(UserCreationForm):
    email = forms.EmailField()

    def clean_email(self):
        # if User.objects.filter(email=self.cleaned_data['email']).exists():
        #     raise forms.ValidationError(
        #         "The given e-mail address is already registered")
        return self.cleaned_data['email']

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self):
        user = super().save(commit=False)
        user.is_instructor = True
        user.is_active = False
        user.save()

        instructor = Instructor.objects.create(user=user)
        instructor.save()
        return user


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['image', 'bio', 'dob', 'mobile']
        widgets = {
            'dob': DateInput(),
        }


class InstructorProfileForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ['image', 'bio', 'dob', 'mobile']
        widgets = {
            'dob': DateInput(),
        }


class CSVUploadForm(forms.Form):
    file = forms.FileField()

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        if not file.name.endswith(".csv"):
            raise ValidationError(
                {
                    "file": "Filetype not supported, the file must be a '.csv'",
                }
            )
        return cleaned_data

    def check_columns(self, required_columns, dict_reader):
        for req_col in required_columns:
            if req_col not in dict_reader.fieldnames:
                raise ValidationError(
                    {
                        f"A required column is missing from the uploaded CSV: '{req_col}'"
                    }
                )

    def clean_email(self):
        # if User.objects.filter(email=self.cleaned_data['email']).exists():
        #     raise forms.ValidationError(
        #         "The given e-mail address is already registered")
        return self.cleaned_data['email']

    @transaction.atomic
    def save(self, email_address):
        user = User()
        user.username = email_address[0:email_address.find('@')]
        user.email = email_address
        user.password = User.objects.make_random_password(length=16)
        user.is_student = True
        user.is_active = False
        user.save()

        student = Student.objects.create(user=user)
        student.save()
        return user
