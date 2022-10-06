from django.conf.urls import url
from django.views.generic import RedirectView
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path

from . import views

admin.site.site_header = "ProofChecker Admin"


urlpatterns = [
    path("courses/<int:course_id>/students/<int:student_id>/proofs/all", views.course_student_proofs_view, name='course_student_proofs'),
    path('', views.home, name='home'),
    path("feedback/", views.feedback_form, name="feedback"),
    path("proofs/", views.ProofView.as_view(), name="all_proofs"),
    path("proofs/new/", views.proof_create_view, name="add_proof"),
    path('proofs/<int:pk>/', views.ProofDetailView.as_view(), name='proof_detail'),
    path("proofs/<pk>/update/", views.proof_update_view, name="update_proof"),
    path("proofs/<pk>/delete/", views.ProofDeleteView.as_view(), name="delete_proof"),
    path("proofs/checker/", views.proof_checker, name='proof_checker'),
    path("tests/syntaxtest", views.SyntaxTestPage, name='syntax_test'),
    path("students/proofs/", views.student_proofs_view, name='student_proofs'),
    path("students/proofs/<pk>", views.student_proofs_view, name='student_proofs'),
    path("students/grades", views.student_grades_view, name='student_grades'),
    # path("students/grades/<int:course_id>", views.student_grades_view, name='student_grades'),
    # path("students/assignments", views.student_assignment, name='student_assignment'),
    path("tests/syntaxtest", views.SyntaxTestPage, name='syntax_test'),
    path("version_log", views.version_log, name='version_log'),
    path("devs", views.devs, name='devs')
]
