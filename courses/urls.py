from django.urls import path

from . import views


urlpatterns = [
    path("students/courses/all", views.student_courses_view, name="student_courses"),
    path("students/courses/enroll/<int:course_id>", views.enroll_course_view, name="enroll_course"),

    path("instructor/courses/all", views.instructor_courses_view, name="instructor_courses"),

    path('courses/all', views.all_courses_view, name="all_courses"),

    path('courses/add', views.course_create_view, name="add_course"),
    path('courses/<int:course_id>/details', views.course_detail_view, name="course_details"),
    path('courses/<int:pk>/delete', views.CourseDeleteView.as_view(), name="delete_course"),
]
