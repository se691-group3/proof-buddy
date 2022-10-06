import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import DeleteView

from accounts.decorators import instructor_required, student_required
from proofchecker.models import Course, Instructor, Proof
from proofchecker.models import Student
from .forms import CourseCreateForm


# Create your views here.

@login_required
def all_courses_view(request):
    if request.user.is_instructor:
        return instructor_courses_view(request)
    elif request.user.is_student:
        return student_courses_view(request)


@student_required
def student_courses_view(request):
    object_list = Student.objects.get(user=request.user).course_set.all()
    courses_to_enroll = Course.objects.filter(~Q(students__user=request.user))

    context = {
        "object_list": object_list,
        "courses_to_enroll": courses_to_enroll
    }
    return render(request, "courses/student_courses.html", context)


@student_required
def enroll_course_view(request, course_id=None):
    Course.objects.get(id=course_id).students.add(Student.objects.get(user=request.user))
    return student_courses_view(request)


@login_required
def course_detail_view(request, course_id=None):
    course = get_object_or_404(Course, id=course_id)
    form = CourseCreateForm(request.POST or None, instance=course)
    students = Student.objects.all()

    if request.user.is_instructor:
        if request.POST:
            if form.is_valid():
                selected_students = request.POST.getlist('studentsSelector[]')
                course = form.save(commit=False)
                course.instructor = Instructor.objects.get(user_id=request.user)
                course.save()
                course.students.clear()
                for student in selected_students:
                    course.students.add(student)
                course.save()
                messages.success(request, f'Course saved successfully')
            else:
                messages.error(request, f'Validation failed. Course is not saved.')
    logger = logging.getLogger('django')
    logger.info("outside of student")
    if request.user.is_student:
        logger.info( "inside of student")
        form.disabled_all();

    

    assignments = Course.objects.get(id=course_id).assignment_set.all();

    selected_students_count = 0
    selected_students = []
    for student in students:
        proofs = Proof.objects.filter(created_by__student=student)
        if student.course_set.filter(id=course_id).exists():
            selected_students.append({'student': student, 'selected': 'selected', 'proofs': proofs})
            selected_students_count += 1
        else:
            selected_students.append({'student': student, 'selected': None, 'proofs': proofs})

    back_view = "student_courses"
    if request.user.is_instructor:
        back_view = "instructor_courses"

    context = {
        "form": form,
        "course": course,
        "assignments": assignments,
        "students": selected_students,
        "selected_students_count": selected_students_count,
        "back_view": back_view
    }
    return render(request, "courses/course_details.html", context)


@instructor_required
def instructor_courses_view(request):
    object_list = Course.objects.filter(instructor__user=request.user)
    context = {
        "object_list": object_list
    }
    return render(request, "courses/instructor_courses.html", context)


@instructor_required
def course_create_view(request):
    form = CourseCreateForm(request.POST or None)
    students = Student.objects.all()

    if request.POST:
        if form.is_valid():
            selected_students = request.POST.getlist('studentsSelector[]')
            course = form.save(commit=False)
            course.instructor = Instructor.objects.get(user=request.user)
            course.save()
            course.students.clear()
            for student in selected_students:
                course.students.add(student)
            course.save()
            messages.success(request, f'Course saved successfully')
            return HttpResponseRedirect(reverse('course_details', kwargs={'course_id': course.id}))

    context = {
        "form": form,
        "students": students
    }
    return render(request, "courses/add_course.html", context)


class CourseDeleteView(DeleteView):
    model = Course
    template_name = "courses/delete_course.html"
    success_url = "/courses/all"
