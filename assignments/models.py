from django.db import models
# Create your models here.


STATUS = (
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
)

class AssignmentDelay(models.Model):
    assignment = models.ForeignKey("proofchecker.assignment", on_delete=models.CASCADE)
    student  = models.ForeignKey("proofchecker.student", on_delete=models.CASCADE)
    due_date = models.DateTimeField(null=True, blank=True)
    submission_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=150, default='pending')

    def __str__(self) -> str:
        return "%s, %s, %s" %(self.assignment, self.student, self.status)