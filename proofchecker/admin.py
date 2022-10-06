from django.contrib import admin
from django.utils.html import format_html

from .models import User, Proof, Problem, Student, Instructor, Assignment, Course, ProofLine, \
    StudentProblemSolution

# Register your models here.
admin.site.register(User)
admin.site.register(Problem)
admin.site.register(Student)
admin.site.register(Instructor)
admin.site.register(Assignment)
admin.site.register(Course)
admin.site.register(StudentProblemSolution)


class ProofLineInline(admin.TabularInline):
    model = ProofLine
    extra = 0
    ordering = ("ORDER",)


@admin.register(Proof)
class ProofAdmin(admin.ModelAdmin):
    list_display = ("created_by_user", "proof_title", "view_proof_in_application")
    list_filter = ["created_by"]

    inlines = [
        ProofLineInline,
    ]

    def created_by_user(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>',
                           "/admin/proofchecker/user/" + str(obj.created_by.pk) + "/change/", obj.created_by.username)

    created_by_user.short_description = "Created By"

    def proof_title(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>',
                           "/admin/proofchecker/proof/" + str(obj.id) + "/change/",
                           obj.name)

    def view_proof_in_application(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', "/proofs/" + str(obj.id),
                           obj.name)
