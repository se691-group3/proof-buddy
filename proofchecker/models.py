from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from proofchecker.proofs.proofutils import is_line_no, make_tree
from proofchecker.utils import tflparser


def validate_line_no(value):
    try:
        is_line_no(value)
    except:
        raise ValidationError(
            _('%(value)s is not a valid line number'),
            params={'value': value},
        )


# TODO: This has to adjust based on parser... need to fix


def validate_formula(value):
    try:
        make_tree(value, tflparser.parser)
    except:
        raise ValidationError(
            _('%(value)s is not a valid expression'),
            params={'value': value},
        )


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(default='profile_pics/default.png',
                              upload_to='profile_pics', null=True, blank=True)
    mobile = models.CharField(max_length=10, null=True, default="xxxxxxxxxx")
    bio = models.TextField(max_length=500, blank=True)
    dob = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.image.path)

        if img.height > 200 or img.width > 200:
            output_size = (200, 200)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Instructor(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(default='profile_pics/default.png',
                              upload_to='profile_pics', null=True, blank=True)
    mobile = models.CharField(max_length=10, null=True, default="xxxxxxxxxx")
    bio = models.TextField(max_length=500, blank=True)
    dob = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.image.path)

        if img.height > 200 or img.width > 200:
            output_size = (200, 200)
            img.thumbnail(output_size)
            img.save(self.image.path)


RULES_CHOICES = (
    ('tfl_basic', 'TFL - Basic Rules Only'),
    ('tfl_derived', 'TFL - Basic & Derived Rules'),
    ('fol_basic', 'FOL - Basic Rules Only'),
    ('fol_derived', 'FOL - Basic & Derived Rules'),
)


class Proof(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rules = models.CharField(
        max_length=255, choices=RULES_CHOICES, default='tfl_basic')
    premises = models.CharField(max_length=255, blank=True, null=True)
    conclusion = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    complete = models.BooleanField(default = False)
    lemmas_allowed = models.BooleanField(default = False)
    disproof_string = models.CharField(max_length=255, null=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return ('{}. Proof {}:\nPremises: {},\nConclusion: {}\nLine Count: {}'.format(
            self.pk,
            self.name,
            self.premises,
            self.conclusion,
            self.proofline_set.count()
        ))

    def get_absolute_url(self):
        return "/proofs"


class ProofLine(models.Model):
    proof = models.ForeignKey(Proof, on_delete=models.CASCADE)
    line_no = models.CharField(max_length=100, validators=[validate_line_no])
    # TODO: Add a validator for the formula field.
    formula = models.CharField(max_length=255, null=True, blank=True)
    rule = models.CharField(max_length=255, null=True, blank=True)
    ORDER = models.IntegerField(null=True)
    comment= models.TextField(blank=True)
    response=models.TextField(blank=True)

    def __str__(self):
        return ('{}. Line {}: {}, {}'.format(
            self.pk,
            self.line_no,
            self.formula,
            self.rule
        ))


class Problem(models.Model):
    question = models.CharField(max_length=255, default='Solve the following problem')
    point = models.DecimalField(max_digits=5, decimal_places=2)
    target_steps = models.PositiveIntegerField()
    lost_points = models.PositiveIntegerField()
    proof = models.OneToOneField(Proof, on_delete=models.CASCADE)
    lemmas_allowed =models.BooleanField(default = False)
    show_target_steps = models.BooleanField(default=True)
    # If the proof is deleted, the problem is deleted


class Course(models.Model):
    title = models.CharField(max_length=255)
    term = models.CharField(max_length=255)
    section = models.PositiveSmallIntegerField()
    # Relationships
    instructor = models.ForeignKey(Instructor, on_delete=models.PROTECT)
    # One-to-many relationship (could perhaps be many-to-many)
    # If instructor is deleted, the course is preserved
    students = models.ManyToManyField(Student)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return "/courses"


class Assignment(models.Model):
    title = models.CharField(max_length=255, null=True, unique=True)
    created_by = models.ForeignKey(
    Instructor, on_delete=models.CASCADE, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True)
    due_by = models.DateTimeField()
    resubmissions = models.IntegerField(default=0, null=True, blank=True)
    problems = models.ManyToManyField(Problem)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_submitted = models.BooleanField(default=False)
    is_late_submitted = models.BooleanField(default=False)
    is_late_submitted_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return "/assignments"


class StudentProblemSolution(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    proof = models.OneToOneField(Proof, on_delete=models.DO_NOTHING)
    submitted_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = (("student", "assignment", "problem", "proof"),)

    def __str__(self):
        return ('{}. student {}, assignment {}, problem {}, proof {}'.format(
            self.pk,
            self.student.user.pk,
            self.assignment.id,
            self.problem.id,
            self.proof.id
        ))



class Feedback(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=120)
    details = models.TextField(max_length=700)
    # attach = models.FileField(blank=True, null=True) , widget=forms.ClearableFileInput(       attrs={'multiple': True}))
    attach = models.FileField(blank=True, null=True)


