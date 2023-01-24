from django import forms

from proofchecker.models import Assignment, Problem, Proof, Course


class DateInput(forms.DateInput):
    input_type = 'date'


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'course', 'start_date', 'due_by', 'is_submitted']
        widgets = {
            'start_date': DateInput(),
            'due_by': DateInput()
        }
        
    def disabled_all(self):
        self.fields['title'].widget.attrs['read-only'] = True
        self.fields['course'].widget.attrs['read-only'] = True
        self.fields['due_by'].widget.attrs['read-only'] = True

    def __init__(self, user, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)
        if user.is_instructor:
            self.fields['course'].queryset = Course.objects.filter(instructor__user=user)
        elif user.is_student:
            self.fields['course'].queryset = Course.objects.filter(students__user=user)


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['question', 'point', 'target_steps', 'show_target_steps', 'lost_points']

    def __init__(self, *args, **kwargs):
        super(ProblemForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['onkeydown'] = 'replaceCharacter(this)'

    def disabled_all(self):
        self.fields['question'].widget.attrs['read-only'] = True
        self.fields['point'].widget.attrs['read-only'] = True
        self.fields['target_steps'].widget.attrs['read-only'] = True
        self.fields['lost_points'].widget.attrs['read-only'] = True
        self.fields['show_target_steps'].widget.attrs['read-only'] = True

class StudentProblemForm(ProblemForm):
    def __init__(self, *args, **kwargs):
        super(StudentProblemForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        # if instance and instance.id:
        #     self.fields['question'].widget.attrs['disabled'] = 'disabled'
        #     self.fields['point'].widget.attrs['disabled'] = 'disabled'
        #     self.fields['target_steps'].widget.attrs['disabled'] = 'disabled'


class ProblemProofForm(forms.ModelForm):
    class Meta:
        model = Proof
        fields = ['rules', 'premises', 'conclusion']

    def __init__(self, *args, **kwargs):
        super(ProblemProofForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['onkeydown'] = 'replaceCharacter(this)'

    def disabled_all(self):
        self.fields['rules'].widget.attrs['read-only'] = True
        self.fields['premises'].widget.attrs['read-only'] = True
        self.fields['conclusion'].widget.attrs['read-only'] = True

class StudentProblemProofForm(ProblemProofForm):
    def __init__(self, *args, **kwargs):
        super(StudentProblemProofForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        # if instance and instance.id:
        #     self.fields['rules'].widget.attrs['disabled'] = 'disabled'
        #     self.fields['premises'].widget.attrs['disabled'] = 'disabled'
        #     self.fields['conclusion'].widget.attrs['disabled'] = 'disabled'
