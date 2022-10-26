from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView
from django.views.generic import TemplateView

# Create your views here.
from accounts.forms import StudentSignUpForm, InstructorSignUpForm, StudentProfileForm, InstructorProfileForm, UserForm
from proofchecker.models import Student, Instructor
from .tokens import account_activation_token

User = get_user_model()


class SignUpView(TemplateView):
    template_name = "accounts/signup.html"


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = "accounts/signup_form.html"

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()

        # Email Activation Setup
        # domain = get_current_site(self.request).domain
        # mail_subject = 'Activate Your Account'
        # uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        # link = reverse('activate', kwargs={
        #     'uidb64': uidb64, 'token': account_activation_token.make_token(user)
        # })
        # activate_url = "http://" + domain + link
        # email_body = "Hi " + user.username + \
        #              ", Please click on the link to confirm your registration.\n" + activate_url
        # to_email = form.cleaned_data.get('email')
        # email = EmailMessage(
        #     mail_subject, email_body, to=[to_email])
        # email.send()

        # username = form.cleaned_data.get('username')
        # messages.success(
        #     self.request, f'Account created for {user.username}. Check Mail to activate the account.')
        return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception as e:
        pass

    if user is not None:
        user.is_active = True
        user.save()
        messages.success(request, f'Account activated for {user.username}')
        return redirect('login')
    else:
        messages.error(request, f'Error occurred while activating account.')
        return redirect('login')


class InstructorSignUpView(CreateView):
    model = User
    form_class = InstructorSignUpForm
    template_name = "accounts/signup_form.html"

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()

        # domain = get_current_site(self.request).domain
        # mail_subject = 'Activate Your Account'
        # uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        # link = reverse('activate', kwargs={
        #     'uidb64': uidb64, 'token': account_activation_token.make_token(user)
        # })
        # activate_url = "http://" + domain + link
        # email_body = "Hi " + user.username + \
        #              ", Please click on the link to confirm your registration.\n" + activate_url
        # to_email = form.cleaned_data.get('email')
        # email = EmailMessage(
        #     mail_subject, email_body, to=[to_email])
        # email.send()

        # username = form.cleaned_data.get('username')
        # messages.success(
        #     self.request, f'Account created for {user.username}. Check Mail to activate the account.')
        return redirect('login')


class StudentProfileView(CreateView):
    model = Student
    form_class = StudentProfileForm
    template_name = "profiles/student_profile.html"

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request, f'Profile Updated Successfully')
        return redirect('student_profile')


class InstructorProfileView(CreateView):
    model = Instructor
    form_class = InstructorProfileForm
    template_name = "profiles/instructor_profile.html"

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request, f'Profile Updated Successfully')
        return redirect('instructor_profile')


class StudentProfileUpdateView(TemplateView):
    user_form = UserForm
    form_class = StudentProfileForm
    template_name = "profiles/student_profile_update.html"

    def post(self, request):
        post_data = request.POST or None
        file_data = request.FILES or None

        user_form = UserForm(post_data, instance=request.user)
        profile_form = StudentProfileForm(
            post_data, file_data, instance=request.user.student)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Profile Updated Successfully')
            return redirect('student_profile')
        context = self.get_context_data(
            user_form=user_form, profile_form=profile_form)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class InstructorProfileUpdateView(TemplateView):
    user_form = UserForm
    form_class = InstructorProfileForm
    template_name = "profiles/instructor_profile_update.html"

    def post(self, request):
        post_data = request.POST or None
        file_data = request.FILES or None

        user_form = UserForm(post_data, instance=request.user)
        profile_form = InstructorProfileForm(
            post_data, file_data, instance=request.user.instructor)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Profile Updated Successfully')
            return redirect('instructor_profile')
        context = self.get_context_data(
            user_form=user_form, profile_form=profile_form)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
