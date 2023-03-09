from django import forms
from django.forms import Textarea

from .models import Proof, ProofLine, Feedback


class ProofForm(forms.ModelForm):
    class Meta:
        model = Proof
        fields = ['name', 'rules', 'premises', 'conclusion','disproof_string', 'lemmas_allowed']

    def __init__(self, *args, **kwargs):
        super(ProofForm, self).__init__(*args, **kwargs)
        self.fields['disproof_string'].required = False
        for visible in self.visible_fields():
            visible.field.widget.attrs['onkeyup'] = 'replaceCharacter(this)'


class ProofCheckerForm(forms.ModelForm):
    class Meta:
        model = ProofLine
        fields = ['line_no', 'formula', 'rule']

    def __init__(self, *args, **kwargs):
        super(ProofCheckerForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['onkeyup'] = 'replaceCharacter(this)'


class ProofLineForm(forms.ModelForm):
    class Meta:
        model = ProofLine
        fields = ['ORDER', 'line_no', 'formula', 'rule', 'comment', 'response']
        widgets = {
            'comment': Textarea(attrs={
                'style': 'width: 100%; height: 45px; padding: 8px 8px;box-sizing: border-box;border: 2px solid #ccc; border-radius: 4px; background-color: #E6D17F;',
                'placeholder': 'Instructor comment here'
                 }),
            'response': Textarea(attrs={
                'style': 'width: 100%; height: 45px; padding: 8px 8px;box-sizing: border-box;border: 2px solid #ccc; border-radius: 4px; background-color: #7BC4FF;',
                'placeholder': 'Student response here'
                })
        }

    def __init__(self, *args, **kwargs):
        super(ProofLineForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['onkeyup'] = 'replaceCharacter(this)'


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'subject', 'details', 'attach']
        widgets = {
            'attach': forms.FileInput(attrs={'multiple': ''}),
        }

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
