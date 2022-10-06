from django import forms

from proofchecker.models import Course, Instructor, Student


class CourseCreateForm(forms.ModelForm):
    
    def disabled_all(self):
        self.fields['title'].widget.attrs['disabled'] = True
        self.fields['term'].widget.attrs['disabled'] = True
        self.fields['section'].widget.attrs['disabled'] = True
    class Meta:
        model = Course
        fields = ['title', 'term', 'section']
