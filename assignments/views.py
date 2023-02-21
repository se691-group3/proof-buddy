from django.utils import timezone
from django.utils.datetime_safe import datetime
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DeleteView
import csv
import pylatex
from accounts.decorators import instructor_required
from proofchecker.forms import ProofLineForm
from proofchecker.models import (
    Proof,
    ProofLine,
    Problem,
    Assignment,
    Instructor,
    Course,
    Student,
    StudentProblemSolution,
    User,
    RULES_CHOICES
)
from proofchecker.proofs.proofchecker import verify_proof
from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj
from proofchecker.proofs.proofutils import get_premises
from proofchecker.utils import folparser, tflparser
from .forms import (
    AssignmentForm,
    ProblemForm,
    ProblemProofForm,
    StudentProblemProofForm,
    StudentProblemForm,
)
from .models import AssignmentDelay
from pylatex import Document, Section, Tabular
from pylatex.position import FlushLeft
from pylatex.utils import bold, NoEscape

@login_required
def all_assignments_view(request):
    if request.user.is_instructor:
        return instructor_assignments_view(request)
    elif request.user.is_student:
        return student_assignments_view(request)


def instructor_assignments_view(request):
    cols = ['id', 'title', 'course__title', 'due_by']
    object_list = Assignment.objects.filter(created_by__user=request.user).values(*cols)
    for obj in object_list:
        obj['course'] = obj['course__title']
        obj.pop('course__title')

        assignment_delay_qs = AssignmentDelay.objects.filter(assignment_id=obj['id'],
                                                             submission_date__isnull=True).exists()
        if assignment_delay_qs:
            obj.update({'submission': True})
        else:
            obj.update({'submission': False})

    print("object_list:", object_list)
    context = {
        "object_list": object_list,
    }
    return render(request, "assignments/instructor_assignments.html", context)


def student_assignments_view(request):
    today_date = datetime.now()
    today_date = today_date.strftime("%Y-%m-%d %H:%M:%S")
    print("today_date:", today_date)
    object_list = Assignment.objects.filter(
        course__in=Course.objects.filter(Q(students__user=request.user)),
        start_date__lte=today_date
    )
    print("object_list:", object_list)
    context = {
        "object_list": object_list,
    }
    return render(request, "assignments/student_assignments.html", context)


#
# @login_required(decorators, name='dispatch')
# class AssignmentListView(ListView):
#     model = Assignment
#     template_name = "assignments/instructor_assignments.html"
#
#     def get_queryset(self):
#         return Assignment.objects.filter(created_by__user=self.request.user)
#


@instructor_required
def create_assignment_view(request):
    form = AssignmentForm(request.user, request.POST or None)
    instructor = Instructor.objects.get(user=request.user)

    if request.POST:
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = instructor
            assignment.save()
            messages.success(request, "Assignment got created successfully!")

            return HttpResponseRedirect(
                reverse("assignment_details", kwargs={"pk": assignment.pk})
            )
        else:
            messages.error(request, form.errors)

    context = {
        "form": form,
    }
    return render(request, "assignments/add_assignment.html", context)


@login_required
def assignment_details_view(request, pk=None):
    studentPk = request.GET.get("studentId")
    if studentPk is None:
        if request.user.is_student:
            studentPk = request.user.pk

    assignment = get_object_or_404(Assignment, pk=pk)
    start_date = assignment.start_date.strftime("%Y-%m-%d")
    current_date = datetime.now().strftime("%Y-%m-%d")

    print("studentPk:", studentPk)
    print("start_date:", start_date)
    if studentPk:
        if current_date >= start_date:
            print("inside if")
        else:
            print("inside else")
            return HttpResponseRedirect("/assignments")

    assignment_date = assignment.due_by.strftime("%Y-%m-%d")

    user_assignment_delay_obj = None
    can_user_request = None
    submission_date = None
    submission_allowed = None
    status = None
    all_problem_grading_complete = False

    total_problem = Assignment.objects.filter(id=assignment.id).values_list('problems__id').count()
    print("total_problem:", total_problem)
    total_grading = StudentProblemSolution.objects.filter(assignment=assignment, student_id=studentPk,
                                                          grade__isnull=False).count()
    print("total_grading:", total_grading)

    if total_grading >= total_problem:
        all_problem_grading_complete = True

    print("all_problem_grading_complete:", all_problem_grading_complete)

    if current_date > assignment_date:
        # print("Time over")
        can_user_request = True

    user_assignment_delay_qs = AssignmentDelay.objects.filter(assignment=assignment, student_id=studentPk)
    print("user_assignment_delay_qs", user_assignment_delay_qs)
    if user_assignment_delay_qs.exists():
        can_user_request = False
        user_assignment_delay_obj = user_assignment_delay_qs.first()
        submission_date = user_assignment_delay_obj.submission_date
        status = user_assignment_delay_obj.status
        if submission_date:
            submission_date = submission_date.strftime("%Y-%m-%d")
            if submission_date >= current_date and status == "accepted":
                submission_allowed = True

    # print("submission_date:", submission_date)
    # print("submission_allowed:", submission_allowed)

    if studentPk is not None:
        date = assignment.due_by
        today = datetime.now()
        diff = today.replace(tzinfo=timezone.utc) - date
        if diff and diff.days > 0:
            assignment.is_submitted = True
            assignment.save()

        late_assignment_obj = user_assignment_delay_qs.first()
        # print("late_Assignment_obj:", late_assignment_obj)
        if late_assignment_obj:
            submission_date = late_assignment_obj.submission_date
            # print("submission_date", submission_date)
            # print("current_date", current_date)
            if submission_date:
                submission_date = submission_date.strftime("%Y-%m-%d")
                if current_date > submission_date:
                    assignment.is_late_submitted = True
                    assignment.save()

    solutions = StudentProblemSolution.objects.filter(assignment=pk, student=studentPk)

    form = AssignmentForm(request.user, request.POST or None, instance=assignment)
    problems = assignment.problems.all()
    totalgrade = 0
    totalpoint = 0
    for problem in problems:
        setattr(problem, "grade", 0)
        totalpoint = totalpoint + problem.point
        for solution in solutions:
            if solution.problem.pk == problem.pk:
                if solution.grade:
                    problem.grade = solution.grade
                    # setattr(problem, 'grade', solution.grade)
                totalgrade = totalgrade + problem.grade
                break

    if request.POST:
        if form.is_valid():
            assignment = form.save(commit=False)
            if request.user.is_student:
                get_student = Student.objects.get(user=request.user)
                get_proof = StudentProblemSolution.objects.filter(
                    assignment=assignment, student=get_student
                )

                # note that "prooff" is NOT a typo!
                for i in get_proof:
                    get_proof = i.proof
                    prooff = ProofObj(lines=[])  #
                    prooff.rules = str(get_proof.rules)
                    prooff.premises = get_premises(get_proof.premises)
                    prooff.conclusion = str(get_proof.conclusion)
                    get_lines = ProofLine.objects.filter(proof=get_proof)
                    for line in get_lines:
                        print(line)
                        proofline = ProofLineObj()
                        proofline.line_no = str(line.line_no)
                        proofline.expression = str(line.formula)
                        proofline.rule = str(line.rule)
                        prooff.lines.append(proofline)
                    if (prooff.rules == "fol_basic") or (prooff.rules == "fol_derived"):

                        parser = folparser.parser
                    else:
                        parser = tflparser.parser
                    response = verify_proof(prooff, parser)
                    if response.err_msg:
                        i.grade = 0
                        i.save()
                    else:
                        if get_lines.count() <= i.problem.target_steps:
                            i.grade = i.problem.point
                            i.save()
                        else:
                            more_line = get_lines.count() - i.problem.target_steps
                            scroe_lost = more_line * i.problem.lost_points
                            i.grade = i.problem.point - scroe_lost
                            i.save()
            # print("dddddd", response.err_msg)

            # if studentPk is not None:
            # assignment.is_submitted = True
            # assignment.is_late_submitted = True
            assignment.problems.add(*problems)
            assignment.save()

            return HttpResponseRedirect(reverse("all_assignments"))
        else:
            messages.error(request, form.errors)

    # if request.user.is_student:
    #     form.disabled_all();
    context = {
        "assignment": assignment,
        "form": form,
        "problems": problems,
        "totalgrade": totalgrade,
        "totalpoint": totalpoint,
        'can_user_request': can_user_request,
        'assignment_delay': user_assignment_delay_obj,
        'submission': submission_allowed,
        'grading': all_problem_grading_complete,
    }

    return render(request, "assignments/assignment_details.html", context)


class AssignmentDeleteView(DeleteView):
    model = Assignment
    template_name = "assignments/delete_assignment.html"
    success_url = "/assignments/"


@login_required
def create_problem(request):
    problem_form = ProblemForm(request.POST or None)
    proof_form = ProblemProofForm(request.POST or None)

    query_set = ProofLine.objects.none()
    ProofLineFormset = inlineformset_factory(
        Proof, ProofLine, form=ProofLineForm, extra=0, can_order=True
    )
    formset = ProofLineFormset(
        request.POST or None, instance=proof_form.instance, queryset=query_set
    )

    assignmentPk = request.GET.get("assignment")
    problem = None

    if request.POST:
        if all([problem_form.is_valid(), proof_form.is_valid(), formset.is_valid()]):
            problem = problem_form.save(commit=False)
            proof = proof_form.save(commit=False)

            proof.created_by = request.user
            proof.save()
            formset.save()

            problem.proof = proof
            problem.save()

            if assignmentPk is not None:
                # problem page loaded from assignment page
                assignment = Assignment.objects.get(id=assignmentPk)
                assignment.problems.add(problem)
                assignment.save()

                return redirect("/assignment/" + assignmentPk + "/details")

            return HttpResponseRedirect(reverse("all_assignments"))

    if request.user.is_student:
        problem_form.disabled_all()
        proof_form.disabled_all()

    context = {
        "problem_form": problem_form,
        "proof_form": proof_form,
        "formset": formset,
    }
    return render(request, "assignments/problem_details.html", context)


@login_required
def problem_details_view(request, pk=None):
    problem = get_object_or_404(Problem, pk=pk)
    problem_form = ProblemForm(request.POST or None, instance=problem)

    studentPk = request.GET.get("studentId")
    if studentPk is None:
        if request.user.is_student:
            studentPk = request.user.pk

    assignmentPk = request.GET.get("assignment")
    proof = None
    try:
        solution = StudentProblemSolution.objects.get(
            student__user_id=studentPk,
            assignment=Assignment.objects.get(id=assignmentPk),
            problem=problem,
        )
        if solution is not None:
            return problem_solution_view(request, problem.id)
    except StudentProblemSolution.DoesNotExist:
        pass

    proof = Proof.objects.get(problem=problem)

    proof_form = ProblemProofForm(request.POST or None, instance=proof)

    ProofLineFormset = inlineformset_factory(
        Proof, ProofLine, form=ProofLineForm, extra=0, can_order=True
    )
    formset = ProofLineFormset(
        request.POST or None,
        instance=proof,
        queryset=proof.proofline_set.order_by("ORDER"),
    )

    if request.POST:
        if all([problem_form.is_valid(), proof_form.is_valid(), formset.is_valid()]):
            problem = problem_form.save(commit=False)
            proof = proof_form.save(commit=False)

            proof.created_by = request.user
            proof.save()
            formset.save()

            problem.proof = proof
            problem.save()
            messages.success(request, "Problem saved successfully")

            if assignmentPk is not None:
                # problem page loaded from assignment page
                return HttpResponseRedirect(
                    reverse("assignment_details", kwargs={"pk": assignmentPk})
                )

            return HttpResponseRedirect(reverse("all_assignments"))


    if request.user.is_student:
        problem_form.disabled_all()
        proof_form.disabled_all()

    context = {
        "object": problem,
        "problem_form": problem_form,
        "proof_form": proof_form,
        "formset": formset,
        "rules": proof.rules
    }
    return render(request, "assignments/problem_details.html", context)


@login_required
def problem_solution_view(request, problem_id=None):
    problem = get_object_or_404(Problem, pk=problem_id)
    problem_form = StudentProblemForm(request.POST or None, instance=problem)

    studentPk = request.GET.get("studentId")
    if studentPk is None:
        if request.user.is_student:
            studentPk = request.user.pk

    assignmentPk = request.GET.get("assignment")
    proof = None
    try:
        solution = StudentProblemSolution.objects.get(
            student__user_id=studentPk,
            assignment_id=assignmentPk,
            problem_id=problem.id,
        )
        proof = solution.proof
    except StudentProblemSolution.DoesNotExist:
        print("no solution exists")
        problem_proof_id = problem.proof.id
        proof = Proof.objects.get(id=problem_proof_id)
        proof.id = None
        proof.created_by = User.objects.get(pk=studentPk)
        proof.save()

        prooflines = ProofLine.objects.filter(proof_id=problem_proof_id)

        for proofline in prooflines:
            proofline.id = None
            proofline.proof = proof
            proofline.save()

        solution = StudentProblemSolution(
            student=Student.objects.get(user_id=studentPk),
            assignment=Assignment.objects.get(id=assignmentPk),
            problem=Problem.objects.get(pk=problem_id),
            proof=Proof.objects.get(id=proof.id),
        )
        solution.save()

    proof_form = StudentProblemProofForm(request.POST or None, instance=proof)

    ProofLineFormset = inlineformset_factory(
        Proof, ProofLine, form=ProofLineForm, extra=0, can_order=True
    )
    formset = ProofLineFormset(
        request.POST or None,
        instance=proof,
        queryset=proof.proofline_set.order_by("ORDER"),
    )

    response = None
    if request.POST:
        if all([problem_form.is_valid(), proof_form.is_valid(), formset.is_valid()]):
            parent = proof_form.save(commit=False)
            if "check_proof" in request.POST:
                proof = ProofObj(lines=[])  #
                proof.rules = str(parent.rules)
                proof.premises = get_premises(parent.premises)
                proof.conclusion = str(parent.conclusion)

                for line in formset.ordered_forms:
                    if len(line.cleaned_data) > 0 and not line.cleaned_data["DELETE"]:
                        proofline = ProofLineObj()
                        child = line.save(commit=False)
                        child.proof = parent
                        proofline.line_no = str(child.line_no)
                        proofline.expression = str(child.formula)
                        proofline.rule = str(child.rule)
                        proof.lines.append(proofline)
                # Determine which parser to user based on selected rules
                if (proof.rules == "fol_basic") or (proof.rules == "fol_derived"):
                    parser = folparser.parser
                else:
                    parser = tflparser.parser
                response = verify_proof(proof, parser)

            elif "submit" in request.POST:
                #assignmentPk.assignment.resubmissions -= 1
                proof.save()
                formset.save()
                messages.success(request, "Solution saved successfully")
                return HttpResponseRedirect(
                    reverse("assignment_details", kwargs={"pk": assignmentPk})
                )

            elif 'autosave' in request.POST:
                proof.save()
                formset.save()

    if request.user.is_student:
        problem_form.disabled_all()
        proof_form.disabled_all()

    context = {
        "object": problem,
        "problem_form": problem_form,
        "proof_form": proof_form,
        "formset": formset,
        "response": response,
        "rules": proof.rules
    }
    return render(request, "assignments/problem_solution.html", context)


class ProblemView(ListView):
    model = Problem
    template_name = "assignments/problems.html"

    # def get_queryset(self):
    #     return Problem.objects.filter(instructor__user=self.request.user)


class ProblemDeleteView(DeleteView):
    model = Problem
    template_name = "assignments/delete_problem.html"
    success_url = "/problems/"


def get_problem_anaylsis_csv_file(request, id):
    
    all_student = StudentProblemSolution.objects.filter(assignment_id=id).values('student').distinct()
    response = HttpResponse('')
    response['Content-Disposition'] = 'attachment; filename=student_grading.csv'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Name', 'Email', 'Course', 'Assignment', 'Problem', 'Point Recieved', 'Problem Total',
                     'Total Points'])

    problem_obj = Assignment.objects.filter(id=id).values('problems__point')
    total_points = 0
    for problem in problem_obj:
        total_points += problem['problems__point']
        # print("PID; ", Problem.objects.filter(id=problem['problems__id']))

    for student_grading in all_student:
        print("student_grading:", student_grading)
        student_grading = StudentProblemSolution.objects.filter(assignment_id=id, student=student_grading['student'])
        for obj in student_grading:
            print("obj:", obj)
            username = obj.student.user.username
            full_name = obj.student.user.first_name + ' ' + obj.student.user.last_name
            email = obj.student.user.email
            course = obj.assignment.course.title
            assignment = obj.assignment.title
            problem = obj.problem.question
            grade = obj.grade
            problem_total = obj.problem.point
            total = total_points
            writer.writerow([username, full_name, email, course, assignment, problem, grade, problem_total, total])

    return response


def get_grading_csv_file(request, id):
    all_student = StudentProblemSolution.objects.filter(assignment_id=id).values('student').distinct()
    assignment_name = Assignment.objects.filter(id=id)[0]
    response = HttpResponse('')
    response['Content-Disposition'] = 'attachment; filename=student_grading_for_'+str(assignment_name)+'.csv'
    writer = csv.writer(response)

    writer.writerow(['Username', assignment_name])

    for student_grading in all_student:
        student_grading = StudentProblemSolution.objects.filter(assignment_id=id, student=student_grading['student'])
        for obj in student_grading:
            username = obj.student.user.username
            grade = obj.grade
            writer.writerow([username, grade])

    return response


def request_for_assignment_delay(request, a_id):
    assignment_id = a_id
    print("assignment_id", assignment_id)
    due_date = Assignment.objects.get(id=assignment_id).due_by
    student = Student.objects.get(user=request.user)

    AssignmentDelay.objects.create(assignment_id=assignment_id, student=student, due_date=due_date)

    return HttpResponseRedirect(f'/assignment/{assignment_id}/details')


def user_assignment_request(request, a_id):
    assignment_id = a_id
    print("assignment_id", assignment_id)
    assignment_obj = Assignment.objects.get(id=assignment_id)
    if assignment_obj.created_by.user == request.user:
        delay_assignment = AssignmentDelay.objects.filter(assignment=assignment_obj,
                                                          submission_date__isnull=True).values('id',
                                                                                               'student__user__username')
        if request.method == "GET":
            context = {'assignment': assignment_obj, 'students': delay_assignment}
            return render(request, "assignments/assignment_delay_request.html", context)

        if request.method == "POST":
            students_list = request.POST.getlist('students')
            submission_date = request.POST.get('submission_date')
            status = request.POST.get('status')
            print("students_list:", students_list)
            print("submission_date:", submission_date)
            print("status:", status)

            current_date = datetime.now().strftime("%Y-%m-%d")

            if submission_date > current_date:
                if status == "rejected":
                    submission_date = current_date

                for student_id in students_list:
                    AssignmentDelay.objects.filter(id=student_id).update(submission_date=submission_date, status=status)
            else:
                messages.warning(request, "New date should be greater then today's date")
                return HttpResponseRedirect(f"/user_assignment_request/{assignment_id}")

        return HttpResponseRedirect('/assignments')
    else:
        return HttpResponse("not authorize to view")


def get_latex_file_assignment(request, pk=None):
    now = datetime.now()

    problem = get_object_or_404(Problem, pk=pk)

    obj = Proof.objects.get(problem=problem)


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

