from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from accounts.views import SignUpView, InstructorSignUpView, StudentSignUpView, StudentProfileView, InstructorProfileView, StudentProfileUpdateView, InstructorProfileUpdateView
from django.contrib.auth import views as auth_views
from .views import activate
urlpatterns = [
    path('accounts/signup/', SignUpView.as_view(), name="signup"),
    path('accounts/signup/student',
         StudentSignUpView.as_view(), name="student_signup"),
    path('accounts/signup/instructor',
         InstructorSignUpView.as_view(), name="instructor_signup"),

    # Forgot Password
    path('accounts/reset_password',
         auth_views.PasswordResetView.as_view(), name="password_reset"),
    path('accounts/reset_password/done',
         auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('accounts/reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('accounts/reset/done', auth_views.PasswordResetCompleteView.as_view(),
         name="password_reset_complete"),

    # Profile
    path('accounts/student', StudentProfileView.as_view(), name="student_profile"),
    path('accounts/instructor', InstructorProfileView.as_view(),
         name="instructor_profile"),
     path('accounts/student/profile-update/', StudentProfileUpdateView.as_view(), name='student_profile_update'),
     path('accounts/instructor/profile-update/', InstructorProfileUpdateView.as_view(), name='instructor_profile_update'),
     path('activate/<uidb64>/<token>',activate, name='activate'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
