import os

import pylatex
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.datetime_safe import datetime
from django.views.generic import ListView, DetailView, DeleteView
from pylatex import Document, Section, Tabular
from pylatex.position import FlushLeft
from pylatex.utils import bold, NoEscape

from accounts.decorators import instructor_required
from proofchecker.models import Student, Course, StudentProblemSolution
from proofchecker.proofs.proofchecker import verify_proof
from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj
from proofchecker.proofs.proofutils import get_premises
from proofchecker.proofs.disprover import makeDict, setVals, checkCntrEx 
from proofchecker.utils import folparser
from proofchecker.utils import tflparser
from .forms import ProofForm, ProofLineForm, FeedbackForm
from .models import Proof, Problem, ProofLine


def home(request):
    proofs = Proof.objects.all()
    context = {"proofs": proofs}
    return render(request, "proofchecker/home.html", context)


def version_log(request):
    return render(request, 'proofchecker/version_log.html')


def devs(request):
    return render(request, 'proofchecker/devs.html')


def SyntaxTestPage(request):
    return render(request, "proofchecker/testpages/syntax_test.html")


def proof_checker(request):
    ProofLineFormset = inlineformset_factory(
        Proof, ProofLine, form=ProofLineForm, extra=0, can_order=True)
    query_set = ProofLine.objects.none()
    form = ProofForm(request.POST or None)
    formset = ProofLineFormset(
        request.POST or None, instance=form.instance, queryset=query_set)
    response = None

    if request.POST:
        if all([form.is_valid(), formset.is_valid()]):

            parent = form.save(commit=False)

            if 'check_proof' in request.POST:
                # Create a new proof object
                proof = ProofObj(lines=[])

                # Grab premise and conclusion from the form
                # Assign them to the proof object
                proof.rules = str(parent.rules)
                proof.premises = get_premises(parent.premises)
                proof.conclusion = str(parent.conclusion)

                for line in formset.ordered_forms:
                    if len(line.cleaned_data) > 0 and not line.cleaned_data['DELETE']:
                        # Create a proofline object
                        proofline = ProofLineObj()

                        # Grab the line_no, formula, and expression from the form
                        # Assign them to the proofline object
                        child = line.save(commit=False)
                        child.proof = parent

                        proofline.line_no = str(child.line_no)
                        proofline.expression = str(child.formula)
                        proofline.rule = str(child.rule)

                        # Append the proofline to the proof object's lines
                        proof.lines.append(proofline)

                # Determine which parser to user based on selected rules
                if ((proof.rules == 'fol_basic') or (proof.rules == 'fol_derived')):
                    parser = folparser.parser
                else:
                    parser = tflparser.parser

                # Verify the proof!
                response = verify_proof(proof, parser)

                # Send the response back
                context = {
                    "form": form,
                    "formset": formset,
                    "response": response
                }

                return render(request, 'proofchecker/proof_checker.html', context)

    context = {
        "form": form,
        "formset": formset
    }
    return render(request, 'proofchecker/proof_checker.html', context)


@login_required
def proof_create_view(request):
    ProofLineFormset = inlineformset_factory(
        Proof, ProofLine, form=ProofLineForm, extra=0, can_order=True)
    query_set = ProofLine.objects.none()
    form = ProofForm(request.POST or None)
    formset = ProofLineFormset(
        request.POST or None, instance=form.instance, queryset=query_set)
    response = None

    if request.POST:
        if all([form.is_valid(), formset.is_valid()]):
            parent = form.save(commit=False)

            if 'check_proof' in request.POST:
                proof = ProofObj(lines=[])  #
                proof.rules = str(parent.rules)
                proof.premises = get_premises(parent.premises)
                proof.conclusion = str(parent.conclusion)
                proof.created_by = request.user.id

                for line in formset.ordered_forms:
                    if len(line.cleaned_data) > 0 and not line.cleaned_data['DELETE']:
                        proofline = ProofLineObj()
                        child = line.save(commit=False)
                        child.proof = parent
                        proofline.line_no = str(child.line_no)
                        proofline.expression = str(child.formula)
                        proofline.rule = str(child.rule)
                        proof.lines.append(proofline)

                # Determine which parser to user based on selected rules
                if ((proof.rules == 'fol_basic') or (proof.rules == 'fol_derived')):
                    parser = folparser.parser
                else:
                    parser = tflparser.parser

                response = verify_proof(proof, parser)

            elif 'submit' in request.POST:
                if len(formset.forms) > 0:
                    parent.created_by = request.user
                    parent.save()
                    formset.save()
                    return HttpResponseRedirect(reverse('all_proofs'))

            elif 'check_disproof' in request.POST:
                proof = ProofObj(lines=[])  #
                proof.rules = str(parent.rules)
                proof.premises = get_premises(parent.premises)
                proof.conclusion = str(parent.conclusion)
                
                valDict = setVals(makeDict(proof))
                response = checkCntrEx(proof,valDict)
                if response.is_valid:
                    print("That is a valid counterexample -- Good Job!")
                else:
                    print(response.err_msg)
                    
            elif 'autosave' in request.POST:
                    if len(formset.forms) > 0:
                        parent.created_by = request.user
                        parent.save()
                        formset.save()
        else: #Handle errors
            if (form.errors.__contains__('name')):
                messages.error(request, 'The name ' + str(form.data['name']) + ' has already exist. Please choose a different name for this proof.')

    context = {
        "object": form,
        "form": form,
        "formset": formset,
        "response": response
    }
    return render(request, 'proofchecker/proof_add_edit.html', context)


@login_required
def proof_update_view(request, pk=None):
    now = datetime.now()
    obj = get_object_or_404(Proof, pk=pk)
    all_proofs = Proof.objects.filter(complete = True) #need to switch to true once I figure out how to update the complete flag for proof in database
    all_proofs_names = []
    for item in all_proofs:
        all_proofs_names.append(item.name)

    if obj.created_by == request.user or request.user.is_instructor:
        ProofLineFormset = inlineformset_factory(
            Proof, ProofLine, form=ProofLineForm, extra=0, can_order=True)
        form = ProofForm(request.POST or None, instance=obj)
        formset = ProofLineFormset(
            request.POST or None, instance=obj, queryset=obj.proofline_set.order_by("ORDER"))
        response = None
        validation_failure = False

        if request.POST:
            if all([form.is_valid(), formset.is_valid()]):
                parent = form.save(commit=False) 
                if 'check_proof' in request.POST:
                    proof = ProofObj(lines=[])
                    proof.rules = str(parent.rules)
                    proof.premises = get_premises(parent.premises)
                    proof.conclusion = str(parent.conclusion)
                    proof.created_by = request.user.id
                    proof.lemmas_allowed = parent.lemmas_allowed
                    

                    for line in formset.ordered_forms:
                        if len(line.cleaned_data) > 0 and not line.cleaned_data['DELETE']:
                            proofline = ProofLineObj()
                            child = line.save(commit=False)
                            child.proof = parent
                            proofline.line_no = str(child.line_no)
                            proofline.expression = str(child.formula)
                            proofline.rule = str(child.rule)
                            proof.lines.append(proofline)

                    # Determine which parser to user based on selected rules
                    if (proof.rules == 'fol_basic') or (proof.rules == 'fol_derived'):
                        parser = folparser.parser
                    else:
                        parser = tflparser.parser

                    response = verify_proof(proof, parser)
                    
                    if (response.err_msg == None) and (response.is_valid): #confirms that proof is both valid and complete before updating complete flag to true
                        obj.complete = response.is_valid
                    else:
                        obj.complete = False
                    obj.save()
                    

                elif 'submit' in request.POST:
                    parent.created_by = request.user
                    parent.save()
                    formset.save()
                    return HttpResponseRedirect(reverse('all_proofs'))

                elif 'check_disproof' in request.POST:
                    proof = ProofObj(lines=[])  #
                    proof.rules = str(parent.rules)
                    proof.premises = get_premises(parent.premises)
                    proof.conclusion = str(parent.conclusion)
                    
                    valDict = setVals(makeDict(proof))
                    response = checkCntrEx(proof,valDict)
                    if response.is_valid:
                        print("That is a valid counterexample -- Good Job!")
                    else:
                        print(response.err_msg)

                elif 'autosave' in request.POST:
                    if len(formset.forms) > 0:
                        parent.created_by = request.user
                        parent.save()
                        formset.save()
            else: #Handle errors
                if (form.errors.__contains__('name')):
                    messages.error(request, 'The name ' + str(form.data['name']) + ' has already exist. Please choose a different name for this proof.')
        ## Get instructor user object who created the problem
        if hasattr(obj,'studentproblemsolution'):
            created_by = obj.proofline_set.instance.studentproblemsolution.assignment.created_by
        else:
            created_by = obj.created_by

        context = {
            "proofs": all_proofs,
            "object": obj,
            "form": form,
            "formset": formset,
            "response": response,
            "createdby": created_by
        }

        return render(request, 'proofchecker/proof_add_edit.html', context)
    else:
        raise PermissionDenied()


def get_latex_file(request, pk=None):
    now = datetime.now()
    obj = get_object_or_404(Proof, pk=pk)

    geometry_options = {"tmargin": "2cm", "lmargin": "2cm"}

    doc = Document(geometry_options=geometry_options, inputenc='utf8x')

    doc.preamble.append(pylatex.Command('title', obj.__dict__['name']))
    doc.preamble.append(pylatex.Command('author', str(request.user)))

    line_number_counter = 0
    form_count = obj.proofline_set.count()

    doc.append(pylatex.Command('fontsize', arguments=['15', '19']))
    doc.append(pylatex.Command('selectfont'))
    doc.append(NoEscape(r'\maketitle'))

    with doc.create(Section('Proof Details')):
        doc.append('Rules: ' + obj.__dict__['rules'] + "\n")
        doc.append('Premises: ' + obj.__dict__['premises'] + "\n")
        doc.append('Conclusion: ' + obj.__dict__['conclusion'] + "\n")

        with doc.create(Section('Proof Table')):
            with doc.create(Tabular('r|c|c')) as table:
                table.add_row(bold('Line #'), bold('Expression'), bold('Rule'))
                table.add_hline()

                while line_number_counter < form_count:
                    if obj.proofline_set.order_by('ORDER').values('line_no')[line_number_counter] in obj.proofline_set.order_by('ORDER').values('line_no'):
                        line_number_object = FlushLeft()
                        dot_count = str(obj.proofline_set.order_by('ORDER').values('line_no')[line_number_counter]).count('.') / 2
                        line_number_object.append(NoEscape(r'\hspace{' + str(dot_count) + 'cm}'))
                        line_number_object.append(
                            obj.proofline_set.order_by('ORDER').values('line_no')[line_number_counter]['line_no'])
                        table.add_row(
                            line_number_object,
                            obj.proofline_set.order_by('ORDER').values('formula')[line_number_counter]['formula'],
                            obj.proofline_set.order_by('ORDER').values('rule')[line_number_counter]['rule'],
                        )
                        table.add_hline()
                    line_number_counter = line_number_counter + 1

    filename = obj.__dict__['name'] + '-' + now.strftime("%d_%m_%Y.%H-%M-%S")+'.tex'
    response = HttpResponse(doc.dumps(), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)

    return response


class ProofView(LoginRequiredMixin, ListView):
    model = Proof
    template_name = "proofchecker/allproofs.html"
    paginate_by = 6

    def get_queryset(self):
        return Proof.objects.filter(created_by=self.request.user)


class ProofDetailView(UserPassesTestMixin, DetailView):
    model = Proof

    def test_func(self):
        obj = self.get_object()
        if obj.created_by == self.request.user or self.request.user.is_instructor:
            return True
        else:
            return False


class ProofDeleteView(DeleteView):
    model = Proof
    template_name = "proofchecker/delete_proof.html"
    success_url = "/proofs/"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            if StudentProblemSolution.objects.get(proof_id=obj.id):
                messages.error(
                    request, 'Proof from Assignment cannot be deleted!')
                return redirect('all_proofs')
            else:
                return super(ProofDeleteView, self).dispatch(request, *args, **kwargs)
        except:
            return super(ProofDeleteView, self).dispatch(request, *args, **kwargs)


class ProblemView(ListView):
    model = Problem
    template_name = "proofchecker/problems.html"


def feedback_form(request):
    if request.POST:
        form = FeedbackForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            details = form.cleaned_data.get('details')
            subject = form.cleaned_data.get('subject')
            mail_subject = 'Bug/Feedback - ' + subject
            email_body = details + "\n\nReported By - " + name + "\nEmail - " + email

            to_email = 'proofchecker.pwreset@gmail.com'
            email = EmailMessage(
                mail_subject, email_body, to=[to_email])
            try:
                attach = request.FILES['attach']
                if attach != None and attach.content_type != None:
                    email.attach(attach.name, attach.read(), attach.content_type)
            except:
                print()
            email.send()
            messages.success(
                request, f'Your Feedback/Bug has been recorded. Thank you')
            return redirect('home')
    else:
        form = FeedbackForm()
    return render(request, 'proofchecker/feedback_form.html', {'form': form})


@instructor_required
def student_proofs_view(request, pk=None):
    courses = Course.objects.filter(instructor__user=request.user)

    students = []
    for course in courses:
        for student in course.students.all():
            student.selected = False
            if student.pk == pk:
                student.selected = True
            students.append(student)

    students = list(set(students))

    student = None
    proofs = None

    if pk is not None:
        student = Student.objects.get(user__pk=pk)
        proofs = Proof.objects.filter(created_by=pk)

    context = {
        "students": students,
        "student": student,
        "proofs": proofs
    }
    return render(request, 'proofchecker/student_proofs.html', context)


@instructor_required
def student_grades_view(request, course_id=None):
    courses = Course.objects.filter(instructor__user=request.user)
    students = []
    if course_id is not None:
        for course in courses:
            if course.id is course_id:
                list_students = course.students.all()
                for student in list_students:
                    students.append(student.user)
    # else:
    #      for course in courses:
    #         for student in course.students.all():
    #             students.append(student)

    students = list(set(students))

    context = {
        "students": students,
        "courses": courses.all(),
        "course_id": course_id
    }
    return render(request, 'proofchecker/student_grades.html', context)


@instructor_required
def course_student_proofs_view(request, course_id=None, student_id=None):
    students = []
    students.append(Course.objects.get(id=course_id).students.all())

    student = None
    proofs = None

    if student_id is not None:
        student = Student.objects.get(user__pk=student_id)
        proofs = Proof.objects.filter(created_by=student_id)

    context = {
        "students": students,
        "student": student,
        "proofs": proofs
    }
    return render(request, 'proofchecker/course_student_proofs.html', context)
